import pytun
import threading
import socket
import os
import argparse
import netifaces
import struct
import fcntl
import sys
import gzip
import time
import zlib

from imports.headers import IPHeader, ESPHeader, unpack_ipv4
from imports.aes2 import AESCipher

def user_args():
    parser = argparse.ArgumentParser(allow_abbrev=False, description="Tunnel")

    parser.add_argument("--enable-gzip-decompression", type=str, default="false", help="Set to True if Gzip DeCompression is required")
    parser.add_argument("--enable-zlib-decompression", type=str, default="false",
                        help="Set to True if Zlib DeCompression is required")
    args = parser.parse_args()

    return args

args = user_args()

# Create a TUN interface
tun = pytun.TunTapDevice(flags=pytun.IFF_TUN | pytun.IFF_NO_PI, name='tun30')
tun.addr = '10.0.10.2'  # IP address for Machine B's TUN interface
tun.dstaddr = '10.0.10.1'  # IP address of Machine A's TUN interface
tun.netmask = '255.255.255.0'
tun.persist(True)
tun.up()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('12.0.0.4', 4444)
sock.bind(server_address)

# Buffer size for receiving data
buffer_size = 900000
with open("timerecorder.txt", "w") as time_rd:
    while True:
        data, address = sock.recvfrom(buffer_size)
        print(f"Received data from {address}: {data}")
        # tun.write(data)
        #
        # # Read data from the TUN interface
        # received_data = tun.read(buffer_size)
        #
        # print(f"Received data from Machine A: {received_data}")
        #
        # ip_header = received_data[:20]
        # iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
        # print(iph)
        # version_ihl = iph[0]
        # version = version_ihl >> 4
        # ihl = version_ihl & 0xF
        # ttl = iph[5]
        # protocol = iph[6]
        # src_ip = socket.inet_ntoa(iph[8])
        # dst_ip = socket.inet_ntoa(iph[9])
        #
        # print(f"Received IPv4 packet - Source IP: {src_ip}, Destination IP: {dst_ip}")
        #
        # payload = received_data[20:]  # Extract payload (after IP header)
        # print(f"Payload: {payload}")
        #
        # payload_str = payload.decode('utf-8', 'ignore')
        # print(f"Payload (decoded): {payload_str}")

        src, dst, protocol = unpack_ipv4(data)

        print(src, dst, protocol)
        cipher = AESCipher(256)

        if protocol == 50:
            print(src)
            print(dst)
            print(protocol)
            print(data)
            print(data[32:])
            esp_data = data[36:]
            if args.enable_gzip_decompression == 'true':
                print("Enabling gzip decompression")
                esp_data = gzip.decompress(data[36:])
            if args.enable_zlib_decompression == 'true':
                print("Enabling zlib decompression")
                esp_data = zlib.decompress(data[36:])
            decrypted_packet = cipher.decrypt(esp_data)  # decrypt the packet
            # write to file descriptor, so it can be read and sent
            print(decrypted_packet.encode())

            end_time = time.time_ns()

            ip_header_time = data[:20]  # Assuming fixed size for IPv4 header
            iph_test = struct.unpack('!BBHHHBBH4s4s', ip_header_time)
            print(iph_test)
            version_ihl = iph_test[0]
            print(version_ihl)
            ip_version = version_ihl >> 4
            print(ip_version)
            ip_header_length = version_ihl & 0xF
            print(ip_header_length)
            ip_ttl = iph_test[5]
            print(ip_ttl)
            ip_protocol = iph_test[6]
            print(ip_protocol)

            timestamp = struct.unpack('!Q', data[28:36])[0]
            print(timestamp)
            print(end_time)
            time_taken = end_time - timestamp
            seconds = time_taken / 1e9

            print(f"Current time in nanoseconds: {time_taken}")
            print(f"Current time in seconds: {seconds}")

            time_rd.write(str(seconds) + '\n')
            # ip_version = 4
            # ip_header_length = 5
            ip_total_length = 20  # IPv4 header length (20 bytes) + payload length
            # ip_ttl = 64
            # ip_protocol = 17  # UDP protocol number

            # Construct the IPv4 header
            ip_header = struct.pack('!BBHHHBBH4s4s',
                                    (ip_version << 4) + ip_header_length,  # Version and header length
                                    0,  # Type of service
                                    ip_total_length,  # Total length
                                    0,  # Identification
                                    0,  # Flags and Fragment Offset
                                    ip_ttl,  # Time to live
                                    ip_protocol,  # Protocol (UDP in this case)
                                    0,  # Header checksum (will be calculated automatically)
                                    socket.inet_aton('10.0.10.1'),  # Source IP address
                                    socket.inet_aton('10.0.10.2'))  # Destination IP address

            # Payload (e.g., UDP packet)
            # udp_src_port = 12345
            # udp_dst_port = 54321
            # udp_length = 8  # UDP header length (8 bytes) + payload length
            # udp_checksum = 0  # UDP checksum (optional for TUN interface)

            # Extract UDP header
            udp_header = data[20:28]  # Assuming fixed size for UDP header (8 bytes)

            # Unpack UDP header
            udph = struct.unpack('!HHHH', udp_header)
            print(udph)
            udp_src_port = udph[0]
            udp_dst_port = udph[1]
            udp_length = udph[2]
            udp_checksum = udph[3]

            # # Construct the UDP header
            # udp_header = struct.pack('!HHHH',
            #                          udp_src_port,  # Source port
            #                          udp_dst_port,  # Destination port
            #                          udp_length,  # Length
            #                          udp_checksum)  # Checksum (optional)

            # Construct the UDP header
            udp_header = struct.pack('!HHHH',
                                     udp_src_port,  # Source port
                                     udp_dst_port,  # Destination port
                                     udp_length,  # Length
                                     udp_checksum)  # Checksum (optional)

            # Complete IP packet (header + payload)
            packet = ip_header + udp_header + decrypted_packet.encode()

            tun.write(packet)
