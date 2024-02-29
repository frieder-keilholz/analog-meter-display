import psutil
import urllib.request
import yaml.loader
import time
import logging

logging.basicConfig(filename='analog-meter.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s)')

meters = yaml.safe_load(open('meters.yml'))

def get_cpu_percent():
    return str(int(psutil.cpu_percent()))

def get_memory_percent():
    return str(int(psutil.virtual_memory().percent))

options = {
    'cpu-percent': get_cpu_percent,
    'memory-percent': get_memory_percent
}

last_color = 'none'
while True:
    for meter in meters['meters']:
        logging.debug(meter)
        #get corresponding metric function
        util = options[meter['metric']]()
        
        #set corresponding color
        util_color = 'none'
        for color in meter['color-thresholds']:
            if int(util) >= color['target']:
                util_color = color['color']
                break

        #send get request to server
        if util_color:
            url = "http://" + meter['ip']+":"+str(meter['port'])+"/util/"+util+"/color/"+util_color
        else:
            url = "http://" + meter['ip']+":"+str(meter['port'])+"/util/"+util
        logging.info(url)
        try:
            urllib.request.urlopen(url + "/" + util +"/", timeout=1)
        except TimeoutError as te:
            print("TimeoutError")
            logging.error(te)
        except urllib.error.URLError as urle:
            print("URLError")
            logging.error(urle)
        except Exception as e:
            print("Error {0}".format(e))
            logging.error(e)
    #await defined interval
    logging.debug('sleep for ' + str(meters['interval']) + ' seconds')
    time.sleep(meters['interval'])