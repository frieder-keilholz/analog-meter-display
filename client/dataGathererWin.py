import wmi
import time

def get_sys_data_win(options):
    start_time = time.time()
    w = wmi.WMI(namespace="root/LibreHardwareMonitor")
    dataDict = {}
    sys_sensors = w.Sensor()
    sensor_count = len(options)
    #end_time = time.time()  # Endzeit erfassen
    #print(f"collecting sensors Dauer: {end_time - start_time:.4f} Sekunden")
    for sensor in sys_sensors:
        if 'cpu-percent' in options and sensor.SensorType == u'Load' and 'CPU Total' == sensor.Name:
            dataDict['cpu-percent'] = sensor.Value
            sensor_count -= 1
        if 'memory-percent' in options and sensor.SensorType == u'Load' and 'Memory' == sensor.Name:
            dataDict['memory-percent'] = sensor.Value
            sensor_count -= 1
        if 'cpu-temp' in options and sensor.SensorType == u'Temperature' and 'CPU Package' == sensor.Name:
            dataDict['cpu-temp'] = sensor.Value
            sensor_count -= 1
        if 'gpu-percent' in options and sensor.SensorType == u'Load' and 'GPU Core' == sensor.Name:
            dataDict['gpu-percent'] = sensor.Value
            sensor_count -= 1
        if 'gpu-temp' in options and sensor.SensorType == u'Temperature' and 'GPU Core' == sensor.Name:
            dataDict['gpu-temp'] = sensor.Value
        if 'video-memory-percent' in options and sensor.SensorType == u'Load' and 'GPU Memory' == sensor.Name:
            dataDict['video-memory-percent'] = sensor.Value
            sensor_count -= 1
        if sensor_count == 0:
            break
    #end_time = time.time()  # Endzeit erfassen
    #print(f"get_sys_data_win Dauer: {end_time - start_time:.4f} Sekunden")  # Dauer ausgeben
    if dataDict:
        return dataDict
    else:
        raise Exception("LibreHardwareMonitor not running! Please launch it!") 