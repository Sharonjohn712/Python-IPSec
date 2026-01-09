import socket


while True:
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Define the UDP server address (Machine B's address)
    server_address = ('11.0.0.4', 0)
    # Data to send
    response = input("Enter response to send to client: ")

    sock.sendto(response.encode(), server_address)

    print(f"Data sent to Machine B: {response}")
