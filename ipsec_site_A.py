import os
import struct
import fcntl
import socket
import threading


class IpsecSiteAServer:
    def __init__(self, tunnel_interface_name, destination_address):
        self.destination_address = destination_address
        self.tunnel_interface_name = tunnel_interface_name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.tunnel_fd = self._initiate_tunnel_fd

    # def _initiate_tunnel_fd(self):
    #     TTUNSETIFF = 0x400454ca
    #     IFF_TUN = 0x0001
    #     IFF_TAP = 0x0002
    #     IFF_NO_PI = 0x1000
    #
    #     # Open TUN device file.
    #     tun = os.open('/dev/net/tun', os.O_RDWR)
    #
    #     ifr = struct.pack('16sH', self.tunnel_interface_name, IFF_TUN | IFF_NO_PI)
    #     ifs = fcntl.ioctl(tun, TTUNSETIFF, ifr)
    #
    #     return tun

    def send_encrypted_packets(self, tun):

        packet = os.read(tun, 1024)
        self.sock.sendto(packet, ("12.0.0.4", 40000))

    def start_tunnel_producer(self):
        TTUNSETIFF = 0x400454ca
        IFF_TUN = 0x0001
        IFF_TAP = 0x0002
        IFF_NO_PI = 0x1000

        # Open TUN device file.
        tun = os.open('/dev/net/tun', os.O_RDWR)

        ifr = struct.pack('16sH', self.tunnel_interface_name.encode(), IFF_TUN | IFF_NO_PI)
        ifs = fcntl.ioctl(tun, TTUNSETIFF, ifr)

        # t = threading.Thread(target=self.send_encrypted_packets, args=())
        try:
            # t.start()
            while True:
                response = input("Enter response to send to client: ")
                os.write(tun, response.encode())
                self.send_encrypted_packets(tun=tun)
        except KeyboardInterrupt:
            print("Terminating ...")
            os._exit(0)


if __name__ == '__main__':
    ipsec_site_a = IpsecSiteAServer(tunnel_interface_name="asa0",
                                    destination_address="10.0.1.2")

    ipsec_site_a.start_tunnel_producer()
