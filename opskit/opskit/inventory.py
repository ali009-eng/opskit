#!/usr/bin/env python3
import subprocess
import argparse
import json
import sys

def scan_subnet(subnet):
    ips = []
    try:
        result = subprocess.run(["nmap", "-sn", subnet], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "Nmap scan report for" in line:
                parts = line.split()
                if len(parts) >= 5:
                    ips.append(parts[4])
        if result.returncode != 0:
            print(f"[WARN] Failed to scan subnet {subnet}.")
    except FileNotFoundError:
        print("[ERROR] Command not found: nmap")
    return ips

def scan_host_ports(host):
    ports = []
    try:
        result = subprocess.run(["nmap", "-F", host], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "/tcp" in line and "open" in line:
                    parts = line.split()
                    if parts:
                        ports.append(parts[0])
        else:
            print(f"[WARN] Failed to scan ports on {host}.")
    except FileNotFoundError:
        print("[ERROR] Command not found: nmap")
    return ports

def build_inventory(subnet):
    inventory = {}
    hosts = scan_subnet(subnet)
    for host in hosts:
        ports = scan_host_ports(host)
        inventory[host] = ports
    return inventory

def export_inventory(inventory, filename):
    import csv
    try:
        if filename.endswith(".csv"):
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["host", "ports"])
                for host, ports in inventory.items():
                    ports_str = ";".join(map(str, ports)) if isinstance(ports, (list, tuple)) else str(ports)
                    writer.writerow([host, ports_str])
            print(f"[INFO] Inventory exported to {filename} (CSV).")
        else:
            with open(filename, "w") as f:
                json.dump(inventory, f, indent=2)
            print(f"[INFO] Inventory exported to {filename} (JSON).")
    except OSError as e:
        print(f"[ERROR] Failed to export: {e}")

def main():
    parser = argparse.ArgumentParser(description="Inventory utilities: scan subnet or host and optionally export results")
    parser.add_argument('--subnet', help='Subnet to scan, e.g. 192.168.1.0/24')
    parser.add_argument('--host', help="Scan a single host's ports")
    parser.add_argument('--export', help='Filename to export results to (CSV or JSON)')
    args = parser.parse_args()

    if not (args.subnet or args.host):
        parser.error('At least one of --subnet or --host is required.')

    results = {}
    if args.subnet:
        results = build_inventory(args.subnet)
        if not args.export:
            print(json.dumps(results, indent=2))

    if args.host:
        ports = scan_host_ports(args.host)
        if args.export:
            results[args.host] = ports
        else:
            print(json.dumps({args.host: ports}, indent=2))

    if args.export:
        try:
            export_inventory(results, args.export)
        except Exception as e:
            print(f"[ERROR] Export failed: {e}")
            sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n[INFO] Interrupted by user')
        sys.exit(130)
