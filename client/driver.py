import platform
from tokenize import String
import urllib.request
import time
import logging

import yaml

from dataGathererLnx import get_sys_data_lnx
from dataGathererWin import get_sys_data_win
import signal
import sys

logging.basicConfig(filename='analog-meter.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s)')

meters = yaml.safe_load(open('client/meters.yml'))
options = []

def handle_shutdown(signum, frame):
    url = "http://" + meters['ip']+":"+str(meters['port'])+ "/A0/U00/C000000000/A1/U00/C000000000/A2/U00/C000000000/A3/U00/C000000000/A4/U00/C000000000/A5/U00/C000000000/"
    sendRequest(url)
    sys.exit(0)

def init_options():
    for meter in meters['meters']:
        options.append(meter['metric'])
    print("Options initialized:", options)

def get_sys_data(options):
    if platform.system() == "Windows":
        return get_sys_data_win(options)
    else:
        return get_sys_data_lnx(options)

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

init_options()

def sendRequest(url: String):
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

signal.signal(signal.SIGINT, handle_shutdown)   # z.B. Strg+C
signal.signal(signal.SIGTERM, handle_shutdown)  # z.B. Shutdown/kill

#the main loop
while True:
    #get system data
    try:
        sys_data = get_sys_data(options)
    except Exception as e:
        print("Error getting system data: ", e)
        break

    #print(sys_data)
    data_string = ""
    for meter in meters['meters']:
        logging.debug(meter)
        #print(meter)
        #Add target number for analog meter
        data_string = data_string + "/A" + str(meter['analog-target'])
        #Add util value
        util = sys_data.get(meter['metric'])
        if isinstance(util, float):
            util = int(util)
        data_string = data_string + "/U" + get_normalized_util(str(util))
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
    sendRequest(url)

