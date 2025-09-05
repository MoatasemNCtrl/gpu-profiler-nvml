#imports 
from pynvml import *
import sys



class nvml_context:
    def __init__(self):

        self.initialized = False
        pass

    def __enter__(self):

            nvmlInit()
            self.initialized = True
            return None 
            
        

    def __exit__(self, exc_type, exc_value, traceback):
        if self.initialized:
            nvmlShutdown()

        return False


def safe_call(fn, *args, default=None):
    try: 
        return fn(*args)
    except NVMLError:
        return default  
    




#static data collection, relevant for variables that don't change (usually)
#it returns a dictionary 



def get_device_static(i: int):
    handle = nvmlDeviceGetHandleByIndex(i)

    return {
        "index": i,
        "name": nvmlDeviceGetName(handle),
        "uuid": nvmlDeviceGetUUID(handle),
        "pci_bus_id": nvmlDeviceGetPciInfo(handle).busId,
        "driver_version": nvmlSystemGetDriverVersion(),
        "vbios_version": nvmlDeviceGetVbiosVersion(handle),
        "memory_total_mb": nvmlDeviceGetMemoryInfo(handle).total // 1048576,
        
        "ecc_mode": nvmlDeviceGetEccMode(handle)[0],  # Returns tuple (current, pending)
    }

# memory_used_mb (int)
# memory_free_mb (int)
# temperature_gpu_c (int or None)
# power_usage_w (float or None)
# sm_clock_mhz (int or None)

def get_device_dynamic(i: int):
    handle = nvmlDeviceGetHandleByIndex(i)

    return {

        "memory_used_mb": nvmlDeviceGetMemoryInfo(handle).used // 1048576,
        "memory_free_mb": nvmlDeviceGetMemoryInfo(handle).free // 1048576,
        "temp": nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU),
        "power": nvmlDeviceGetPowerUsage(handle) / 1000,
        "sm_clock_mhz": nvmlDeviceGetClockInfo(handle, NVML_CLOCK_SM)
        
    }


# row assembler inc 

def make_row(i: int, fields: list[str]):
    

        



         



try:
    with nvml_context():
        # Your NVML-dependent logic here
        ...
except NVMLError:
    print("nvml unavailable", file=sys.stderr)
    sys.exit(2)













#main scripture
# try:
#     # Validate args (→ exit 3 if invalid)
#     # Use `with nvml_context():` 
#     #   → Collect fields, safe_call, assemble rows, render output
#     sys.exit(0)  # Success
# except KnownNVMLInitErrors:
#     print("NVML unavailable", file=sys.stderr)
#     sys.exit(2)
# except InvalidFieldError:
#     print("Invalid field in --fields", file=sys.stderr)
#     sys.exit(3)
# except Exception as e:
#     print("Unexpected error:", str(e), file=sys.stderr)
#     sys.exit(1)




        # except NVMLError: 
        #     sys.stderr.write("nvml unavailable\n")
        #     sys.exit(2)