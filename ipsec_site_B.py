import os
import struct
import fcntl
import socket
import threading


class IpsecSiteAServer:
    def __init__(self, tunnel_interface_name, destination_address, source_address):
        self.destination_address = destination_address
        self.tunnel_interface_name = tunnel_interface_name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.source_address = source_address

    def _initiate_tunnel_fd(self):
        TUNSETIFF = 0x400454ca
        TUNSETOWNER = TUNSETIFF + 2
        IFF_TUN = 0x0001
        IFF_TAP = 0x0002
        IFF_NO_PI = 0x1000

        tunnel_fd = os.open('/dev/net/tun', os.O_RDWR)
        ifr = struct.pack('16sH', self.tunnel_interface_name.encode(), IFF_TUN | IFF_NO_PI)
        ifs = fcntl.ioctl(tunnel_fd, TUNSETIFF, ifr)

        return tunnel_fd

    def send_encrypted_packets(self, packet_data):
        self.sock.sendto(packet_data, (self.destination_address, 40000))

    def start_tunnel_consumer(self):
        ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ss.bind(("12.0.0.4", 40000))
        tun = self._initiate_tunnel_fd()
        while True:
            print("Starting tunnel consumer")
            data, addr = ss.recvfrom(1024)
            print("udp_recv")
            print(data)
            os.write(tun, data)
    #
    # def start_tunnel_producer(self):
    #
    #     t = threading.Thread(target=self.send_encrypted_packets, args=(self.sock, self))
    #     try:
    #         t.start()
    #         while True:
    #             response = input("Enter response to send to client: ")
    #             self.send_encrypted_packets(packet_data=response.encode())
    #     except KeyboardInterrupt:
    #         print("Terminating ...")
    #         os._exit(0)


if __name__ == '__main__':
    ipsec_site_a = IpsecSiteAServer(tunnel_interface_name="asa0",
                                    destination_address="10.0.1.2",
                                    source_address="10.0.1.2")

    ipsec_site_a.start_tunnel_consumer()
