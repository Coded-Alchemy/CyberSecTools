import requests
import optparse
from threading import BoundedSemaphore, Thread

# Maximum number of simultaneous requests
maxConnections = 10
# Semaphore to limit the number of concurrent connection attempts
connection_lock = BoundedSemaphore(value=maxConnections)

# Global flag to track if enumeration should stop (not used here but could be for other features)
Stop = False


def check_directory(directory, base_url, release):
    """
    Check if the directory is valid by sending an HTTP request.

    Parameters:
    directory (str): The directory to test.
    base_url (str): The target base URL.
    release (bool): A flag indicating if the connection lock should be released after the attempt.

    The function prints valid directories if found.
    """
    try:
        url = f"http://{base_url}/{directory}.html"
        response = requests.get(url)
        if response.status_code != 404:  # Only print if the directory is valid
            print(f"[+] Valid directory: {url}")
    except requests.ConnectionError:
        pass
    except Exception as e:
        print(f"[!] Error checking {directory}: {e}")
    finally:
        if release:
            connection_lock.release()


def main():
    """
    Main function to parse command line arguments and start directory enumeration.
    """
    parser = optparse.OptionParser('usage: %prog -u <base URL> -f <wordlist file>')
    parser.add_option('-u', dest='base_url', type='string', help='specify base URL')
    parser.add_option('-f', dest='wordlist_file', type='string', help='specify wordlist file')

    (options, args) = parser.parse_args()

    base_url = options.base_url
    wordlist_file = options.wordlist_file

    # Validate that required options are provided
    if base_url is None or wordlist_file is None:
        print(parser.usage)
        exit(0)

    try:
        # Open the wordlist file
        with open(wordlist_file, 'r', encoding='utf-8', errors='replace') as fn:
            for line in fn.readlines():
                if Stop:
                    print("[*] Exiting...")
                    exit(0)

                connection_lock.acquire()  # Acquire lock for new connection attempt
                directory = line.strip('\r').strip('\n')  # Clean the directory string
                print(f"[-] Testing: {directory}")
                thread = Thread(target=check_directory, args=(directory, base_url, True))
                thread.start()  # Start a new thread for the directory check
    except FileNotFoundError:
        print(f"[!] Error: File {wordlist_file} not found.")  # Handle file not found error
    except Exception as e:
        print(f"[!] An error occurred: {e}")  # Handle other exceptions


if __name__ == '__main__':
    main()
