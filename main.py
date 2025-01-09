import os
import time
import psutil # type:ignore
import hashlib
import random
import hmac

try:
    from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetTemperature, nvmlShutdown # type:ignore
    nvmlInit()
    gpu_handle = nvmlDeviceGetHandleByIndex(0)
    gpu_temperature = nvmlDeviceGetTemperature(gpu_handle, 0)  # GPU temperature
    nvmlShutdown()
except:
    gpu_temperature = None  # Fallback if GPU metrics are unavailable

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
    metrics["current_time"] = time.time_ns()
    metrics["process_count"] = len(psutil.pids())
    metrics["system_load"] = os.getloadavg() if hasattr(os, "getloadavg") else None
    
    # Application Metrics
    metrics["current_process_memory"] = psutil.Process().memory_info().rss
    metrics["open_files"] = len(psutil.Process().open_files())
    
    # Combine Metrics for Hashing
    seed = hashlib.sha256(str(metrics).encode()).hexdigest()
    seed = hashlib.sha256(seed.encode()).hexdigest()
    metrics["hashed_metrics"] = seed
    
    return metrics["hashed_metrics"]

a = 1103515245
c = 12345
m = 2**31

def getRandom(seed, rounds, interMediate=None):
    if rounds == 0:
        return interMediate

    seed_int = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % m
    interMediate = interMediate if interMediate is not None else seed_int

    random_value = (a * interMediate + seed_int + c) % m
    new_seed = getEntropy()

    return getRandom(new_seed, rounds=rounds-1, interMediate=random_value)

seed = getEntropy()

random_ = getRandom(seed, 10)
print(random_)
