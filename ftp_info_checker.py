import socket
from ftplib import FTP, FTP_TLS, error_perm
import datetime
from concurrent.futures import ThreadPoolExecutor


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
        ('anonympus', ''),
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
