import subprocess

command = ["sudo", "python3", "main.py"]

for i in range(20):
    print(f"Running process {i + 1}...")
    subprocess.run(command)
    print(f"Process {i + 1} completed.")
