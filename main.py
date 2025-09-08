import argparse
import socket
import asyncio
import concurrent.futures
import threading
import time
from Utils import output


#takes host and port if result = 0, dont move on if returns anything else print error scanning port
def Scan_port(host, port, timeout = 1):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #default timeout is 1 second
        sock.settimeout(timeout)
        #connect save status to result then close
        result = sock.connect_ex((host, port))
        sock.close()
        return port if result == 0 else None  
    except Exception as e:
        print(f"Error scanning port {port}: {e}")

#new scan port function
#needs to take in arguments (host, start_port, end_port, timeout, workers, semaphore, delay_between_ports)
#If Async used switch case between method == 1 sequential, 2 fast sequential, 3 multi-threaded, 4 Async turbo, else use default
#If mode used switch case between method == stealth, Aggressive, Balanced
#best to make each Async method and each mode its own sub function and call in a switch case

def sequential(host, ports, timeout = 1, delay = 0):
    open_ports = []
    for port in ports:
        result = Scan_port(host, port, timeout)
        if result['open']:
            print(f"Open: {port}")
            open_ports.append(port)
        if delay > 0:
            time.sleep(delay)
    return sorted(open_ports)

def fast_sequential(host, ports, timeout = 0.3, delay = 0):
    open_ports = []
    for port in ports:
        result = Scan_port(host, port, timeout)
        if result['open']:
            print(f"Open: {port}")
            open_ports.append(port)
        if delay > 0:
            time.sleep(delay)
    return sorted(open_ports)


def multi_threaded(host, ports, timeout=0.2, workers=100):
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_port = {
            executor.submit(sequential, host, port, timeout): port
            for port in ports
        }

        for future in concurrent.futures.as_completed(future_port):
            port = future_port[future]

            try:
                result = future.result()
                if result['open']:
                    print(f"Open {port}")
                    open_ports.append(port)
            
            except Exception as e:
                print(f"Error scanning port {port}: {e}")
    return sorted(open_ports)

async def async_scan(host, ports, timeout=0.15, semaphore_limit=500):
    semaphore = asyncio.Semaphore(semaphore_limit)
    open_ports = []

    async def scan_port_async(port):
        async with semaphore:
            try:
                future = asyncio.open_connection(host, port)
                reader, writer = await asyncio.wait_for(future, timeout=timeout)
                writer.close()
                await writer.wait_closed()
                return {'Open': port}
            except:
                return {'Closed': port}
        
    tasks = [scan_port_async(port) for port in ports]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, dict) and result['open']:
            print(f"Open: {result['port']}")
            open_ports.append(result['port'])

    return sorted(open_ports)

def stealth_scan(host, ports, timeout=2.0, delay=1.0):
    return sequential(host, ports, timeout, delay)

def aggressive_scan(host, ports, timeout=0.05, semaphore_limit=1000):
    return asyncio.run(async_scan(host, ports, timeout, semaphore_limit))

def balanced_scan(host, ports, timeout=0.5, workers=50):
    return multi_threaded(host, ports, timeout, workers)


#scanning range takes host, start and end port
def Scan_port_range(host, start_port, end_port, method=1, mode=None, **kwargs):
    #sets empty array
    ports = list(range(start_port, end_port + 1))
    
    # Special modes override method selection
    if mode == 'stealth':
        return stealth_scan(host, ports, **kwargs)
    elif mode == 'aggressive':
        return aggressive_scan(host, ports, **kwargs)
    elif mode == 'balanced':
        return balanced_scan(host, ports, **kwargs)
    
    # Method-based scanning
    if method == 1:
        # Sequential scanning
        timeout = kwargs.get('timeout', 1.0)
        delay = kwargs.get('delay', 0)
        return sequential(host, ports, timeout, delay)
        
    elif method == 2:
        # Fast sequential
        timeout = kwargs.get('timeout', 0.3)
        delay = kwargs.get('delay', 0)
        return fast_sequential(host, ports, timeout, delay)
        
    elif method == 3:
        # Multi-threaded
        timeout = kwargs.get('timeout', 0.2)
        workers = kwargs.get('workers', 100)
        return multi_threaded(host, ports, timeout, workers)
        
    elif method == 4:
        # Async turbo
        timeout = kwargs.get('timeout', 0.15)
        semaphore = kwargs.get('semaphore', 500)
        return asyncio.run(async_scan(host, ports, timeout, semaphore))
        
    else:
        # Default to sequential
        return sequential(host, ports, 1.0, 0)

#handles ports and ranges
def parse_port_range(port_input):
    port_input = str(port_input)
    if '-' in port_input:
        start, end = map(int, port_input.split('-'))
        return start, end
    else:
        port = int(port_input)
        return port, port

async def main(args: argparse.Namespace) -> None:
    try:
        target = args.target
        if target == False:
            print("Invalid target")
            return

        if args.range:
            try:
                start_port, end_port = parse_port_range(args.range)
            except ValueError:
                print("Invalid port range format")
        
        else:
            start_port, end_port = 1,1024

        method = 1
        mode = None

        if args.async_mode:
            try:
                method = int(args.async_mode)
                if method not in [1, 2, 3, 4]:
                    print("Invalid async method. Use 1-4")
                    return
            except ValueError:
                # Check if it's a mode string
                if args.async_mode.lower() in ['stealth', 'aggressive', 'balanced']:
                    mode = args.async_mode.lower()
                else:
                    print("Invalid async parameter. Use 1-4 or stealth/aggressive/balanced")
                    return
        
        print(f"scanning {target} for ports {start_port}  {end_port}")

        open_ports = Scan_port_range(target, start_port, end_port)
        
        if open_ports:
            print(f"Found {len(open_ports)} open ports: {open_ports}")
            if args.output:
                output.output_results(open_ports, args.output)
            else:
                output.output_results(open_ports)

    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GhostPort: A tool for port scanning")

    parser.add_argument("--target", required=True, help="set the target (IP or Domain)")
    parser.add_argument("--Async", type=str, help="Async mode 50-100x faster than sequential")
    parser.add_argument("--range", type=str, help="choose range of ports to scan (eg: 22, 80 or 22-50)")
    parser.add_argument("--output", type=str, help="output file name (supports .txt, .csv .json)")

    args = parser.parse_args()
    asyncio.run(main(args))