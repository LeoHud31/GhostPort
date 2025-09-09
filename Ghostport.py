import argparse
import socket
import asyncio
import time
import concurrent.futures
from Utils import output


#handles ports and ranges
def parse_port_range(port_input):
    port_input = str(port_input)
    if '-' in port_input:
        start, end = map(int, port_input.split('-'))
        return start, end
    else:
        port = int(port_input)
        return port, port

def Scan_port_sync(host, port, timeout = 0.5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        err = sock.connect_ex((host, port))
        sock.close()
        return {"open": err == 0, "port": port}
    except Exception:
        return {"open": False, "port": port}


async def Scan_port(host, port, timeout = 0.5):
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


async def Sequential(host, ports, timeout = 0.6, delay = 0):
    open_ports = []
    for port in ports:
        result = await Scan_port(host, port, timeout)
        if result.get('open'):
            print(f"Open: {port}")
            open_ports.append(port)
        if delay > 0:
            await asyncio.sleep(delay)
    return open_ports

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

async def Stealth(host, ports, timeout = 0.6, delay = 0.5):
    open_ports = []
    for port in ports:
        result = await Scan_port(host, port, timeout)
        if result.get('open'):
            print(f"Open: {port}")
            open_ports.append(port)
        if delay > 0:
            await asyncio.sleep(delay)
    return open_ports

async def Aggressive(host, ports, timeout=0.5, semaphore_limit=1000):
    return await Async_scan(host, ports, timeout, semaphore_limit)

async def Balanced(host, ports, timeout=0.5, workers =50):
    return await Multi_threaded(host, ports, timeout, workers)

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

        if args.mode:
            try:
                print(f"Scanning {target} ports {start_port}-{end_port} in mode {args.mode}")
                start_time = time.time()

                if args.mode == 1:
                    open_ports = await Sequential(target, ports)
                elif args.mode == 2:
                    open_ports = await Fast_sequential(target, ports)
                elif args.mode == 3:
                    open_ports = await Multi_threaded(target, ports)
                elif args.mode == 4:
                    open_ports = await Async_scan(target, ports)
                elif args.mode == 5:
                    open_ports = await Stealth(target, ports)
                elif args.mode == 6:
                    open_ports = await Aggressive(target, ports)
                elif args.mode ==7:
                    open_ports = await Balanced(target, ports)
                else:
                    print("Invalid mode. Chosse 1-7")
                    return
                
                end_time = time.time()
                print(f"\n Scan completed time taken {end_time - start_time:.2f} seconds")
                print(f"Open ports found: {open_ports}")

            except Exception as e:
               print(f"Error in mode execution {e}")


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