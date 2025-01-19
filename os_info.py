import platform


def get_os_name():
    """
        Returns the name of the operating system.

        This function uses the `platform.system()` function to determine
        the name of the operating system the script is currently running on.

        Returns:
            str: The name of the operating system (e.g., 'Windows', 'Linux', 'Darwin').

    """
    return platform.system()


def get_os_version():
    """
        Returns the version of the operating system.

        This function uses the `platform.release()` function to determine
        the version of the operating system the script is currently running on.

        Returns:
            str: The version of the operating system

    """
    return platform.release()


def get_os_details():
    """
        Returns the details of the operating system.

        This function uses the `platform.version()` function to determine
        the details of the operating system the script is currently running on.

        Returns:
            str: The details of the operating system

    """
    return platform.version()


def main():
    try:
        print(f"Operating System: {get_os_name()}")
        print(f"Version: {get_os_version()}")
        print(f"Details: {get_os_details()}")
    except Exception as error:
        print(f"An unexpected error occurred: {error}")


if __name__ == "__main__":
    main()
