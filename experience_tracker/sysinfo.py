import psutil
import cpuinfo
import socket


def get_cpu_info():
    info = cpuinfo.get_cpu_info()
    return info['count'], info['brand'], info['vendor_id']


def get_gpu_info():
    try:
        import torch

        count = torch.cuda.device_count()
        return [(i, torch.cuda.get_device_name(i)) for i in range(0, count)]
    except:
        return []


def get_hostname():
    return socket.gethostname()


def get_memory_info():
    mem = psutil.virtual_memory()
    return mem.available, mem.total

