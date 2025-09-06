from pynvml import *
import sys
from tabulate import tabulate
import argparse


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
    


def _b2s(x):
    return x.decode() if isinstance(x, bytes) else x

def _bytes_to_mb(x):
    return x // 1048576 if isinstance(x, int) else None



def get_device_static(i: int):
    handle = nvmlDeviceGetHandleByIndex(i)

    pci = safe_call(nvmlDeviceGetPciInfo, handle)
    mem = safe_call(nvmlDeviceGetMemoryInfo, handle)
    ecc = safe_call(nvmlDeviceGetEccMode, handle)

    return {
        "index": i,
        "name": _b2s(safe_call(nvmlDeviceGetName, handle)),
        "uuid": _b2s(safe_call(nvmlDeviceGetUUID, handle)),
        "pci_bus_id": _b2s(getattr(pci, "busId", None)) if pci else None,
        "driver_version": _b2s(safe_call(nvmlSystemGetDriverVersion)),
        "vbios_version": _b2s(safe_call(nvmlDeviceGetVbiosVersion, handle)),
        "memory_total_mb": _bytes_to_mb(mem.total) if mem else None,
        "ecc_mode": (ecc[0] if isinstance(ecc, tuple) and len(ecc) > 0 else None),
    }

def get_device_dynamic(i: int):
    handle = nvmlDeviceGetHandleByIndex(i)

    mem = safe_call(nvmlDeviceGetMemoryInfo, handle)
    power_mw = safe_call(nvmlDeviceGetPowerUsage, handle)

    return {
        "index": i,
        "memory_used_mb": _bytes_to_mb(mem.used) if mem else None,
        "memory_free_mb": _bytes_to_mb(mem.free) if mem else None,
        "temp": safe_call(nvmlDeviceGetTemperature, handle, NVML_TEMPERATURE_GPU),
        "power": (power_mw / 1000.0) if isinstance(power_mw, int) else None,
        "sm_clock_mhz": safe_call(nvmlDeviceGetClockInfo, handle, NVML_CLOCK_SM),
    }



STATIC_FIELDS = [
    "index", "name", "uuid", "pci_bus_id",
    "driver_version", "vbios_version", "memory_total_mb", "ecc_mode",
]
DYNAMIC_FIELDS = [
    "index", "memory_used_mb", "memory_free_mb", "temp", "power", "sm_clock_mhz",
]
SCHEMA = {"static": STATIC_FIELDS, "dynamic": DYNAMIC_FIELDS}



def main():
    ap = argparse.ArgumentParser(description="NVML snapshot → table (static|dynamic)")
    ap.add_argument("--mode", choices=("static", "dynamic"), required=True)
    ap.add_argument("--no-header", action="store_true", help="Hide header row")
    ap.add_argument("--devices", type=str, default=None, help="e.g., 0,2 or 0-2")
    args = ap.parse_args()

    try:
        with nvml_context():
            count = nvmlDeviceGetCount()

            # device subset (optional)
            indices = list(range(count))
            if args.devices:
                sel = set()
                for tok in args.devices.split(","):
                    tok = tok.strip()
                    if not tok: 
                        continue
                    if "-" in tok:
                        a, b = tok.split("-", 1)
                        sel.update(range(int(a), int(b) + 1))
                    else:
                        sel.add(int(tok))
                indices = sorted(i for i in sel if 0 <= i < count)

            rows = []
            if args.mode == "static":
                for i in indices:
                    try:
                        rows.append(get_device_static(i))
                    except NVMLError:
                        rows.append({"index": i})
                fields = STATIC_FIELDS
            else:
                for i in indices:
                    try:
                        rows.append(get_device_dynamic(i))
                    except NVMLError:
                        rows.append({"index": i})
                fields = DYNAMIC_FIELDS

            # project to fixed schema so column order is stable
            rows_proj = [{f: r.get(f, None) for f in fields} for r in rows]

            # print table
            if args.no_header:
                print(tabulate(rows_proj, headers=[], tablefmt="github"))
            else:
                print(tabulate(rows_proj, headers="keys", tablefmt="github"))

    except NVMLError:
        print("nvml unavailable", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


