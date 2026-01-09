# Simple linux tun/tap device example tunnel over udp
# create tap device with ip tuntap add device0 tap
# set ip address on it and run tap-linux on that device and set desitation ip
# run same on another node, changing dst ip to first node

import fcntl
import struct
import os
import socket
import threading
import sys

TUNSETIFF = 0x400454ca
TUNSETOWNER = TUNSETIFF + 2
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000


def udp_send(dst, packet):
    print("udp_send")
    sock.sendto(packet, (dst, 40000))


def recv():
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.bind(("12.0.0.4", 40000))
    while True:
        data, addr = ss.recvfrom(1024)
        print("udp_recv")
        print(data)
        os.write(tun, data)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: tap-linux.py <tap_interface> <dst_address_of_tunnel>")
        sys.exit(1)
    iface = sys.argv[1]
    dst = sys.argv[2]
    print("Working on %s inteface, destination address %s:40000 udp" % (iface, dst))
    tun = os.open('/dev/net/tun', os.O_RDWR)
    # ifr = struct.pack('16sH', iface.encode(), IFF_TAP | IFF_NO_PI)
    ifr = struct.pack('16sH', iface.encode(), IFF_TUN | IFF_NO_PI)
    ifs = fcntl.ioctl(tun, TUNSETIFF, ifr)
    print(ifs)
    # fcntl.ioctl(tun, TUNSETOWNER, 1000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    t = threading.Thread(target=recv)
    try:
        t.start()
        while True:
            packet = os.read(tun, 2048)
            if not packet:
                break
            print(f"Received from client: {packet}")

            if True:
                response = input("Enter response to send to client: ")
                udp_send(dst, response.encode())

    except KeyboardInterrupt:
        print("Terminating ...")
        os._exit(0)
