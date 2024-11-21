import socket
from ftplib import FTP, FTP_TLS, error_perm
import datetime
from concurrent.futures import ThreadPoolExecutor
import os


def check_folder_content(ftp, folder=""):
    """
    Allows user to navigate through folders on the FTP server
    """
    current_path = folder or "/"
    os.makedirs("data", exist_ok=True)

    while True:
        print(f"\nCurrent Directory: {current_path}")
        try:
            ftp.cwd(current_path)
            items = []
            ftp.retrlines('LIST', items.append)

            directories, files = [], []
            print("\nContents:")
            for idx, item in enumerate(items, start=1):
                parts = item.split(maxsplit=8) # Split LIST output
                name = parts[-1] # File or Directory name
                is_directory = item.startswith("d") # Check if it is a directory
                if is_directory:
                    directories.append(name)
                    print(f"{idx}. [DIR] {name}")
                else:
                    files.append(name)
                    print(f"{idx}. [FILE] {name}")

            # What the user is going to do?
            print("\nOptions:")
            print("[0] Go back to the parent directory")
            print("[1-n] Open folder by number (if applicable")
            print("[d] Download file by number")
            print("[q] Quit navigation")

            choice = input("Enter your choice: ").strip()
            if choice.lower() == "q":
                print("Exiting folder navigation.")
                break
            elif choice == "0":
                current_path = "../"
            elif choice == "d":
                # Ask to download a file
                file_choice = input("Enter file number to download: ").strip()
                if file_choice.isdigit() and 1 <= int(file_choice) <= len(files):
                    selected_file = files[int(file_choice) - 1]
                    download_path = os.path.join("data", selected_file)
                    with open(download_path, "wb") as f:
                        ftp.retrbinary(f"RETR {selected_file}", f.write)
                    print(f"File '{selected_file}' downloaded to 'data/{selected_file}'.")
                else:
                    print("Invalid file choice. Please try again.")
            elif choice.isdigit() and 1 <= int(choice) <= len(items):
                selected_directory = directories[int(choice) - 1]
                current_path = f"{current_path.rstrip(f'/')}/{selected_directory}"
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error navigating folder: {e}")
            break

# Check FTP details for a given IP address
def check_ftp(ip):
    # Create a log file for the current IP
    log_file = f"ftp_checker/{ip}_ftp_checker.txt"

    # Log messages to the file
    def log(message):
        print(message)
        with open(log_file, "a") as file:
            file.write(message + "\n")

    log(f"--- FTP Scan Result for {ip} ---")
    log(f"Scan started at: {datetime.datetime.now()}")

    # Check if FTP port is open
    try:
        with socket.create_connection((ip, 21), timeout=5) as sock:
            log(f"FTP port 21 is open on {ip}")
    except socket.error:
        log(f"FTP port 21 is not open on {ip}. Finishing scan.")
        return

    # Attempt to connect and check server banner
    try:
        ftp = FTP()
        ftp.connect(ip, 21, timeout=10)
        banner = ftp.getwelcome()
        log(f"Server Banner: {banner}")
    except Exception as e:
        log(f"Could not retrieve server banner: {e}")
        return

    # Check for anonymous login
    try:
        ftp.login()
        log(f"Anonymous login is allowed on {ip}.")
        log("Listing directories for anonymous access:")
        directories = []
        ftp.retrlines('LIST', directories.append)
        for directory in directories:
            log(directory)
        print("Directories retrieved successfully.")

        # Ask user if they want to explore the folders
        explore = input("Would you like to explore the folders content? (y/n): ").strip().lower()
        if explore == "y":
            check_folder_content(ftp)
        ftp.quit()
        return
    except error_perm as e:
        log(f"Anonymous login is not allowed on {ip}.")
        log(f"Server response: {e}")
    except Exception as e:
        log(f"Could not connect to FTP server on {ip}: {e}")
        return

    # Test default credentials
    default_credentials = [
        ('admin', 'admin'),
        ('ftp', 'ftp'),
        ('anonymous', ''),
        ('user', 'pass'),
        ('anonymous', 'anonymous'),
        ('guest', 'guest'),
        ('guest', ''),
    ]

    for username, password in default_credentials:
        try:
            ftp = FTP()
            ftp.connect(ip, 21, timeout=10)
            ftp.login(username, password)
            log(f"Login successful with credentials: {username}/{password}")
            ftp.quit()
            break
        except error_perm:
            log(f"Login failed for: {username}/{password}")
        except Exception as e:
            log(f"Could not perform login check with {username}/{password}: {e}")

    # Check for FTPS support
    try:
        ftps = FTP_TLS()
        ftps.connect(ip, 21, timeout=10)
        ftps.auth()
        ftps.login()
        log("FTPS supported. Anonymous login successfule over FTPS")
        ftps.quit()
    except Exception as e:
        log(f"FTPS check failed: {e}")


    log(f"Scan completed at: {datetime.datetime.now()}")
    log("---------------------------------------------")


def main():
    ips = input("Enter IPs to scan (comma-separated) or a filename: ").strip()

    # Is the users input a file of a list of IPs?
    if ".txt" in ips:
        with open(ips) as file:
            ip_list = [line.strip() for line in file.readlines()]
    else:
        ip_list = ips.split(",")

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(check_ftp, ip_list)

    print("Scan completed. Check the generated .txt files for results")

if __name__ == "__main__":
    main()
