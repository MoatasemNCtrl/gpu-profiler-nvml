from pynvml import *


try: 
    nvmlInit()
    print("NVML intialized")



    Driver = nvmlSystemGetDriverVersion()



    for i in range(nvmlDeviceGetCount()):
        handle = nvmlDeviceGetHandleByIndex(i)
        name = nvmlDeviceGetName(handle)
        uuid = nvmlDeviceGetUUID(handle)
        memory = nvmlDeviceGetMemoryInfo(handle)
        used = memory.used / 1048576.0
        total = memory.total / 1048576.0

        try:
            power = nvmlDeviceGetPowerUsage(handle) / 1000
        except NVMLError:
            print("NVML_ERROR_NOT_SUPPORTED")
            power = None
            
        try: 
            temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
        except NVMLError:
            print("NVML_ERROR_NOT_SUPPORTED")
            temp = None 


        print(f"[GPU {i}] {name}")
        print(f"UUID           : {uuid}")
        print(f"Driver Version : {Driver}")
        print(f"Memory Usage   : {used} / {total} MB")
        print(f"Power          : {power} W")
        print(f"Temp           : {temp} C")


except NVMLError:
    print("ERROR: NVML failed to initialize. Is the NVIDIA driver installed?")

finally:
    try: nvmlShutdown()
    except Exception: pass

