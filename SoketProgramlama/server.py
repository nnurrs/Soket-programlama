import threading
import socket

host = '127.0.0.1'
portTCP = 12345
portUDP = 12346

# TCP server 
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.bind((host, portTCP))
tcp_server.listen()

clients = []
tcp_kullaniciAdlari = []

# UDP server
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind((host, portUDP))

udp_clients = []
udp_kullaniciAdlari = {}

global user_counter
user_counter = 0

def get_variable():
    return user_counter

def broadcast_tcp(msg):  # TCP üzerinden yayın fonksiyonu
    print(msg.decode('utf-8'))
    for client in clients:
        client.send(msg)

def handle_tcp(client):  # TCP üzerinden bağlantıları yönetme fonksiyonu
    while True:
        try:
            msg = client.recv(1024)
            if not msg:
                break
            if msg.decode('utf-8').strip().lower() == "görüşürüz":
                index = clients.index(client)
                kullaniciAdi = tcp_kullaniciAdlari[index]
                clients.remove(client)
                client.close()
                broadcast_tcp(f'{kullaniciAdi} [TCP] ({user_counter}) sohbet odasından ayrıldı.'.encode('utf-8'))
                tcp_kullaniciAdlari.remove(kullaniciAdi)
                break
            broadcast_tcp(f'{msg.decode("utf-8")}'.encode('utf-8'))
            broadcast_udp(f'{msg.decode("utf-8")}'.encode('utf-8'))
        except Exception as e:
            print(f"Hata: {e}")
            break

def receive_tcp():
    global user_counter  # Declare user_counter as global

    while True:
        client, adr = tcp_server.accept()

        kullaniciAdi = client.recv(1024).decode('utf-8')
        tcp_kullaniciAdlari.append(kullaniciAdi)
        clients.append(client)

        user_counter += 1  # Increment user_counter
        broadcast_tcp(f'{kullaniciAdi} [TCP] ({user_counter}) ile bağlanmıştır hoşgeldiniz'.encode('utf-8'))
        client.send(f"Hoşgeldiniz {kullaniciAdi} [TCP] ({user_counter}) ile bağlısınız".encode('utf-8'))

        thread = threading.Thread(target=handle_tcp, args=(client,))
        thread.start()

msgs = []
udp_lock = threading.Lock()

def receive_udp():
    while True:
        try:
            msg, addr = udp_server.recvfrom(1024)
            with udp_lock:
                msgs.append((msg, addr))
        except Exception as e:
            print(f"Hata: {e}")
            pass

def broadcast_udp(msg):
    with udp_lock:
        for client in udp_clients:
            try:
                udp_server.sendto(msg, client)
            except Exception as e:
                print(f"Hata: {e}")
                udp_clients.remove(client)

def broadcast_udp_loop():
    global user_counter  # Declare user_counter as global

    while True:
        with udp_lock:
            while msgs:
                msg, addr = msgs.pop(0)
                msg_decode = msg.decode('utf-8')
                kullaniciAd = msg_decode.split()[0]

                if addr not in udp_clients:
                    udp_clients.append(addr)

                user_counter += 1
                if "[UDP] ile bağlanmıştır hoşgeldiniz" in msg_decode:
                    udp_kullaniciAdlari[addr] = (kullaniciAd, user_counter)
                    for client in udp_clients:
                        if client != addr:
                            try:
                                udp_server.sendto(f"Hoşgeldiniz {kullaniciAd} [UDP] ({user_counter}) ile bağlısınız".encode('utf-8'), client)
                            except Exception as e:
                                print(f"Hata: {e}")
                                udp_clients.remove(client)
                    udp_server.sendto(f"Hoşgeldiniz {kullaniciAd} [UDP] ({user_counter}) ile bağlısınız".encode('utf-8'), addr)

                elif "çıkış yaptı" in msg_decode:
                    udp_clients.remove(addr)
                    if addr in udp_kullaniciAdlari:
                        del udp_kullaniciAdlari[addr]
                    for client in udp_clients:
                        try:
                            udp_server.sendto(f"{kullaniciAd} [UDP] ({user_counter}) {msg_decode}".encode('utf-8'), client)
                        except Exception as e:
                            print(f"Hata: {e}")
                            udp_clients.remove(client)
                else:
                    for client in udp_clients:
                        if client != addr:
                            try:
                                udp_server.sendto(f"{kullaniciAd} [UDP] ({user_counter}) ({udp_kullaniciAdlari[addr][1]}) {msg_decode}".encode('utf-8'), client)
                            except Exception as e:
                                print(f"Hata: {e}")
                                udp_clients.remove(client)
                broadcast_tcp(msg)

tcp_thread = threading.Thread(target=receive_tcp)
udp_receive_thread = threading.Thread(target=receive_udp)
udp_broadcast_thread = threading.Thread(target=broadcast_udp_loop)

tcp_thread.start()
udp_receive_thread.start()
udp_broadcast_thread.start()

print("Server dinliyor...")
