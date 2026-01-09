import os
# Buffer size for receiving data
buffer_size = 1024

while True:
    tun = os.open('/dev/net/tun', os.O_RDWR)
    packet = os.read(tun, buffer_size)

    # Process the received packet
    print(f"Received packet: {packet}")

    # Example: Processing IPv4 packet
    if len(packet) >= 20:  # Minimum IPv4 header length is 20 bytes
        # Extract IP header information
        ip_header = packet[:20]
        src_ip = '.'.join(map(str, ip_header[12:16]))
        dst_ip = '.'.join(map(str, ip_header[16:20]))
        print(f"Source IP: {src_ip}, Destination IP: {dst_ip}")

        # Process or forward the packet as needed
        # Example: Print payload (after IP header)
        payload = packet[20:]
        print(f"Payload: {payload}")

    else:
        print(f"Received unrecognized packet: {packet}")