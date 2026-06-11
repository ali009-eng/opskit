#!/usr/bin/env python3
import os
import subprocess
import argparse

def fetch_logs(name, syslog_path="/var/log/"):
    """Fetch logs from the specified log file."""
    path = syslog_path + name + ".log"
    if not os.path.exists(path):
        print(f"Log file not found at {path}.")
        return []
    with open(path, "r") as f:
        logs = f.readlines()
    return logs

def filter_logs(logs, levels=["ERROR", "WARNING"]):
    """Filter logs by severity level."""
    lines = []
    for log in logs:
        if any(level in log for level in levels):
            lines.append(log.strip())
    return lines

def count_logs(lines):
    """Count logs by severity level."""
    error_count = sum(1 for line in lines if "ERROR" in line)
    warning_count = sum(1 for line in lines if "WARNING" in line)
    return {"ERROR": error_count, "WARNING": warning_count}

def live_logs(name, syslog_path="/var/log/"):
    """Live stream logs from the specified log file."""
    path = syslog_path + name + ".log"
    if not os.path.exists(path):
        print(f"Log file not found at {path}.")
        return
    process = subprocess.Popen(["tail", "-f", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        print(line.strip())

def main():
    parser = argparse.ArgumentParser(description="Fetch and filter logs from log files.")
    parser.add_argument("-n", "--name", required=True, help="Name of the log file (without .log extension).")
    parser.add_argument("-p", "--syslog-path", default="/var/log/", help="Directory containing the log file.")
    parser.add_argument("-e", "--error-level", required=False, default="ERROR", help="Error level to filter.")
    parser.add_argument("-w", "--warning-level", required=False, default="WARNING", help="Warning level to filter.")
    parser.add_argument("-c", "--count", action="store_true", help="Count the number of logs.")
    parser.add_argument("-l", "--live", action="store_true", help="Live stream logs.")
    args = parser.parse_args()

    levels = []
    for level in (args.error_level, args.warning_level):
        if level:
            levels.append(level.strip().upper())
    levels = list(dict.fromkeys(levels))

    if args.live:
        live_logs(args.name, args.syslog_path)
    else:
        logs = fetch_logs(args.name, args.syslog_path)
        filtered_logs = filter_logs(logs, levels=levels)
        if args.count:
            print(f"Log counts: {count_logs(filtered_logs)}")
        else:
            for log in filtered_logs:
                print(log)

if __name__ == "__main__":
    main()
