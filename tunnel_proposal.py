from py_ipsec import IPsec, Policy, Peer, Proposal

# Define IPsec parameters
local_addr = '192.168.1.1'  # Local machine's public IP address
remote_addr = '192.168.2.1'  # Remote machine's public IP address
local_subnet = '10.1.0.0/24'  # Local subnet behind this machine
remote_subnet = '10.2.0.0/24'  # Remote subnet behind the other machine
shared_secret = 'mysecretpassword'  # Pre-shared key for authentication

# Configure IPsec Proposal
proposal = Proposal(
    encryption_algorithm='aes',
    encryption_key_size=128,
    integrity_algorithm='sha1',
    dh_group=2
)

# Configure IPsec Policy
policy = Policy(
    mode='tunnel',
    local_subnet=local_subnet,
    remote_subnet=remote_subnet,
    proposal=proposal
)

# Configure IPsec Peer
peer = Peer(
    address=remote_addr,
    policy=policy,
    pre_shared_key=shared_secret
)

# Create and start IPsec VPN tunnel
ipsec = IPsec(
    local_addr=local_addr,
    peers=[peer]
)

ipsec.start()

# Optionally, you can monitor the status of the IPsec connection
print("IPsec tunnel established successfully.")
print("IPsec status:")
print(ipsec.status())
