import sys
import socket
import pyfiglet
from threading import Thread, Lock

# Display ASCII banner
ascii_banner = pyfiglet.figlet_format("Coded Alchemy")
print(ascii_banner)

# Thread-safe storage for open ports
open_ports = []
lock = Lock()


def probe_port(ip, port):
    """
    Probes a specific port on the given IP address.

    Parameters:
    ip (str): The target IP address.
    port (int): The port to probe.

    Returns:
    bool: True if the port is open, False otherwise.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex((ip, port)) == 0:
                with lock:
                    open_ports.append(port)
                return True
    except Exception:
        pass
    return False


def port_scanner(ip, ports):
    """
    Scans a range of ports on the given IP address using threads.

    Parameters:
    ip (str): The target IP address.
    ports (range): The range of ports to scan.
    """
    threads = []
    for port in ports:
        thread = Thread(target=probe_port, args=(ip, port))
        threads.append(thread)
        thread.start()

        # Throttle threads to prevent overwhelming the system
        if len(threads) >= 100:  # Limit to 100 concurrent threads
            for t in threads:
                t.join()
            threads = []

    # Ensure all threads have completed
    for t in threads:
        t.join()


def main():
    """
    Main function to parse arguments, run the port scanner, and display results.
    """
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <target_ip> [<start_port>-<end_port>]")
        sys.exit(1)

    ip = sys.argv[1]

    try:
        if len(sys.argv) > 2:
            port_range = sys.argv[2].split("-")
            start_port = int(port_range[0])
            end_port = int(port_range[1])
        else:
            print("[*] No port range provided. Scanning all ports (1-65535).")
            start_port, end_port = 1, 65535

        ports = range(start_port, end_port + 1)
    except (IndexError, ValueError):
        print("Invalid port range. Use the format <start_port>-<end_port> (e.g., 1-65535).")
        sys.exit(1)

    print(f"Scanning IP: {ip} on ports {start_port}-{end_port}...\n")
    port_scanner(ip, ports)

    if open_ports:
        print("\nOpen Ports:")
        for port in sorted(open_ports):
            print(f" - Port {port}: Open")
    else:
        print("\nLooks like no ports are open :(")


if __name__ == "__main__":
    main()
