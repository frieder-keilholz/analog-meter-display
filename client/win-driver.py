import gpustat
import psutil
import urllib.request
import yaml.loader
import time
import logging

logging.basicConfig(filename='analog-meter.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s)')

meters = yaml.safe_load(open('client/meters.yml'))

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

def get_color_gradient(color_thresholds, util):
    color_thresholds = sorted(color_thresholds, key=lambda x: x['target-value'])
    if util <= color_thresholds[0]['target-value']:
        return color_thresholds[0]['color']
    if util >= color_thresholds[-1]['target-value']:
        return color_thresholds[-1]['color']

    for i in range(len(color_thresholds) - 1):
        low, high = color_thresholds[i], color_thresholds[i + 1]
        if low['target-value'] <= util <= high['target-value']:
            frac = (util - low['target-value']) / float(high['target-value'] - low['target-value'])
            return tuple(
                int(low['color'][c] + frac * (high['color'][c] - low['color'][c])) 
                for c in range(3)
            )

def get_color_thresholds(color_thresholds, util):
    for threshold in color_thresholds:
        if util <= threshold['target-value']:
            return threshold['color']
    return color_thresholds[-1]['color']

#normalizes color values to be always tree characters. EX: 97 --> 097 or 2 --> 002
def get_normalized_color_valus(color_values):
    normalized_color_valus_string =""
    for color in color_values:
        color_value_string = str(color)
        while (len(color_value_string) <3):
            color_value_string = '0' + color_value_string 
        normalized_color_valus_string = normalized_color_valus_string + color_value_string
    return normalized_color_valus_string

#normalizes util values to be always two characters. EX: 6 --> 02      
def get_normalized_util(util):
    if (len(util)<2):
        util = '0' + util
    return util

options = {
    'cpu-percent': get_cpu_percent,
    'cpu-temp': get_cpu_temp,
    'memory-percent': get_memory_percent,
    'gpu-percent': get_gpu_percent,
    'gpu-temp': get_gpu_temp,
    'video-memory-percent':get_video_memory
}

while True:
    data_string = ""
    for meter in meters['meters']:
        logging.debug(meter)
        #print(meter)
        #Add target number for analog meter
        data_string = data_string + "/A" + str(meter['analog-target'])
        #Add util value
        util = options[meter['metric']]()
        data_string = data_string + "/U" + get_normalized_util(util)
        #Add color values
        if 'color-thresholds' in meter:
            data_string = data_string + "/C" + get_normalized_color_valus(get_color_thresholds(meter['color-thresholds'], int(util)))
        elif 'color-gradient' in meter:
            data_string = data_string + "/C" + get_normalized_color_valus(get_color_gradient(meter['color-gradient'], int(util)))
        
    #await defined interval
    #print(data_string)
    #build and send GET request to server
    url = "http://" + meters['ip']+":"+str(meters['port'])+ data_string
    print(url)
    try:
        urllib.request.urlopen(url , timeout=1)
    except TimeoutError as te:
        print("TimeoutError")
        logging.error(te)
    except urllib.error.URLError as urle:
        print("URLError")
        logging.error(urle)
    except Exception as e:
        print("Error {0}".format(e))
        logging.error(e)
    logging.debug('sleep for ' + str(meters['interval']) + ' seconds')
    time.sleep(meters['interval'])

#old com logic
"""
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
            url = "http://" + meter['ip']+":"+str(meter['port'])+"/util/"+util+"/target/"+str(meter['analog-target'])+"/color/r/"+str(util_color[0])+"/g/"+str(util_color[1])+"/b/"+str(util_color[2])
            print(url)
        else:
            url = "http://" + meter['ip']+":"+str(meter['port'])+"/util/"+util+"/target/"+str(meter['analog-target'])
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
        """