import psutil
import urllib.request

while True:
    #get cpu usage in percent over 0.5 seconds
    util = str(int(psutil.cpu_percent(0.5)))
    print(util)
    #send get request to server
    urllib.request.urlopen("http://192.168.178.172:80/util/" + util +"/")