import git
import os
import subprocess
import paramiko
import time
import argparse

def get_latest_code(computer_path, branch="main"):
    # git.Repo requires the local directory path, not the remote URL
    repo = git.Repo(computer_path)
    repo.git.checkout(branch)
    repo.remotes.origin.pull()
    print(f"Checked out latest code from {branch} branch in {computer_path}.")

def download_code(github_path, computer_path, branch="main"):
    if not os.path.exists(computer_path):
        git.Repo.clone_from(github_path, computer_path, branch=branch)
        print(f"Cloned repository from {github_path} to {computer_path}.")
    else:
        print(f"Directory {computer_path} already exists. Pulling latest changes.")
        # Fixed: Now only passing the expected 2 arguments
        get_latest_code(computer_path, branch)

def code_handler(github_path, computer_path, branch="main"):
    if os.path.exists(computer_path):
        # Fixed: Passing the local path instead of the remote URL
        get_latest_code(computer_path, branch)
    else:
        download_code(github_path, computer_path, branch)


def restart_systemd(service_name):
    """Restart a systemd service."""
    try:
        subprocess.run(["systemctl", "restart", service_name], check=True)
        print(f"Restarted {service_name} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart {service_name}: {e}")
    

def set_up_ssh_connection(username, path_to_key, ip_address, port=22):
    """Set up an SSH connection using Paramiko."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip_address, port=port, username=username, key_filename=path_to_key)
        print(f"SSH connection established to {ip_address}:{port} as {username}.")
        return ssh
    except Exception as e:
        print(f"Failed to establish SSH connection: {e}")
        return None


def execute_remote_command(ssh, command):
    """Execute a command on the remote server via SSH."""
    try:
        
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output and error == "":
            
            print(f"Command output: {output}")
            return True, output, exit_status
        if error != "":
            print(f"Command error: {error}")
            return False, "", exit_status
        
    except Exception as e:
        print(f"Failed to execute remote command: {e}")
        return False, "", 1

def main():
    parser = argparse.ArgumentParser(description="Deploy code from GitHub to a remote server and restart a systemd service.")
    parser.add_argument("--github-path", required=True, help="URL of the GitHub repository to deploy.")
    parser.add_argument("--computer-path", required=True, help="Local path where the code will be deployed.")
    parser.add_argument("--branch", default="main", help="Git branch to deploy (default: main).")
    parser.add_argument("--username", required=False, default=None, help="Username for SSH connection.")
    parser.add_argument("--key-path", required=False, default=None, help="Path to the SSH private key.")
    parser.add_argument("--ip-address", required=False, default=None, help="IP address of the remote server.")
    parser.add_argument("--port", type=int, default=22, help="Port for SSH connection (default: 22).")
    parser.add_argument("--service-name", required=True, help="Name of the systemd service to restart.")
    args = parser.parse_args()

    if args.ip_address:
        ssh = set_up_ssh_connection(args.username, args.key_path, args.ip_address, args.port)
        if ssh:
            success, output, exit_status = execute_remote_command(ssh, f"cd {args.computer_path} && git pull origin {args.branch}")
            if success:
                print("Code updated successfully on the remote server.")
                execute_remote_command(ssh, f"sudo systemctl restart {args.service_name}")
            else:
                print("Failed to update code on the remote server.")
            ssh.close()
        else:
            print("Could not establish SSH connection. Aborting.")
    else:
        code_handler(args.github_path, args.computer_path, args.branch)
        restart_systemd(args.service_name)