#!/usr/bin/env python3
import socket
import threading
import sys
import time
from datetime import datetime
import argparse

class PortScanner:
    def __init__(self, host, timeout=3, threads=100):
        self.host = host
        self.timeout = timeout
        self.threads = threads
        self.open_ports = []
        self.lock = threading.Lock()
        
        self.services = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 993: "IMAPS",
            995: "POP3S", 3389: "RDP", 5432: "PostgreSQL", 3306: "MySQL",
            1433: "MSSQL", 6379: "Redis", 27017: "MongoDB", 5984: "CouchDB"
        }
    
    def resolve_hostname(self, hostname):
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            print(f"[-] Could not resolve hostname: {hostname}")
            return None
    
    def scan_port(self, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((self.host, port))
                
                if result == 0:
                    service = self.services.get(port, "Unknown")
                    with self.lock:
                        self.open_ports.append((port, service))
                        print(f"[+] Port {port} - {service} - OPEN")
        except Exception as e:
            pass
    
    def scan_range(self, start_port, end_port):
        print(f"\n[*] Starting port scan on {self.host}")
        print(f"[*] Scanning ports {start_port}-{end_port}")
        print(f"[*] Timeout: {self.timeout}s | Threads: {self.threads}")
        print(f"[*] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        start_time = time.time()
        
        threads = []
        for port in range(start_port, end_port + 1):
            while len(threads) >= self.threads:
                threads = [t for t in threads if t.is_alive()]
                time.sleep(0.01)
            
            thread = threading.Thread(target=self.scan_port, args=(port,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("-" * 50)
        print(f"[*] Scan completed in {duration:.2f} seconds")
        print(f"[*] Found {len(self.open_ports)} open ports")
        
        if self.open_ports:
            print("\n[+] Open Ports Summary:")
            for port, service in sorted(self.open_ports):
                print(f"    {port:5d} - {service}")
        else:
            print("\n[-] No open ports found")
    
    def scan_common_ports(self):
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 
                       993, 995, 1723, 3306, 3389, 5432, 5900, 8080, 8443]
        
        print(f"\n[*] Scanning common ports on {self.host}")
        print(f"[*] Ports to scan: {len(common_ports)}")
        print(f"[*] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        threads = []
        for port in common_ports:
            thread = threading.Thread(target=self.scan_port, args=(port,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        print("-" * 50)
        print(f"[*] Found {len(self.open_ports)} open ports")
        
        if self.open_ports:
            print("\n[+] Open Ports Summary:")
            for port, service in sorted(self.open_ports):
                print(f"    {port:5d} - {service}")

def main():
    parser = argparse.ArgumentParser(description="Enhanced Port Scanner")
    parser.add_argument("host", help="Target hostname or IP address")
    parser.add_argument("-p", "--ports", help="Port range (e.g., 1-1000) or single port")
    parser.add_argument("-c", "--common", action="store_true", help="Scan common ports only")
    parser.add_argument("-t", "--timeout", type=float, default=3, help="Connection timeout (default: 3s)")
    parser.add_argument("--threads", type=int, default=100, help="Number of threads (default: 100)")
    
    args = parser.parse_args()
    
    original_host = args.host
    if not args.host.replace('.', '').isdigit():
        scanner_temp = PortScanner(args.host)
        resolved_ip = scanner_temp.resolve_hostname(args.host)
        if not resolved_ip:
            sys.exit(1)
        args.host = resolved_ip
        print(f"[*] Resolved {original_host} to {args.host}")
    
    scanner = PortScanner(args.host, args.timeout, args.threads)
    
    try:
        if args.common:
            scanner.scan_common_ports()
        elif args.ports:
            if '-' in args.ports:
                start, end = map(int, args.ports.split('-'))
                scanner.scan_range(start, end)
            else:
                port = int(args.ports)
                scanner.scan_port(port)
                if scanner.open_ports:
                    print(f"[+] Port {port} - {scanner.open_ports[0][1]} - OPEN")
                else:
                    print(f"[-] Port {port} - CLOSED")
        else:
            scanner.scan_common_ports()
            
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

def interactive_mode():
    print("=== Enhanced Port Scanner ===")
    
    host = input("Enter target IP/hostname: ").strip()
    if not host:
        print("[-] No host provided")
        return
    
    scanner_temp = PortScanner(host)
    if not host.replace('.', '').isdigit():
        resolved_ip = scanner_temp.resolve_hostname(host)
        if not resolved_ip:
            return
        print(f"[*] Resolved {host} to {resolved_ip}")
        host = resolved_ip
    
    print("\nScan options:")
    print("1. Scan single port")
    print("2. Scan port range")
    print("3. Scan common ports")
    
    choice = input("Select option (1-3): ").strip()
    
    scanner = PortScanner(host)
    
    try:
        if choice == '1':
            port = int(input("Enter port number: "))
            scanner.scan_port(port)
            if scanner.open_ports:
                print(f"[+] Port {port} - {scanner.open_ports[0][1]} - OPEN")
            else:
                print(f"[-] Port {port} - CLOSED")
        
        elif choice == '2':
            start = int(input("Enter start port: "))
            end = int(input("Enter end port: "))
            if start > end:
                print("[-] Start port must be less than end port")
                return
            scanner.scan_range(start, end)
        
        elif choice == '3':
            scanner.scan_common_ports()
        
        else:
            print("[-] Invalid choice")
    
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
    except ValueError:
        print("[-] Invalid port number")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        interactive_mode()