import getpass
import hashlib

# Demo only: this is not suitable for production authentication.
correct_username = input("Set a test username: ")
correct_password_hash = hashlib.sha256(
    getpass.getpass("Set a test password: ").encode()
).hexdigest()

attempts = 0
max_attempts = 3
locked_users = set()

username = input("Username: ")

if username in locked_users:
    print("Account is locked. Please contact support.")
else:
    while attempts < max_attempts:
        password = getpass.getpass("Password: ")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if username == correct_username and password_hash == correct_password_hash:
            print("\n✓ Login successful!")
            break
        else:
            attempts += 1
            remaining = max_attempts - attempts
            print(f"✗ Incorrect username or password.")
            print(f"Attempts remaining: {remaining}\n")

    if attempts == max_attempts:
        locked_users.add(username)
        print("✗ Account locked due to too many failed attempts.")