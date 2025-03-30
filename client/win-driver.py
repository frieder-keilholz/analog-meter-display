import gpustat
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

def get_gpu_percent():
    gpu_stats = gpustat.GPUStatCollection.new_query()
    return gpu_stats.gpus[0].utilization

def get_color_gradient(color_thresholds, util):
    color_thresholds = sorted(color_thresholds, key=lambda x: x['target'])
    if util <= color_thresholds[0]['target']:
        return color_thresholds[0]['color']
    if util >= color_thresholds[-1]['target']:
        return color_thresholds[-1]['color']

    for i in range(len(color_thresholds) - 1):
        low, high = color_thresholds[i], color_thresholds[i + 1]
        if low['target'] <= util <= high['target']:
            frac = (util - low['target']) / float(high['target'] - low['target'])
            return tuple(
                int(low['color'][c] + frac * (high['color'][c] - low['color'][c])) 
                for c in range(3)
            )

def get_color_thresholds(color_thresholds, util):
    for threshold in color_thresholds:
        if util <= threshold['target']:
            return threshold['color']
    return color_thresholds[-1]['color']

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
        if 'color-thresholds' in meter:
            util_color = get_color_thresholds(meter['color-thresholds'], int(util))
        elif 'color-gradient' in meter:
            util_color = get_color_gradient(meter['color-gradient'], int(util))

        #build and send GET request to server
        if util_color != 'none':
            url = "http://" + meter['ip']+":"+str(meter['port'])+"/util/"+util+"/color/r/"+str(util_color[0])+"/g/"+str(util_color[1])+"/b/"+str(util_color[2])
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