import threading
import socket
import os
import argparse
import netifaces
import struct
import fcntl
import sys
import time

# CUSTOM IMPORTS
from imports.headers import IPHeader, ESPHeader, unpack_ipv4
from imports.aes import AESCipher


class SiteSocket:
    def __init__(self, interface_name: str, dst_ip, tunnel_interface_name: str):
        self.destination_ip = dst_ip
        self.tunnel_interface_name = tunnel_interface_name
        self.interface_name = interface_name
        self.physical_interface_ip = netifaces.ifaddresses(self.interface_name)[2][0]['addr']

    def _initiate_tunnel_fd(self):
        # CONSTANTS
        TUNSETIFF = 0x400454ca
        IFF_TUN = 0x0001
        IFF_TAP = 0x0002
        IFF_NO_PI = 0x1000

        # Open TUN device file.
        tunnel_fd = os.open('/dev/net/tun', os.O_RDWR)
        print(tunnel_fd)
        ifr = struct.pack('16sH', self.tunnel_interface_name.encode(), IFF_TUN | IFF_NO_PI)
        ifs = fcntl.ioctl(tunnel_fd, TUNSETIFF, ifr)
        print(ifs)
        return tunnel_fd

    def _sender_receiver_sockets(self):
        # Create a RAW Socket to send the traffic
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # sender_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        # sender_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sender_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        print(self.interface_name)
        # Raw socket to recv the traffic
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver_socket.bind((self.physical_interface_ip, 0))

        return sender_socket, receiver_socket

    def send_data(self, sender_socket, tunnel_fd):
        # ip_header = IPHeader(self.physical_interface_ip, self.destination_ip)  # create an IP header
        # packet_from_fd = os.read(tunnel_fd, 1024)  # read the file descriptor for packets

        message = input("Enter your message (Type 'bye' to exit): ")
        while message.lower().strip() != "bye":
            print("Writing to tunnel")
            os.write(tunnel_fd, message.encode())
            # packet_from_tunnel = os.read(tunnel_fd, 1024)

            sender_socket.sendto(message.encode(), (self.destination_ip, 0))

    def receive_data(self, receiver_socket, tunnel_fd):
        packet_from_socket = receiver_socket.recv(1024)

        while True:
            if not packet_from_socket:
                break
            try:
                print(packet_from_socket)
                os.write(tunnel_fd, packet_from_socket)
                packet_from_socket = receiver_socket.recv(1024)

            except Exception as e:
                print(e)

    def main(self):
        tunnel_fd = self._initiate_tunnel_fd()
        sender_socket, receiver_socket = self._sender_receiver_sockets()


        if args.system == "server":
            # self.receive_data(receiver_socket, tunnel_fd)

            # server_daemon = threading.Thread(target=self.receive_data, args=(receiver_socket, tunnel_fd))
            # server_daemon.setDaemon(True)
            # server_daemon.start()
            print("Tunnel is open and running...")
            self.receive_data(receiver_socket, tunnel_fd)

            # while True:
            #     try:
            #         for _ in range(10):
            #             time.sleep(0.2)
            #     except KeyboardInterrupt:
            #         sys.exit(1)

        else:
            print("Starting tunnel client...")
            self.send_data(sender_socket, tunnel_fd)
            # client_daemon = threading.Thread(target=self.send_data, args=(sender_socket,
            #                                                               tunnel_fd))
            # client_daemon.setDaemon(True)
            # client_daemon.start()
            # print("Tunnel is open and running...")
            # while True:
            #     try:
            #         for _ in range(10):
            #             time.sleep(0.2)
            #     except KeyboardInterrupt:
            #         sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--eth-interface", help="Physical interface to bind to")
    parser.add_argument('--destination-ip', '-dstip', action='store', type=str, help="Destination IP of the Tunnel",
                        required=True)
    parser.add_argument('--encrypt-key', '-key', action='store', type=str, help="Encryption key used for connection",
                        required=True)
    parser.add_argument('--tunnel-interface-name', '-tunint', action='store', type=str,
                        help="TUN tunnel interface name", required=True)
    parser.add_argument('--system', action='store', type=str,
                        help="Provide whether to start the server/client", required=True)
    args = parser.parse_args()

    SiteSocket(interface_name=args.eth_interface,
               dst_ip=args.destination_ip,
               tunnel_interface_name=args.tunnel_interface_name).main()
