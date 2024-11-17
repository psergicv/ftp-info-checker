# ftp-info-checker
A Python script for scanning FTP servers to check if the FTP port is open, retrieve server information, test for anonymous access, and assess default credentials.


## Features
- Checks if FTP port 21 is open.
- Retrieves FTP server banner.
- Tests for anonymous access.
- Tests a set of common default credentials.
- Checks for FTPS support.
- Logs results to a file named `ftp_checker/<IP>_ftp.txt`.

## Usage
1. Clone the repository:
   ```
   git clone https://github.com/your-username/ftp_scanner.git
   cd ftp_scanner
   ```

2. Run the script:
   ```
   python ftp_scanner.py
   ```

3. Enter a single IP, multiple IPs (comma-separated), or a file containing IPs.

## Disclaimer
This script is intended for educational purposes and ethical testing only. Do not use it to scan IPs or systems without explicit permission from their owners.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
   
