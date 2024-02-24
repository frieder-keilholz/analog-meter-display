import psutil
import urllib.request
import yaml.loader
import time

meters = yaml.safe_load(open('meters.yml'))

def get_cpu_percent():
    return str(int(psutil.cpu_percent()))

def get_memory_percent():
    return str(int(psutil.virtual_memory().percent))

options = {
    'cpu-percent': get_cpu_percent,
    'memory-percent': get_memory_percent
}

while True:
    for meter in meters['meters']:
        #get corresponding metric function
        util = options[meter['metric']]()
        
        #send get request to server
        url = "http://" + meter['ip']+":"+str(meter['port'])+"/util"
        print(url)
        try:
            urllib.request.urlopen(url + "/" + util +"/", timeout=0.5)
        except TimeoutError:
            print("TimeoutError")
        except urllib.error.URLError:
            print("URLError")
    #await defined interval
    time.sleep(meters['interval'])