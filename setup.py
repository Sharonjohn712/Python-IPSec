from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ipsec-tunnel",
    version="1.0.0",
    author="Jadhusan",
    author_email="your.email@example.com",
    description="A Python implementation of an IPsec-like tunnel for secure communication between hosts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jadhusan24/Python-IPsecTunnel",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Networking",
        "Topic :: Security",
    ],
    python_requires='>=3.8',
    install_requires=[
        'pycryptodome',
        'netifaces',
        'python-pytun',
    ],
    entry_points={
        'console_scripts': [
            'ipsec-tunnel=ipsec_tunnel.main:main',
        ],
    },
)
