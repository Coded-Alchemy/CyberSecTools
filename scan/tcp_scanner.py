# This script performs a TCP full connect scan to identify open ports on a target host.

import optparse
import socket
from socket import setdefaulttimeout
from threading import Semaphore, Thread

# Create a semaphore for controlling access to the console output
screenLock = Semaphore(value=1)


def connect_scan(target_host, target_port):
    """
    Attempts to connect to a specified port on the target host.

    Args:
        target_host (str): The target host's IP address or hostname.
        target_port (int): The target port to scan.

    Returns:
        None
    """
    try:
        # Create a TCP socket
        connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection_socket.settimeout(1)  # Set a timeout for the connection

        # Attempt to connect to the target host and port
        connection_socket.connect((target_host, target_port))

        # Send an empty byte string to avoid errors
        connection_socket.send(b'')
        results = connection_socket.recv(100)

        # Acquire the lock to safely print to the console
        screenLock.acquire()
        print(f'[+] {target_port}/tcp open')
        print(f'[+] {results.decode("utf-8")}')

    except (socket.timeout, ConnectionRefusedError):
        # If the connection is refused or times out, the port is closed
        screenLock.acquire()
        print(f'[-] {target_port}/tcp closed')
    except Exception as exception:
        # Catch any other exceptions
        screenLock.acquire()
        print(f'[-] Error scanning {target_port}/tcp: {str(exception)}')
    finally:
        # Always close the socket
        screenLock.release()
        connection_socket.close()


def port_scan(target_host, target_ports):
    """
    Scans a list of ports on a specified target host.

    Args:
        target_host (str): The target host's IP address or hostname.
        target_ports (list): A list of ports to scan.

    Returns:
        None
    """
    try:
        target_ip = socket.gethostbyname(target_host)
    except socket.gaierror:
        print(f"[-] Cannot resolve '{target_host}': Unknown host")
        return

    try:
        target_name = socket.gethostbyaddr(target_ip)
        print(f'\nScan Results for: {target_name[0]}\n')
    except socket.herror:
        print(f'\nScan Results for: {target_ip}\n')

    setdefaulttimeout(1)  # Set default timeout for all socket operations
    for port in target_ports:
        thread = Thread(target=connect_scan, args=(target_host, int(port)))
        thread.start()


def run():
    """
    Parses command-line arguments and initiates the port scan.

    Returns:
        None
    """
    parser = optparse.OptionParser("usage: %prog -H <target host> -p <target port>")
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-p', dest='tgtPort', type='string', help='specify target port[s] separated by comma')

    (options, args) = parser.parse_args()

    target_host = options.tgtHost
    if options.tgtPort:
        target_ports = options.tgtPort.split(',')
    else:
        target_ports = []

    if target_host is None or not target_ports:
        print('[-] You must specify a target host and port[s].')
        exit(0)

    port_scan(target_host, target_ports)


# Execute the script from the terminal like this:
# python3 your_script_name.py -H target_host -p port1,port2,port3
if __name__ == '__main__':
    run()
