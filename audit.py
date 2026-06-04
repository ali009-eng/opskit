import subprocess
import sys
import argparse
from datetime import datetime

VERSION = "1.0.0"

def run_cmd(cmd):
    """Run a shell command and return output. Exit cleanly if command not found."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and result.stderr:
            print(f"[WARN] {result.stderr.strip()}")
        return result.stdout
    except FileNotFoundError:
        print(f"[ERROR] Command not found: {cmd[0]}")
        sys.exit(1)

def get_disk_usage():
    """Show disk usage across all mounted filesystems."""
    print(f"=== Disk Usage ===")
    print(run_cmd(["df", "-h"]))

def get_top_processes():
    """Show top 10 processes by CPU and memory usage."""
    print("=== Top 10 Processes (CPU) ===")
    lines = run_cmd(["ps", "aux", "--sort=-%cpu"]).strip().split("\n")
    for line in lines[:11]:
        print(line)
    print()
    print("=== Top 10 Processes (Memory) ===")
    lines = run_cmd(["ps", "aux", "--sort=-%mem"]).strip().split("\n")
    for line in lines[:11]:
        print(line)
    print()

def get_open_ports():
    """Show all open and listening ports."""
    print("=== Open Ports ===")
    print(run_cmd(["ss", "-tulnp"]))

def get_logged_in_users():
    """Show currently logged in users."""
    print("=== Logged In Users ===")
    print(run_cmd(["who"]))

def get_uptime():
    """Show system uptime and load average."""
    print("=== Uptime ===")
    print(run_cmd(["uptime", "-p"]))
    print(run_cmd(["cat", "/proc/loadavg"]))

def save_output(args):
    """Re-run audit and save output to a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_{timestamp}.txt"
    import io
    from contextlib import redirect_stdout
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        print(f"opskit audit report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        if args.a or args.d: get_disk_usage()
        if args.a or args.t: get_top_processes()
        if args.a or args.p: get_open_ports()
        if args.a or args.u: get_logged_in_users()
        if args.a or args.U: get_uptime()
    with open(filename, "w") as f:
        f.write(buffer.getvalue())
    print(f"[OK] Report saved to {filename}")

def main():
    parser = argparse.ArgumentParser(
        prog="audit",
        description="opskit audit — system inspection tool"
    )
    parser.add_argument("-d", action="store_true", help="Disk usage")
    parser.add_argument("-t", action="store_true", help="Top processes (CPU + memory)")
    parser.add_argument("-p", action="store_true", help="Open ports")
    parser.add_argument("-u", action="store_true", help="Logged in users")
    parser.add_argument("-U", action="store_true", help="Uptime and load average")
    parser.add_argument("-a", action="store_true", help="Run all checks")
    parser.add_argument("-o", action="store_true", help="Save output to file")
    parser.add_argument("--version", action="version", version=f"audit {VERSION}")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)

    if args.o:
        save_output(args)
        return

    print(f"[audit] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if args.a or args.d: get_disk_usage()
    if args.a or args.t: get_top_processes()
    if args.a or args.p: get_open_ports()
    if args.a or args.u: get_logged_in_users()
    if args.a or args.U: get_uptime()

if __name__ == "__main__":
    main()