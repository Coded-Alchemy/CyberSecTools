import argparse
import hashlib
import os


def sha256_hash_string(input_string):
    """
    Calculate the SHA-256 hash of a string.

    Args:
    input_string (str): The string to hash.

    Returns:
    str: The SHA-256 hash of the input string.
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode('utf-8'))
    return sha256_hash.hexdigest()


def sha256_hash_file(file_path):
    """
    Calculate the SHA-256 hash of a file.

    Args:
    file_path (str): The path to the file to hash.

    Returns:
    str: The SHA-256 hash of the file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: The file '{file_path}' does not exist.")

    sha256_hash = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:
            for byte_block in iter(lambda: file.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    except Exception as exception:
        raise RuntimeError(f"An error occurred while hashing the file: {exception}")


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="SHA-256 Hashing Utility",
        usage="%(prog)s [-s STRING | -f FILE]"
    )

    # Add arguments
    parser.add_argument('-s', '--string', type=str, help='Enter a string to hash')
    parser.add_argument('-f', '--file', type=str, help='Enter the path of the file to hash')

    # Parse arguments
    args = parser.parse_args()

    # Check if no arguments were passed
    if not args.string and not args.file:
        print("Error: You must specify either a string (-s) or a file (-f) to hash.")
        parser.print_help()
        return

    # Handle string hashing
    if args.string:
        hashed_string = sha256_hash_string(args.string)
        print(f"SHA-256 Hash of the string: {hashed_string}")

    # Handle file hashing
    if args.file:
        try:
            hashed_file = sha256_hash_file(args.file)
            print(f"SHA-256 Hash of the file: {hashed_file}")
        except (FileNotFoundError, RuntimeError) as exception:
            print(exception)


if __name__ == '__main__':
    main()
