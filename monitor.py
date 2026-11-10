import time
import shutil
import os 
import socket

def get_memory_usage():
    with open("/proc/meminfo", 'r') as f:
        values = {"MemTotal":-1, "MemAvailable":-1}
        for line in f:
            if (line.startswith(("MemTotal", "MemAvailable"))):
                values[line.split()[0][:-1]] = int(line.split()[1])
    
    return ((values["MemTotal"] - values["MemAvailable"]) / values["MemTotal"]) * 100

def loop_through_cpuinfo(workTime, idleTime, line):
    for index, value in enumerate(line[1:9]):
        value = int(value)

        if index in (3, 4):
            idleTime += value
        else:
            workTime += value

    return [workTime, idleTime]

def read_cpu_times():
    with open("/proc/stat") as f:
        line = f.readline().split()

    initialWorkTime = 0
    initialIdleTime = 0
    
    result =  loop_through_cpuinfo(initialWorkTime, initialIdleTime, line)
    initialWorkTime = result[0]
    initialIdleTime = result[1]
    
    time.sleep(1)

    with open("/proc/stat") as f:
        line = f.readline().split()

    postWorkTime = 0
    postIdleTime = 0
    
    result =  loop_through_cpuinfo(postWorkTime, postIdleTime, line)
    postWorkTime = result[0]
    postIdleTime = result[1]
    
    initialTotalTime = initialWorkTime + initialIdleTime
    postTotalTime = postWorkTime + postIdleTime
    
    return (1 - ((postIdleTime - initialIdleTime) / (postTotalTime - initialTotalTime))) * 100



def get_disk_usage():
    total, used, free = shutil.disk_usage("/")

    return used / (used + free) * 100


import http.client

def check_service(host, port, path="/"):
    connection = http.client.HTTPConnection(
        host, port, timeout=2
    )

    try:
        connection.request("GET", path)
        response = connection.getresponse()

        if 200 <= response.status < 300:
            return "ONLINE"
        else:
            return "UNHEALTHY"

    except (OSError, http.client.HTTPException):
        return "OFFLINE"

    finally:
        connection.close()


while True:

    try:
        os.system("clear")

        print("========== LINUX SERVICE MONITOR ==========")
        print(f"Memory usage: {get_memory_usage():.2f}%")
        print(f"CPU usage: {read_cpu_times():.2f}%")
        print(f"Disk usage: {get_disk_usage():.2f}%")
        print("\n")
      
        status = check_service("localhost", 8080)

        print("Service:\tlocalhost:8080")
        print(f"Status:\t\t{status}")
            
        print("===========================================")


        time.sleep(2)

        

    except KeyboardInterrupt:
        print("Exiting program...")
        break




        