# Content
setup
File paths
File functions
Example commands
Known issues

# Setup
Use terminal to cd into file location eg: cd documents/GhostPort
Run python Ghostport.py
enter command (see example commands for direction of use)

# File paths

GhostPort
|
|-- testing/
|   |- tests.txt
|
|-- Utils/
|   |- output.py <-- JSON, TXT, CSV export
|
|-- Ghostport.py <-- mian entrypoint and runner for CLI

# File functions

output.py
output_results - drives the other functions
write_txt - writes to a text file 
write_csv - writes to a csv file
write_json - writes to a json file
print_open_ports - prints the open ports

Ghostport.py
get_service_name - returns the port service name (if known) using a dictionary
parse_port_range - parses the input to the necessary info
Scan_port_sync - scans a port with the async function
Scan_port - scans a port without the async function
Sequential - sequentially scans the ports 1 by 1
Fast_sequential - does same as sequential but faster
Multi_threaded - uses the multithreaded feature from asyncio to rapidly run multiple instances of the loop simultaniously
Async_scan - uses the asynchronous semaphore feature to run simultaniously. Similar to multithreaded just a different approach
Stealth - slowly runs scan_port to be less likely to be detected
Aggressive - uses Async_scan and massively overpowers it to be incredbily fast
Balanced - uses Multithreaded for a swift scan thats a good balance of speed
Main - checks for valid inputs such as target and mode and calls in the necessary functions to execute and output

# syntax of inputs
--target - required, makes the user input what the IP or domain is being targetted
--output - optional, if the user wants to output the results the can choose file and file path with the extension of .txt, .csv or .json. If the file doesnt already exist the name inputted will be created
--range - allows the user to select a range of ports to scan. Default is 1-1024
-- mode - allows the user to choose a mode that they want to use for the scan

# example commands
python Ghostport.py --target example.com --mode 2 --range 1-100 
python Ghostport.py --target example.com --mode 6 --range 1-100 --output results.txt
python Ghostport.py --target example.com --mode 5 --output results.csv 

# Known issues
doesnt work on linux yet