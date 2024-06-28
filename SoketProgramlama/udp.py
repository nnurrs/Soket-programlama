import socket
import threading
import sys

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def receive():
    while True:
        try:
            msg, _ = client.recvfrom(1024)
            msg_decode = msg.decode('utf-8')
            if "zaten kullanımda" in msg_decode:
                print(msg_decode)
                global ad
                ad = input("kullanıcı adı: ")
                client.sendto(f"{ad} [UDP] ile bağlanmıştır hoşgeldiniz".encode('utf-8'), ("localhost", 12346))
            elif "[UDP]" in msg_decode:
                print(msg_decode)
            else:
                print(msg_decode)
        except:
            pass

ad = input("kullanıcı adı: ")

t = threading.Thread(target=receive)
t.start()

client.sendto(f"{ad} [UDP] ile bağlanmıştır hoşgeldiniz".encode('utf-8'), ("localhost", 12346))

while True:
    msg = input("")
    if msg == "görüşürüz":
        client.sendto(f"{ad} çıkış yaptı".encode('utf-8'), ("localhost", 12346))
        client.sendto(f"[UDP] {ad}: görüşürüz.".encode('utf-8'), ("localhost", 12346))
        client.sendto(f'[UDP] {ad}: sohbet odasından ayrıldı.'.encode('utf-8'), ("localhost", 12346))
        print(f"[UDP] {ad}: görüşürüz.")
        print(f"[UDP] {ad}: sohbet odasından ayrıldı.")
        sys.exit()
    else:
        client.sendto(f"[UDP] {ad}: {msg}".encode('utf-8'), ("localhost", 12346))
        print(f"[UDP] {ad}: {msg}")  # Gönderilen mesajı kendi ekranına da yazdır
