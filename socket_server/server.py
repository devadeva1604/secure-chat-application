import socket
import threading


HOST = "127.0.0.1"
PORT = 5001

clients = []


def broadcast(message, current_client):

    for client in clients:

        if client != current_client:

            try:
                client.send(message)

            except:
                clients.remove(client)


def handle_client(client):

    while True:

        try:

            message = client.recv(1024)

            if message:

                print("Message:", message.decode())

                broadcast(message, client)

            else:
                break

        except:
            break

    if client in clients:
        clients.remove(client)

    client.close()


server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.bind((HOST, PORT))

server.listen()

print("Socket Server Started")
print("Waiting for users...")


while True:

    client, address = server.accept()

    print("New user connected:", address)

    clients.append(client)

    thread = threading.Thread(
        target=handle_client,
        args=(client,)
    )

    thread.start()