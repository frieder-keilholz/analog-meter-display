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
    if dataDict:
        return dataDict
    else:
        raise Exception("Cannot retrieve system data")

def get_cpu_percent():
    return str(int(psutil.cpu_percent()))

def get_cpu_temp():
    #print("iny")
    return '0'

def get_memory_percent():
    return str(int(psutil.virtual_memory().percent))

def get_gpu_percent():
    gpu_stats = gpustat.GPUStatCollection.new_query()
    return str(gpu_stats.gpus[0].utilization)

def get_gpu_temp():
    #print("iny")
    return '0'

def get_video_memory():
    #print("iny")
    return '0'