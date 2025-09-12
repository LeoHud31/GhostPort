import argparse
import socket
import asyncio
import time
import concurrent.futures
from Utils.output import output

#service info NOT WORKING
banner_dictionary = {
    "20": "FTP",
    "21": "FTP",
    "22": "SSH",
    "23": "Telnet",
    "25": "SMTP",
    "53": "DNS",
    "80": "HTTP",
    "110": "POP3",
    "119": "NNTP",
    "123": "NTP",
    "143": "IMAP",
    "161": "SNMP",
    "194": "IRC",
    "443": "HTTPS"
}

def get_service_info(port):
    service_name = banner_dictionary.get(str(port))
    is_known = str(port) in banner_dictionary
    return{
        'port': port,
        'service': service_name,
        'known': is_known
    }

def get_service_name(port):
    """Get service name from port number using your dictionary"""
    return banner_dictionary.get(str(port), f"Unknown-{port}")

def is_known_service(port):
    """Check if port is in your dictionary"""
    return str(port) in banner_dictionary

def get_service_info(port):
    """Get both port and service name"""
    service = get_service_name(port)
    known = is_known_service(port)
    return {
        'port': port,
        'service': service,
        'known': known
    }
    

#handles ports and ranges
def parse_port_range(port_input):

    port_input = str(port_input)
    if '-' in port_input:
        start, end = map(int, port_input.split('-'))
        return start, end
    else:
        port = int(port_input)
        return port, port

#scan port without the async function
def Scan_port_sync(host, port, timeout = 0):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        err = sock.connect_ex((host, port))
        sock.close()
        return {"open": err == 0, "port": port}
    except Exception:
        return {"open": False, "port": port}

#scan port with async, dont remove the reader variable, although its not called dont remove it or it wont works
async def Scan_port(host, port, timeout = 0):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        try:
            await writer.wait_closed()
        except AttributeError:
            pass
        return {"open": True, "port": port}
    except Exception:
        return {"open": False, "port": port}

#scans port with async and has a smaller timeout
async def Sequential(host, ports, timeout = 0.3, delay = 0.1):
    open_ports = []
    for port in ports:
        result = await Scan_port(host, port, timeout)
        if result.get('open'):
            print(f"Open: {port}")
            open_ports.append(port)
        if delay > 0:
            await asyncio.sleep(delay)
    return open_ports

#faster as has even smaller timeout
async def Fast_sequential(host, ports, timeout = 0.3, delay = 0):
    open_ports = []
    for port in ports:
        result = await Scan_port(host, port, timeout)
        if result.get('open'):
            print(f"Open: {port}")
            open_ports.append(port)
        if delay > 0:
            await asyncio.sleep(delay)
    return open_ports

#multithreading has short timeout and 100 workers, distributes the work over 100 sub processes
async def Multi_threaded(host, ports, timeout=0.2, workers=100):
    open_ports = []
    loop = asyncio.get_event_loop()

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_port = {
            loop.run_in_executor(executor, Scan_port_sync, host, port, timeout)
            for port in ports
        }

        for task in asyncio.as_completed(future_port):
            try:
                result = await task
                if result['open']:
                    print(f"Open {result['port']}")
                    open_ports.append(result["port"])
            
            except Exception as e:
                print(f"Error scanning port: {e}")
    return open_ports

#similar to multithreaded but uses async and semaphore rather than multithreaded
async def Async_scan(host, ports, timeout = 1, semaphore_limit = 200):
    semaphore = asyncio.Semaphore(semaphore_limit)
    open_ports = []

    async def Scan_with_semaphore(port):
        async with semaphore:
            return await Scan_port(host, port, timeout)

    tasks = [asyncio.create_task(Scan_with_semaphore(port)) for port in ports]
    results = await asyncio.gather(*tasks)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Error scanning port {ports[i]}: {result}")
            continue
        if result["open"]:
            print(f"Open: {result['port']}")
            open_ports.append(result["port"])

    return open_ports

#uses the sacn port but slows it down
async def Stealth(host, ports, timeout = 0.6, delay = 0.2):
    open_ports = []
    for port in ports:
        result = await Scan_port(host, port, timeout)
        if result.get('open'):
            print(f"Open: {port}")
            open_ports.append(port)
        if delay > 0:
            await asyncio.sleep(delay)
    return open_ports

#very fast version of async
async def Aggressive(host, ports, timeout=0.6, semaphore_limit=1000):
    return await Async_scan(host, ports, timeout, semaphore_limit)

#quick using multi threaded
async def Balanced(host, ports, timeout=0.5, workers =50):
    return await Multi_threaded(host, ports, timeout, workers)

#main function
async def main(args: argparse.Namespace) -> None:
    try:
        target = args.target
        if not target:
            print("Invalid target")
            return

        if args.range:
            try:
                start_port, end_port = parse_port_range(args.range)
            except ValueError:
                print("Invalid port range format")
        else:
            start_port, end_port = 1,1024

        ports = range(start_port, end_port +1)

        #loops through modes
        if args.mode:
            try:
                start_time = time.time()
                output_time = time.ctime()
                print(f"Scanning {target} ports {start_port}-{end_port} in mode {args.mode}")
                print(f"start time of {output_time}")
                

                if args.mode == 1:
                    print("Using Sequential mode\n")
                    open_ports = await Sequential(target, ports)
                elif args.mode == 2:
                    print("Using fast-Sequential mode\n")
                    open_ports = await Fast_sequential(target, ports)
                elif args.mode == 3:
                    print("Using Multi-threaded\n")
                    open_ports = await Multi_threaded(target, ports)
                elif args.mode == 4:
                    print("Using Async scan mode\n")
                    open_ports = await Async_scan(target, ports)
                elif args.mode == 5:
                    print("Using Stealth mode\n")
                    open_ports = await Stealth(target, ports)
                elif args.mode == 6:
                    print("Using Aggressive mode\n")
                    open_ports = await Aggressive(target, ports)
                elif args.mode ==7:
                    print("Using balanced mode\n")
                    open_ports = await Balanced(target, ports)
                else:
                    print("Invalid mode. Chosse 1-7")
                    return
                
                end_time = time.time()
                print(f"\nScan completed time taken {end_time - start_time:.2f} seconds")
                print(f"Open ports found: {open_ports}")

            except Exception as e:
               print(f"Error in mode execution {e}")

        
        if args.output:
            output.output_results(open_ports, args.output)
        else:
            output.output_results(open_ports)

    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description= "GhostPort: A tool for port scanning")

    parser.add_argument("--target", required=True, help="Set the target (IP or domain)")
    parser.add_argument("--output", type=str, help="output file name (supports .txt, .csv, .json)")
    parser.add_argument("--range", type=str, help="give range of ports")
    parser.add_argument("--mode", type=int, help="choose mode: 1- Sequential, 2- Fast Sequential, 3- Multi threaded, 4- Async Scan, 5- Stealth, 6- aggressive, 7- Balanced")

    args = parser.parse_args()
    asyncio.run(main(args))