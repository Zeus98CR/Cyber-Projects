import re
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

FAILURE_THRESHOLD = 5
ACCOUNT_THRESHOLD = 3
TIME_WINDOW_MINUTES = 10

# ============================================================
# LOG PARSER
# ============================================================

# Example log:
#
# 2026-08-19 08:12:31 FAILED_LOGIN user=admin ip=192.168.1.50
#
# 2026-08-19 08:13:02 SUCCESS_LOGIN user=alice ip=192.168.1.20

LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2})\s+"
    r"(?P<event>\w+)\s+"
    r"user=(?P<user>\S+)\s+"
    r"ip=(?P<ip>\S+)"
)

def parse_line(line):
    """
    Parse one log line.

    Returns a dictionary or None if the line is invalid.
    """

    match = LOG_PATTERN.search(line)

    if not match:
        return None

    data = match.groupdict()

    data["timestamp"] = datetime.strptime(
        data["timestamp"],
        "%Y-%m-%d %H:%M:%S"
    )

    return data


def load_logs(filename):
    """
    Load and parse a log file.
    """

    events = []
    invalid_lines = 0

    with open(filename, "r", encoding="utf-8") as file:

        for line in file:

            event = parse_line(line)

            if event:
                events.append(event)
            else:
                invalid_lines += 1

    return events, invalid_lines


# ============================================================
# BASIC STATISTICS
# ============================================================

def calculate_statistics(events):

    total = len(events)

    event_types = Counter(
        event["event"]
        for event in events
    )

    users = Counter(
        event["user"]
        for event in events
    )

    ips = Counter(
        event["ip"]
        for event in events
    )

    failed_logins = [
        event for event in events
        if event["event"] == "FAILED_LOGIN"
    ]

    successful_logins = [
        event for event in events
        if event["event"] == "SUCCESS_LOGIN"
    ]

    return {
        "total_events": total,
        "event_types": dict(event_types),
        "unique_users": len(users),
        "unique_ips": len(ips),
        "failed_logins": len(failed_logins),
        "successful_logins": len(successful_logins),
    }


# ============================================================
# BRUTE FORCE DETECTION
# ============================================================

def detect_brute_force(events):

    failures_by_ip = defaultdict(list)

    for event in events:

        if event["event"] == "FAILED_LOGIN":

            failures_by_ip[event["ip"]].append(event)

    findings = []

    for ip, failures in failures_by_ip.items():

        failures.sort(
            key=lambda x: x["timestamp"]
        )

        for i in range(len(failures)):

            window_start = failures[i]["timestamp"]

            window_end = (
                window_start
                + __import__("datetime").timedelta(
                    minutes=TIME_WINDOW_MINUTES
                )
            )

            window_events = [
                event
                for event in failures[i:]
                if event["timestamp"] <= window_end
            ]

            if len(window_events) >= FAILURE_THRESHOLD:

                usernames = set(
                    event["user"]
                    for event in window_events
                )

                findings.append({
                    "type": "POSSIBLE_BRUTE_FORCE",
                    "risk": "HIGH",
                    "ip": ip,
                    "failed_attempts": len(window_events),
                    "accounts_targeted": len(usernames),
                    "accounts": sorted(usernames),
                    "reason": (
                        f"{len(window_events)} failed logins "
                        f"within {TIME_WINDOW_MINUTES} minutes"
                    )
                })

                break

    return findings


# ============================================================
# MULTI-ACCOUNT DETECTION
# ============================================================

def detect_multiple_accounts(events):

    accounts_by_ip = defaultdict(set)

    for event in events:

        if event["event"] == "FAILED_LOGIN":
            accounts_by_ip[event["ip"]].add(
                event["user"]
            )

    findings = []

    for ip, accounts in accounts_by_ip.items():

        if len(accounts) >= ACCOUNT_THRESHOLD:

            findings.append({
                "type": "MULTIPLE_ACCOUNTS_TARGETED",
                "risk": "MEDIUM",
                "ip": ip,
                "accounts_targeted": len(accounts),
                "accounts": sorted(accounts),
                "reason": (
                    f"{ip} attempted authentication "
                    f"against {len(accounts)} accounts"
                )
            })

    return findings


# ============================================================
# UNUSUAL LOGIN TIME
# ============================================================

def detect_unusual_hours(events):

    findings = []

    for event in events:

        hour = event["timestamp"].hour

        # Example baseline:
        # consider 00:00-05:59 unusual.
        if event["event"] == "SUCCESS_LOGIN" and (
            hour < 6
        ):

            findings.append({
                "type": "UNUSUAL_LOGIN_TIME",
                "risk": "MEDIUM",
                "ip": event["ip"],
                "user": event["user"],
                "timestamp": (
                    event["timestamp"].isoformat()
                ),
                "reason": (
                    "Successful login occurred "
                    "during unusual hours"
                )
            })

    return findings


# ============================================================
# RISK SCORING
# ============================================================

def calculate_score(finding):

    score = 0

    finding_type = finding["type"]

    if finding_type == "POSSIBLE_BRUTE_FORCE":
        score += 60

        if finding["failed_attempts"] >= 20:
            score += 20

    elif finding_type == "MULTIPLE_ACCOUNTS_TARGETED":
        score += 35

        if finding["accounts_targeted"] >= 10:
            score += 20

    elif finding_type == "UNUSUAL_LOGIN_TIME":
        score += 25

    return min(score, 100)


def add_scores(findings):

    for finding in findings:

        finding["score"] = calculate_score(finding)

        score = finding["score"]

        if score >= 80:
            finding["risk"] = "CRITICAL"

        elif score >= 60:
            finding["risk"] = "HIGH"

        elif score >= 30:
            finding["risk"] = "MEDIUM"

        else:
            finding["risk"] = "LOW"

    return findings


# ============================================================
# REPORTING
# ============================================================

def print_report(statistics, findings, invalid_lines):

    print()
    print("=" * 60)
    print("              AUTOMATED CYBER ANALYST")
    print("=" * 60)

    print()
    print("STATISTICS")
    print("-" * 60)

    print(
        f"Events analyzed:    "
        f"{statistics['total_events']}"
    )

    print(
        f"Unique users:       "
        f"{statistics['unique_users']}"
    )

    print(
        f"Unique IPs:          "
        f"{statistics['unique_ips']}"
    )

    print(
        f"Failed logins:      "
        f"{statistics['failed_logins']}"
    )

    print(
        f"Successful logins:  "
        f"{statistics['successful_logins']}"
    )

    print(
        f"Invalid log lines:  "
        f"{invalid_lines}"
    )

    print()
    print("EVENT TYPES")
    print("-" * 60)

    for event_type, count in (
        statistics["event_types"].items()
    ):
        print(f"{event_type:<25} {count}")

    print()
    print("SECURITY FINDINGS")
    print("-" * 60)

    if not findings:

        print("No suspicious activity detected.")

        return

    for number, finding in enumerate(
        findings,
        start=1
    ):

        print()
        print(
            f"[{number}] "
            f"{finding['risk']} "
            f"(score={finding['score']})"
        )

        print(
            f"Type: {finding['type']}"
        )

        print(
            f"Reason: {finding['reason']}"
        )

        if "ip" in finding:
            print(
                f"IP: {finding['ip']}"
            )

        if "user" in finding:
            print(
                f"User: {finding['user']}"
            )

        if "accounts" in finding:
            print(
                "Accounts: "
                + ", ".join(finding["accounts"])
            )

    print()


# ============================================================
# JSON EXPORT
# ============================================================

def save_json(
    filename,
    statistics,
    findings
):

    report = {
        "generated_at": datetime.now().isoformat(),
        "statistics": statistics,
        "findings": findings
    }

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            default=str
        )

    print(
        f"JSON report saved to: {filename}"
    )


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze(filename):

    events, invalid_lines = load_logs(
        filename
    )

    statistics = calculate_statistics(
        events
    )

    findings = []

    findings.extend(
        detect_brute_force(events)
    )

    findings.extend(
        detect_multiple_accounts(events)
    )

    findings.extend(
        detect_unusual_hours(events)
    )

    findings = add_scores(findings)

    # Remove exact duplicate findings.
    unique_findings = []
    seen = set()

    for finding in findings:

        identifier = json.dumps(
            finding,
            sort_keys=True,
            default=str
        )

        if identifier not in seen:

            seen.add(identifier)
            unique_findings.append(
                finding
            )

    return (
        statistics,
        unique_findings,
        invalid_lines
    )


# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Analyze authentication logs "
            "for suspicious activity."
        )
    )

    parser.add_argument(
        "logfile",
        help="Path to the log file"
    )

    parser.add_argument(
        "--json",
        default="cyber_report.json",
        help="Output JSON report"
    )

    args = parser.parse_args()

    try:

        statistics, findings, invalid = analyze(
            args.logfile
        )

        print_report(
            statistics,
            findings,
            invalid
        )

        save_json(
            args.json,
            statistics,
            findings
        )

    except FileNotFoundError:

        print(
            f"Error: file not found: "
            f"{args.logfile}"
        )

    except PermissionError:

        print(
            "Error: permission denied."
        )

    except Exception as error:

        print(
            f"Unexpected error: {error}"
        )


if __name__ == "__main__":
    main()