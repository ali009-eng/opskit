#!/usr/bin/env python3
import json
import os
import subprocess
import argparse

def collect_data(services):
    data = {}
    data["disk"] = subprocess.run(["df", "-h"], capture_output=True, text=True).stdout
    data["memory"] = subprocess.run(["free", "-h"], capture_output=True, text=True).stdout
    data["processes"] = subprocess.run(["ps", "aux"], capture_output=True, text=True).stdout
    data["services"] = {}
    for svc in services:
        result = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True)
        data["services"][svc] = result.stdout.strip()
    return data

def generate_html(data):
    html = "<html><head><title>System Report</title></head><body>"
    html += "<h1>System Report</h1>"
    html += "<h2>Disk Usage</h2><pre>{}</pre>".format(data["disk"])
    html += "<h2>Memory Usage</h2><pre>{}</pre>".format(data["memory"])
    html += "<h2>Running Processes</h2><pre>{}</pre>".format(data["processes"])
    html += "<h2>Service Status</h2><ul>"
    for svc, status in data["services"].items():
        html += "<li>{}: {}</li>".format(svc, status)
    html += "</ul></body></html>"
    return html

def generate_json(data):
    return json.dumps(data, indent=4)

def save_report(content, filename):
    with open(filename, "w") as f:
        f.write(content)
    print(f"Report saved to {filename}")

def send_report_email(email, subject, body, attachment_path=None):
    if not email:
        return
    if attachment_path:
        command = ["mail", "-s", subject, "-a", attachment_path, email]
        message = "Please see the attached report.\n"
    else:
        command = ["mail", "-s", subject, email]
        message = body
    try:
        subprocess.run(command, input=message, text=True, check=True)
        print(f"Email sent to {email}")
    except FileNotFoundError:
        print("Warning: mail command not found; unable to send email.")
    except subprocess.CalledProcessError:
        print(f"Warning: failed to send email to {email}")

def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a system report.")
    parser.add_argument("--services", required=True, help="Comma-separated list of services to check")
    parser.add_argument("--html", help="Output filename for HTML report")
    parser.add_argument("--json", help="Output filename for JSON report")
    parser.add_argument("--email", help="Email address to send the report to")
    args = parser.parse_args(argv)

    services = [svc.strip() for svc in args.services.split(",") if svc.strip()]
    data = collect_data(services)

    if not args.html and not args.json:
        parser.error("At least one of --html or --json must be provided.")

    html_path = None
    json_path = None

    if args.html:
        save_report(generate_html(data), args.html)
        html_path = args.html

    if args.json:
        save_report(generate_json(data), args.json)
        json_path = args.json

    if args.email:
        subject = "System Report"
        send_report_email(args.email, subject, "", attachment_path=html_path or json_path)

if __name__ == "__main__":
    main()
