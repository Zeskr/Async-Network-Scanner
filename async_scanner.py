import asyncio
import argparse
import socket

async def grab_banner(reader, writer):
    """Attempts to read the service banner"""
    try:
        # Sends a generic request
        writer.write(b"HEAD / HTTP/1.0\r\n\r\n")
        await writer.drain()

        banner = await asyncio.wait_for(reader.read(1024), timeout=2.0)
        return banner.decode('utf-8', errors='ignore').strip().split('\n')[0][:50]
    except Exception:
        return "Unknown Service / No Banner"
    finally:
        writer.close()
        await writer.wait_closed()

async def scan_port(ip, port, timeout):
    """Attempts a TCP connection to a specific port"""
    try:
        # Open connection with a strict timeout
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout
        )
        banner = await grab_banner(reader, writer)
        print(f"[+] Port {port}/tcp is OPEN - Banner: {banner}")
        return port
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        # Port is closed/filtered
        return None

async def main():
    parser = argparse.ArgumentParser(description="Async TCP Port Scanner")
    parser.add_argument('target', help="Target IP address")
    parser.add_argument('--start', type=int, default=1, help="Start port (default: 1)")
    parser.add_argument('--end', type=int, default=1024, help="End port (default: 1024)")
    parser.add_argument('-t', '--timeout', type=float, default=1.0, help="Connection timeout in seconds")
    args = parser.parse_args()

    target_ip = socket.gethostbyname(args.target)
    print(f"[*] Starting async scan against {target_ip} (Ports {args.start}-{args.end})...")

    # Create a list
    tasks = []
    for port in range(args.start, args.end + 1):
        tasks.append(scan_port(target_ip, port, args.timeout))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)
    print("[*] Scan complete.")

if __name__ == '__main__':
    # Run the async event loop
    asyncio.run(main())
