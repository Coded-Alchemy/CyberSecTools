import argparse
import nmap
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore

# Create a semaphore for controlling access to the console output
screenLock = Semaphore(value=1)


def nmap_scan_for_port(target_host, target_port, nm_scan):
    """
    Scan a specific port and print the results including detailed service information.
    """
    try:
        nm_scan.scan(target_host, str(target_port))

        # Get the state of the port (open or closed)
        port_state = nm_scan[target_host]['tcp'][int(target_port)]['state']

        # Prepare the prefix (- or +) for the port state
        port_prefix = "[+]" if port_state == "open" else "[-]"

        # Get the service name, product, version and extra info for open ports
        service_name = nm_scan[target_host]['tcp'][int(target_port)].get('name', 'Unknown')
        product = nm_scan[target_host]['tcp'][int(target_port)].get('product', 'Unknown')
        version = nm_scan[target_host]['tcp'][int(target_port)].get('version', 'Unknown')
        extra_info = nm_scan[target_host]['tcp'][int(target_port)].get('extrainfo', 'None')

        # Format the service info output for open ports
        if port_state == "open":
            service_info = f", Service: {service_name}, Info: {product} {version} {extra_info}"
        else:
            service_info = f", Service: {service_name}"

        # Print the formatted output in one line
        with screenLock:
            print(f"{port_prefix} Port: {target_port}, State: {port_state}{service_info}")

    except Exception as error:
        with screenLock:
            print(f"Error scanning port {target_port}: {error}")


def nmap_scan(target_host, target_ports=None):
    """
    Perform a full scan or a partial scan based on the provided ports.
    """
    options = "-sT -sV -O -A"  # TCP connect scan with service version detection
    nm_scan = nmap.PortScanner()

    try:
        # Scan specific ports or all ports
        if target_ports:
            # Print host and state once
            with screenLock:
                print(f"\nScan Results for: {target_host}")
                nm_scan.scan(target_host, ','.join(target_ports), options)
                print(f"State: {nm_scan[target_host].state()}")  # Host state (up/down)
                print(f"Protocol: tcp")

            # Create a thread pool to scan ports concurrently
            with ThreadPoolExecutor() as executor:
                futures = []
                for port in target_ports:
                    futures.append(executor.submit(nmap_scan_for_port, target_host, port, nm_scan))

                # Wait for all threads to complete
                for future in as_completed(futures):
                    pass

        else:
            # If no ports specified, scan all ports (1-65535)
            nm_scan.scan(target_host, '1-65535', options)
            print(f"\nScanning all ports on {target_host}...")

            # Print host and state once
            with screenLock:
                print(f"\nScan Results for: {target_host}")
                print(f"State: {nm_scan[target_host].state()}")  # Host state (up/down)
                print(f"Protocol: tcp")

            # Create a thread pool to scan ports concurrently
            with ThreadPoolExecutor() as executor:
                futures = []
                for port in nm_scan[target_host]['tcp']:
                    futures.append(executor.submit(nmap_scan_for_port, target_host, port, nm_scan))

                # Wait for all threads to complete
                for future in as_completed(futures):
                    pass

    except nmap.nmap.PortScannerError as error:
        print(f"PortScannerError: {error}")
    except Exception as error:
        print(f"An error occurred: {error}")


def run():
    """
    Main function to parse command line arguments and initiate the nmap scan.
    """
    parser = argparse.ArgumentParser(description='Nmap Port Scanner')
    parser.add_argument('-H', '--host', required=True, help='Specify target host (IP address or hostname)')
    parser.add_argument('-p', '--port', required=False, help='Specify target port[s] separated by commas')

    args = parser.parse_args()
    target_host = args.host

    # Create a ThreadPoolExecutor with a maximum of 10 concurrent threads
    if args.port:
        target_ports = args.port.split(',')
        target_ports = [port.strip() for port in target_ports]  # Clean up any extra spaces
        # Start scanning with specified ports
        nmap_scan(target_host, target_ports)
    else:
        # Scan all ports if no specific ports are provided
        nmap_scan(target_host)


if __name__ == '__main__':
    try:
        run()
    except Exception as exception:
        print(f"An unexpected error occurred: {exception}")
