import pdf2docx
import json
import os
import subprocess




def collect_data(service):

    data = {}
    
    # Collect disk and memory info
    disk_result = subprocess.run(["df", "-h"], capture_output=True, text=True)
    memory_result = subprocess.run(["free", "-h"], capture_output=True, text=True)
    processes_result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    
    # Assign to data dict
    data["disk"] = disk_result.stdout
    data["memory"] = memory_result.stdout
    data["processes"] = processes_result.stdout
    
    # Check each service in the service list
    data["services"] = {}
    for svc in service:
        result = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True)
        data["services"][svc] = result.stdout.strip()
    
    return data