import pytun
import socket
import time
import struct
import gzip
import zlib
import argparse
# CUSTOM IMPORTS
from imports.headers import IPHeader, ESPHeader, unpack_ipv4
from imports.aes2 import AESCipher


def user_args():
    parser = argparse.ArgumentParser(allow_abbrev=False, description="Tunnel")

    parser.add_argument("--enable-gzip-compression", type=str, default="false", help="Set to True if Gzip Compression is required")
    parser.add_argument("--enable-zlib-compression", type=str, default="false",
                        help="Set to True if ZLIB Compression is required")
    parser.add_argument("--file-name", type=str,
                        help="Specify file name")

    args = parser.parse_args()

    return args


args = user_args()

# Create a TUN interface
tun = pytun.TunTapDevice(flags=pytun.IFF_TUN | pytun.IFF_NO_PI, name='tun30')
tun.addr = '10.0.10.1'  # IP address for Machine A's TUN interface
tun.dstaddr = '10.0.10.2'  # IP address of Machine B's TUN interface
tun.netmask = '255.255.255.0'
tun.persist(True)
tun.up()

# for i in range(5000):
while True:
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Define the UDP server address (Machine B's address)
    server_address = ('12.0.0.4', 4444)
    # Data to send
    # response = input("Enter response to send to client: ")
    with open(args.file_name, "r") as data_file:
        response = data_file.readlines()
    cipher = AESCipher(256)
    ip_h = IPHeader('11.0.0.4', '12.0.0.4')
    encrypted_packet = cipher.encrypt(str(response))
    esp_h = ESPHeader(encrypted_packet)

    esp_packet = esp_h.payload
    if args.enable_gzip_compression == 'true':
        print("Enabled gzip compression")
        esp_packet = gzip.compress(esp_h.payload)
    elif args.enable_zlib_compression == 'true':
        print("Enabled zlip compression")
        esp_packet = zlib.compress(esp_h.payload)

    timestamp = time.time_ns()
    print(timestamp)
    # Convert timestamp to network byte order (big-endian)
    timestamp_bytes = struct.pack('!Q', timestamp)
    udp_header = struct.pack('!HHHH', 4444, 4444, 8, 0)
    packet = (ip_h.header + udp_header + timestamp_bytes + esp_packet)

    sock.sendto(packet, server_address)

    print(f"Data sent to Machine B: {response}")

    # Write data to the TUN interface
    tun.write(packet)
