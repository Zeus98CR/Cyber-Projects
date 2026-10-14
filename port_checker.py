import socket

host = "127.0.0.1"

ports = [21, 22, 23, 25, 53, 80, 443, 8080]

print("Checking your own computing device...")
print()

for port in ports:

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)

    result = sock.connect_ex((host, port))

    if result == 0:
        print("Port", port, "is OPEN")
    else:
        print("Port", port, "is closed")

    sock.close()