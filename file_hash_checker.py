from builtins import input
import hashlib

filename = input("Enter the filename: ")

try:
    with open(filename, "rb") as file:
        data = file.read()

    file_hash = hashlib.sha256(data).hexdigest()

    print("\nSHA-256 hash:")
    print(file_hash)

except FileNotFoundError:
    print("File not found.")