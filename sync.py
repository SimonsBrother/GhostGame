import subprocess

pi_ip = "192.168.1.31"
source_dir = "/Users/calebhair/Documents/Projects/GhostGame"
target_dir = "/home/caleb/Documents"

command = f'rsync -azP -e ssh "{source_dir}" caleb@{pi_ip}:"{target_dir}"'
print(command)
print(subprocess.Popen(command, shell=True))
