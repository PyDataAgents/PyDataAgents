import socket
import threading
import time
import random

HOST = "0.0.0.0"   # Listen on all interfaces
PORT = 5000        # Change if needed

def handle_client(conn, addr):
    print(f"[+] New connection from {addr}")
    with conn:
        conn.sendall(b"Welcome to Test TCP Server\r\n")
        conn.sendall(b"Type commands: GET TEMP | GET STATUS | GET TIME | EXIT\r\n")

        while True:
            data = conn.recv(1024)
            if not data:
                break

            cmd = data.decode("utf-8").strip().upper()
            print(f"Received command: {cmd}")

            if cmd == "GET TEMP":
                response = f"TEMP={round(random.uniform(20.0, 30.0), 2)}C\r\n"
            elif cmd == "GET STATUS":
                response = "STATUS=OK\r\n"
            elif cmd == "GET TIME":
                response = f"TIME={time.strftime('%Y-%m-%d %H:%M:%S')}\r\n"
            elif cmd == "EXIT":
                response = "BYE\r\n"
                conn.sendall(response.encode())
                break
            else:
                response = "ERR=UNKNOWN COMMAND\r\n"

            conn.sendall(response.encode())

    print(f"[-] Connection from {addr} closed.")

def main():
    print(f"Starting TCP server on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Waiting for connections...")

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()

if __name__ == "__main__":
    main()