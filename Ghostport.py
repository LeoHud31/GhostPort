import argparse
import socket
import asyncio
import time
import concurrent.futures
from Utils import output
from typing import Iterable, List, Dict, Optional, Union

#handles ports and ranges
def parse_port_range(port_input):
    port_input = str(port_input)
    if '-' in port_input:
        start, end = map(int, port_input.split('-'))
        return start, end
    else:
        port = int(port_input)
        return port, port

def Scan_port(host: str, port: int, timeout: float = 1) -> Dict[str, bool]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        err = sock.connect_ex((host, port))
        sock.close()
        return {"Open": err == 0}
    except Exception:
        return {"Open": False}


def Sequential(host, ports, timeout = 1, delay = 0):
    open_ports = []
    for port in ports:
        result = Scan_port(host, port, timeout)
        if result.get('open'):
            print(f"Open: {port}")
            open_ports.append(port)
        if delay > 0:
            time.sleep(delay)
    return sorted(open_ports)

async def Fast_sequential(host, ports, timeout = 0.3, delay = 0):
    open_ports = []
    for port in ports:
        result = Scan_port(host, port, timeout)
        if result.get('open'):
            print(f"Open: {port}")
            open_ports.append(port)
        if delay > 0:
            time.sleep(delay)
    return sorted(open_ports)

async def Multi_threaded(host, ports, timeout=0.2, workers=100):
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_port = {
            executor.submit(Scan_port, host, port, timeout): port
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


async def Async_scan(host, ports, port,  timeout = 0.15, semaphore_limit = 500):
    semaphore = asyncio.Semaphore(semaphore_limit)
    open_ports = []

    async with semaphore:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return {"Open": port}
        except Exception as e:
            print(f"Error occured at {e}")

    tasks = [Scan_port(port) for port in ports]
    results = await asyncio.gather(*tasks)

    for result in results:
        if result["open"]:
            print(f"Open: {result['port']}")
            open_ports.append(result["port"])
    return sorted(open_ports)

async def Stealth(host, ports, timeout = 1.5, delay = 0.5):
    return Multi_threaded(host, ports, timeout, delay)

async def Aggressive(host, ports, timeout=0.1, semaphore_limit=1000):
    return asyncio.run(Async_scan(host, ports, timeout, semaphore_limit))

async def Balanced(host, ports, timeout=0.5, workers =50):
    return Multi_threaded(host, ports, timeout, workers)

async def main(args: argparse.Namespace) -> None:
    try:
        target = args.target
        if target == False:
            print("Invalid target")

        if args.range:
            try:
                start_port, end_port = parse_port_range(args.range)
            except ValueError:
                print("Invalid port range format")
        else:
            start_port, end_port = 1,1024

        if args.mode:
            try:
                if args.mode == 1:
                    await Sequential()
                elif args.mode == 2:
                    await Fast_sequential()
                elif args.mode == 3:
                    await Multi_threaded()
                elif args.mode == 4:
                    await Async_scan()
                elif args.mode == 5:
                    await Stealth()
                elif args.mode == 6:
                    await Aggressive()
                elif args.mode ==7:
                    await Balanced()
                else:
                    print("Invalid mode. Chosse 1-7")
                    return
            except Exception as e:
                print("Error in mode execution")


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