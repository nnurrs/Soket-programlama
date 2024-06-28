import socket
import threading
import sys

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 12345))

def receive():
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if "zaten alınmış" in msg:
                print(msg)
                global ad
                ad = input("kullanıcı adı: ")
                client.send(f"{ad}".encode('utf-8'))
                t = threading.Thread(target=receive)
                t.start()
            elif "[TCP]" in msg:
                print(msg)
            else:
                print(msg)
        except:
            pass

ad = input("kullanıcı adı: ")

t = threading.Thread(target=receive)
t.start()

client.send(f"{ad}".encode('utf-8'))

while True:
    msg = input("")
    if msg == "görüşürüz":
        client.send(f"[TCP] {ad}: görüşürüz".encode('utf-8'))
        client.send(f'[TCP] {ad} sohbet odasından ayrıldı.'.encode('utf-8'))
        sys.exit()
    else:
        client.send(f"[TCP] {ad}: {msg}".encode('utf-8'))
