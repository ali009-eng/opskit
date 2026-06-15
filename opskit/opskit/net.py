#!/usr/bin/env python3
import subprocess
import argparse
import sys

def ping_host(host):
    """Ping a host to check connectivity."""
    try:
        result = subprocess.run(["ping", "-c", "4", host], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[INFO] Host {host} is reachable.")
            print(result.stdout)
        else:
            print(f"[WARN] Host {host} is not reachable.")
            print(result.stderr)
    except FileNotFoundError:
        print("[ERROR] Command not found: ping")

def check_latency(host):
    """Check latency to a host using ping."""
    try:
        result = subprocess.run(["ping", "-c", "4", host], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            for line in lines:
                if "rtt=" in line:
                    print(line)
        else:
            print(f"[WARN] Host {host} is not reachable.")
            print(result.stderr)
    except FileNotFoundError:
        print("[ERROR] Command not found: ping")

def scan_ports(host):
    """Scan common ports on a host using nmap."""
    try:
        result = subprocess.run(["nmap", "-F", host], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[INFO] Port scan results for {host}:")
            print(result.stdout)
        else:
            print(f"[WARN] Failed to scan ports on {host}.")
            print(result.stderr)
    except FileNotFoundError:
        print("[ERROR] Command not found: nmap")

def dns_lookup(host):
    """Perform a DNS lookup for a host."""
    try:
        result = subprocess.run(["nslookup", host], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[INFO] DNS lookup results for {host}:")
            print(result.stdout)
        else:
            print(f"[WARN] Failed to perform DNS lookup for {host}.")
            print(result.stderr)
    except FileNotFoundError:
        print("[ERROR] Command not found: nslookup")

def traceroute_host(host):
    """Perform a traceroute to a host."""
    try:
        result = subprocess.run(["traceroute", host], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[INFO] Traceroute results for {host}:")
            print(result.stdout)
        else:
            print(f"[WARN] Failed to perform traceroute to {host}.")
            print(result.stderr)
    except FileNotFoundError:
        print("[ERROR] Command not found: traceroute")

def main():
    parser = argparse.ArgumentParser(description="Network utilities: ping, latency, port scan, DNS, traceroute")
    parser.add_argument('-p', action='store_true', dest='ping', help='Ping the host')
    parser.add_argument('-l', action='store_true', dest='latency', help='Check latency to the host')
    parser.add_argument('-s', action='store_true', dest='scan', help='Scan common ports on the host')
    parser.add_argument('-d', action='store_true', dest='dns', help='Perform DNS lookup for the host')
    parser.add_argument('-t', action='store_true', dest='traceroute', help='Run traceroute to the host')
    parser.add_argument('-H', '--host', required=True, dest='host', help='Target host or domain')
    args = parser.parse_args()

    if not (args.ping or args.latency or args.scan or args.dns or args.traceroute):
        parser.error('At least one action flag is required: -p, -l, -s, -d, or -t')

    host = args.host
    if args.ping:
        ping_host(host)
    if args.latency:
        check_latency(host)
    if args.scan:
        scan_ports(host)
    if args.dns:
        dns_lookup(host)
    if args.traceroute:
        traceroute_host(host)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n[INFO] Interrupted by user')
        sys.exit(130)
