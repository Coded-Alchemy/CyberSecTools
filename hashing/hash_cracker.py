import hashlib
import pyfiglet
import optparse

# Algorithm list this script works with.
algorithm_list = ['md5', 'sha256', 'sha512', 'sha384']

def crack_hash(hash_to_crack, wordlist_path, algorithm):
    """
    Attempts to crack the given hash using a wordlist and specified algorithm.

    Parameters:
    hash_to_crack (str): The hash to be cracked.
    wordlist_path (str): The file path of the wordlist to use.
    algorithm (str): The hashing algorithm to use ('md5' or 'sha256').

    Returns:
    str: The cracked password if found, or None if not.
    """
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='replace') as file:
            for line in file:
                password = line.strip()  # Remove extra whitespace/newlines
                # Select the hashing algorithm
                if algorithm == algorithm_list[0]:
                    hashed_password = hashlib.md5(password.encode()).hexdigest()
                elif algorithm == algorithm_list[1]:
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                elif algorithm == algorithm_list[2]:
                    hashed_password = hashlib.sha512(password.encode()).hexdigest()
                elif algorithm == algorithm_list[3]:
                    hashed_password = hashlib.sha384(password.encode()).hexdigest()
                else:
                    raise ValueError(f"Unsupported algorithm: {algorithm}")

                if hashed_password == hash_to_crack:
                    return password
    except FileNotFoundError:
        print(f"[!] Error: Wordlist file '{wordlist_path}' not found.")
        exit(1)
    except Exception as e:
        print(f"[!] An error occurred: {e}")
        exit(1)
    return None


def main():
    """
    Main function to parse arguments, display banner, and attempt to crack the hash.
    """
    # Display banner
    ascii_banner = pyfiglet.figlet_format("Hash Cracker")
    print(ascii_banner)
    print("Welcome to the Hash Cracker, lets do some crack!\n")

    # Set up argument parser
    parser = optparse.OptionParser(
        usage="usage: %prog -w <wordlist> -H <hash> [-a <algorithm>]",
        description="A hash cracker for MD5 and SHA256 hashes using a wordlist."
    )
    parser.add_option("-w", dest="wordlist", type="string", help="Specify the wordlist file path.")
    parser.add_option("-H", dest="hash", type="string", help="Specify the hash to crack.")
    parser.add_option("-a", dest="algorithm", type="string", default="md5",
                      help="Specify the hashing algorithm (default: md5). Options: md5, sha256, sha512, sha384.")

    (options, args) = parser.parse_args()

    # Validate required arguments
    if not options.wordlist or not options.hash:
        parser.error("Both wordlist and hash are required. Use -w and -h options.")

    wordlist_path = options.wordlist
    hash_to_crack = options.hash
    algorithm = options.algorithm.lower()

    # Validate algorithm
    if algorithm not in algorithm_list:
        print(f"[!] Error: Unsupported algorithm '{algorithm}'. Use {algorithm_list}.")
        exit(1)

    print(f"[*] Attempting to crack hash: {hash_to_crack}")
    print(f"[*] Using wordlist: {wordlist_path}")
    print(f"[*] Hashing algorithm: {algorithm}\n")

    # Attempt to crack the hash
    cracked_password = crack_hash(hash_to_crack, wordlist_path, algorithm)
    if cracked_password:
        print(f"[+] Password found: {cracked_password}")
    else:
        print("[!] No matching password found in the wordlist.")


if __name__ == "__main__":
    main()
