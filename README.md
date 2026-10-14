# Cyber Projects

A collection of small Python utilities and learning projects related to cybersecurity.

## Projects

- `cyber_desk_analyst.py` — parses authentication logs and reports suspicious activity.
- `file_hash_checker.py` — calculates file hashes.
- `file_security_checker.py` — performs basic file security checks.
- `login_security_testing.py` — demonstrates a local login-attempt limit.
- `morse_code_translation.py` — translates Morse code and handles audio.
- `password_strength_tester.py` — gives basic password-strength feedback.
- `port_checker.py` — checks TCP ports on `127.0.0.1` by default.

## Getting started

The scripts use Python's standard library. Use Python 3.10 or newer, then run a
script from this folder, for example:

```powershell
python .\cyber_desk_analyst.py .\auth.log
python .\password_strength_tester.py
```

Run `python .\<script-name>.py --help` for command-line options where supported.

`login_security_testing.py` is an educational demo, not production
authentication. It asks you to set temporary test credentials when run.

## Responsible use

These projects are for learning and authorized testing only. Only inspect files
and systems you own or have explicit permission to test. The port checker
defaults to the local machine; do not use it against systems without permission.
