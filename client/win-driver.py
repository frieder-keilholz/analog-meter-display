import psutil
import urllib.request
import yaml.loader
import time
import logging

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
        logging.debug(meter)
        #get corresponding metric function
        util = options[meter['metric']]()
        
        #send get request to server
        url = "http://" + meter['ip']+":"+str(meter['port'])+"/util"
        logging.info(url)
        try:
            urllib.request.urlopen(url + "/" + util +"/", timeout=0.5)
        except TimeoutError as te:
            print("TimeoutError")
            logging.error(te)
        except urllib.error.URLError as urle:
            print("URLError")
            logging.error(urle)
    #await defined interval
    logging.debug('sleep for ' + str(meters['interval']) + ' seconds')
    time.sleep(meters['interval'])