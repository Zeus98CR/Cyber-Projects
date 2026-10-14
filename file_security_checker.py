import os

folder = input("Enter folder path: ")

suspicious_extensions = [
    ".exe",
    ".bat",
    ".cmd",
    ".scr",
    ".vbs",
    ".ps1",
    ".js",
    ".jse",
    ".vbe",
    ".wsf",
    ".wsh",
    ".hta",
    ".msi",
    ".com",
    ".lnk",
    ".reg",
    ".dll",
    ".cpl",
    ".jar",
    ".chm"
]

try:
    files = os.listdir(folder)

    print("\nChecking files...\n")

    for file in files:

        filename = file.lower()

        for extension in suspicious_extensions:

            if filename.endswith(extension):
                print("Potentially suspicious:", file)

except FileNotFoundError:
    print("Folder not found.")