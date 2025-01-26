# type: ignore

import os
import time
import psutil
import hashlib
import random
import hmac
import secrets
from datetime import datetime

import threading

try:
    from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetTemperature, nvmlShutdown # type:ignore
    nvmlInit()
    gpu_handle = nvmlDeviceGetHandleByIndex(0)
    gpu_temperature = nvmlDeviceGetTemperature(gpu_handle, 0)  # GPU temperature
    nvmlShutdown()
except:
    gpu_temperature = None  # Fallback if GPU metrics are unavailable

def get_process_entropy():
    processes = psutil.process_iter(attrs=['pid', 'name', 'status', 'cpu_percent', 'memory_info'])
    
    entropy_data = []
    
    for proc in processes:
        try:
            proc_info = str(proc.info)
            entropy_data.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return ''.join(entropy_data)

def getEntropy():
    # Hardware Metrics
    metrics = {}
    
    # CPU Metrics
    metrics["cpu_temp"] = random.randint(30, 90)  # Simulated as an example
    metrics["cpu_load"] = psutil.cpu_percent(interval=0.1)
    metrics["cpu_count"] = psutil.cpu_count()
    metrics["cpu_freq"] = psutil.cpu_freq().current if psutil.cpu_freq() else None
    
    # Memory Metrics
    memory_info = psutil.virtual_memory()
    metrics["memory_used"] = memory_info.used
    metrics["memory_available"] = memory_info.available
    metrics["swap_used"] = psutil.swap_memory().used
    
    # Disk Metrics
    disk_usage = psutil.disk_usage('/')
    metrics["disk_used"] = disk_usage.used
    metrics["disk_free"] = disk_usage.free
    metrics["disk_io"] = psutil.disk_io_counters().read_bytes + psutil.disk_io_counters().write_bytes
    
    # Network Metrics
    net_io = psutil.net_io_counters()
    metrics["net_sent"] = net_io.bytes_sent
    metrics["net_recv"] = net_io.bytes_recv
    metrics["connections"] = len(psutil.net_connections(kind='tcp'))
    metrics["net_latency"] = random.randint(1, 100)  # Simulate latency variability
    
    # Power Metrics
    if hasattr(psutil, "sensors_battery") and psutil.sensors_battery():
        battery = psutil.sensors_battery()
        metrics["battery_percent"] = battery.percent if battery else None
        metrics["power_plugged"] = battery.power_plugged if battery else None
    else:
        metrics["battery_percent"] = None
        metrics["power_plugged"] = None
    
    # GPU Metrics (if available)
    metrics["gpu_temp"] = gpu_temperature
    
    # System Metrics
    metrics["uptime"] = time.time() - psutil.boot_time()
    metrics["current_time"] = datetime.now().isoformat()
    metrics["process_count"] = len(psutil.pids())
    metrics["system_load"] = os.getloadavg() if hasattr(os, "getloadavg") else None
    
    # Random Hardware Events
    metrics["hardware_entropy"] = secrets.token_bytes(32).hex()
    metrics["processes"] = get_process_entropy()
    
    # Combine Metrics for Hashing
    combined_data = ''.join(str(value) for value in metrics.values())
    seed = hashlib.sha512(combined_data.encode()).hexdigest()
    metrics["hashed_metrics"] = seed
    
    return metrics["hashed_metrics"]

def getSeed(entropy):
    nonce = os.urandom(32).hex()

    seed = entropy + nonce
    return seed

def getRandom(seed, rounds, intermediate=None):
    if rounds == 0:
        return intermediate

    k = bytes([1] * 32)
    v = intermediate if intermediate is not None else bytes([0] * 32)

    k = hmac.new(k, (v + bytes([0]) + bytes(seed.encode())), hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()

    output = hmac.new(k, v, hashlib.sha256)
    v = output.digest()

    new_seed = getSeed(getEntropy())
    return getRandom(new_seed, rounds-1, v)

def generate(count):
    print(count)
    with open("random_bits_unmod.bin", "ab") as f:
        seed = getSeed(getEntropy())
        random_value = getRandom(seed, 10)
        sha256_hash = hashlib.sha256(random_value).digest()
        f.write(sha256_hash)


threads = []
for i in range(500):
    thread = threading.Thread(target=lambda: generate(i+1))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
