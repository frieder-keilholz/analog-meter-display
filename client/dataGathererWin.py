import time
import json, requests

url = 'http://127.0.0.1:8085'

#TODO Initilizing methode to distinguish between intelcpu and amd cpu and to check if LibreHardwareMonitor is running, otherwise raise exception
#TODO also for gpus
cpuVendor = "/intelcpu"
gpuVendor = "/gpu-nvidia"

def get_sys_data_win(options):
    start_time = time.time()

    dataDict = {}
    #end_time = time.time()  # Endzeit erfassen
    #print(f"collecting sensors Dauer: {end_time - start_time:.4f} Sekunden")

    if 'cpu-percent' in options :
        params = dict(id=cpuVendor + "/0/load/0", action="Get")
        resp = requests.post(url=url + "/Sensor", params=params, timeout=1)
        data = json.loads(resp.text)
        dataDict['cpu-percent'] = data['value']
    if 'memory-percent' in options:
        params = dict(id="/ram/load/0", action="Get")
        resp = requests.post(url=url + "/Sensor", params=params, timeout=1)
        data = json.loads(resp.text)
        dataDict['memory-percent'] = data['value']
    if 'cpu-temp' in options:
        params = dict(id=cpuVendor + "/0/temperature/0", action="Get")
        resp = requests.post(url=url + "/Sensor", params=params, timeout=1)
        data = json.loads(resp.text)
        dataDict['cpu-temp'] = data['value']
    if 'gpu-percent' in options:
        params = dict(id=gpuVendor + "/0/load/0", action="Get")
        resp = requests.post(url=url + "/Sensor", params=params, timeout=1)
        data = json.loads(resp.text)
        dataDict['gpu-percent'] = data['value']
    if 'gpu-temp' in options:
        params = dict(id=gpuVendor + "/0/temperature/0", action="Get")
        resp = requests.post(url=url + "/Sensor", params=params, timeout=1)
        data = json.loads(resp.text)
        dataDict['gpu-temp'] = data['value']
    if 'video-memory-percent' in options:
        params = dict(id=gpuVendor + "/0/load/3", action="Get")
        resp = requests.post(url=url + "/Sensor", params=params, timeout=1)
        data = json.loads(resp.text)
        dataDict['video-memory-percent'] = data['value']

    #end_time = time.time()  # Endzeit erfassen
    #print(f"get_sys_data_win Dauer: {end_time - start_time:.4f} Sekunden")  # Dauer ausgeben
    if dataDict:
        return dataDict
    else:
        raise Exception("LibreHardwareMonitor not running! Please launch it!") 




def main():
    params = dict(id="/ram/load/0", action="Get")
    resp = requests.post(url=url + "/Sensor", params=params, timeout=1)
    data = json.loads(resp.text)
    #print(data)
    print(data['value'])


if __name__ == '__main__':
    main()