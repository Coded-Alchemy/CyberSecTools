import requests
import optparse

def enumerate_subdomains(domain, wordlist):
    """
    Enumerate subdomains for a given domain using a wordlist.

    Parameters:
    domain (str): The target domain.
    wordlist (str): Path to the wordlist file containing potential subdomains.

    Returns:
    None
    """
    try:
        # Read the wordlist file
        with open(wordlist, 'r', encoding='utf-8', errors='replace') as file:
            subdomains = file.read().splitlines()
    except FileNotFoundError:
        print(f"[!] Error: Wordlist file '{wordlist}' not found.")
        exit(1)

    print(f"[*] Enumerating subdomains for: {domain}")
    print(f"[*] Using wordlist: {wordlist}\n")

    for sub in subdomains:
        subdomain_url = f"http://{sub}.{domain}"
        try:
            response = requests.get(subdomain_url, timeout=5)
            if response.status_code == 200:
                print(f"[+] Valid subdomain: {subdomain_url}")
        except requests.ConnectionError:
            # Ignore connection errors for non-existent subdomains
            pass
        except Exception as e:
            print(f"[!] An error occurred: {e}")

    print("\n[*] Enumeration complete.")


def main():
    """
    Main function to parse command-line arguments and start subdomain enumeration.
    """
    parser = optparse.OptionParser(
        usage="usage: %prog -d <domain> -w <wordlist>",
        description="A subdomain enumeration tool using HTTP requests."
    )
    parser.add_option("-d", dest="domain", type="string", help="Specify the target domain.")
    parser.add_option("-w", dest="wordlist", type="string", help="Specify the wordlist file path.")

    (options, args) = parser.parse_args()

    # Validate required arguments
    if not options.domain or not options.wordlist:
        parser.error("Both domain and wordlist are required. Use -d and -w options.")

    domain = options.domain
    wordlist = options.wordlist

    enumerate_subdomains(domain, wordlist)


if __name__ == "__main__":
    main()
