import gpustat
import psutil

def get_sys_data_lnx(options):
    dataDict = {}
    if 'cpu-percent' in options:
        dataDict['cpu-percent'] = get_cpu_percent()
    if 'cpu-temp' in options:
        dataDict['cpu-temp'] = get_cpu_temp()
    if 'memory-percent' in options:
        dataDict['memory-percent'] = get_memory_percent()
    if 'gpu-percent' in options:
        dataDict['gpu-percent'] = get_gpu_percent()
    if 'gpu-temp' in options:
        dataDict['gpu-temp'] = get_gpu_temp()
    if 'video-memory-percent' in options:
        dataDict['video-memory-percent'] = get_video_memory()
    if 'incoming-data' in options:
        dataDict['incoming-data'] = get_incoming_data()
    if 'outgoing-data' in options:
        dataDict['outgoing-data'] = get_outgoing_data()
    if dataDict:
        return dataDict
    else:
        raise Exception("Cannot retrieve system data")

def get_cpu_percent():
    return str(int(psutil.cpu_percent()))

def get_cpu_temp():
    return str(int(psutil.sensors_temperatures()['coretemp'][0].current))

def get_memory_percent():
    return str(int(psutil.virtual_memory().percent))

def get_gpu_percent():
    gpu_stats = gpustat.GPUStatCollection.new_query()
    return str(gpu_stats.gpus[0].utilization)

def get_gpu_temp():
    gpu_stats = gpustat.GPUStatCollection.new_query()
    return str(gpu_stats.gpus[0].temperature)

def get_video_memory():
    gpu_stats = gpustat.GPUStatCollection.new_query()
    gpu_mem_percent = (gpu_stats.gpus[0].memory_used / gpu_stats.gpus[0].memory_total) * 100
    return str(int(gpu_mem_percent))

def get_incoming_data():
    return str(int(psutil.net_io_counters().bytes_recv / (1024 * 1024)))  # Convert to MB

def get_outgoing_data():
    return str(int(psutil.net_io_counters().bytes_sent / (1024 * 1024)))  # Convert to MB