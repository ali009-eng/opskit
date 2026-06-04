



import os
import subprocess
import argparse
import time

from pendulum import datetime




def is_service_running(service_name):
    result = subprocess.run(
        ["systemctl", "is-active", service_name],
        capture_output=True,
        text=True
    )

    return result.stdout.strip() == "active"

def restart_service(service_name):
    try:
        subprocess.run(["systemctl", "restart", service_name], check=True)
        print(f"Restarted {service_name} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart {service_name}: {e}")

def log_incident(service_name, event):
    with open("/var/log/opskit_incidents.log", "a") as f:
        f.write(f"{datetime.now()} {service_name}: {event}\n")

def show_history(service_name):
    log_path = "/var/log/opskit_incidents.log"
    if not os.path.exists(log_path):
        print("No incident history found.")
        return
    with open(log_path, "r") as f:
        lines = [line for line in f.readlines() if service_name in line]
    if not lines:
        print(f"No incidents logged for {service_name}.")
        return
    print(f"Incident History for {service_name}:")
    for line in lines[-10:]:
        print(line.strip())

def show_watch(service_name, interval=60):
    print(f"Watching {service_name} every {interval} seconds. Press Ctrl+C to stop.")
    try:
        while True:
            if not is_service_running(service_name):
                print(f"[ALERT] {service_name} is down!")
                log_incident(service_name, "Service is down")
                restart_service(service_name)
            else:
                print(f"{service_name} is running.")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopped watching.")


def main():
    parser = argparse.ArgumentParser(description="Watch and manage a systemd service.")
    parser.add_argument("service", help="Name of the systemd service to monitor (e.g. sshd.service)")
    parser.add_argument("-i", "--interval", type=int, default=60, help="Polling interval in seconds for watching (default: 60)")
    parser.add_argument("--history", action="store_true", help="Show recent incident history for the service")
    parser.add_argument("--restart", action="store_true", help="Attempt to restart the service once")
    parser.add_argument("--status", action="store_true", help="Show current service status")
    parser.add_argument("--watch", action="store_true", help="Continuously watch the service (default if no action provided)")

    args = parser.parse_args()

    svc = args.service

    if args.history:
        show_history(svc)
        return

    if args.status:
        running = is_service_running(svc)
        print(f"{svc} is {'running' if running else 'stopped'}.")
        return

    if args.restart:
        restart_service(svc)
        return

    # Default behaviour: watch continuously (or when --watch specified)
    if args.watch or (not args.history and not args.restart and not args.status):
        show_watch(svc, interval=args.interval)


if __name__ == "__main__":
    main()
