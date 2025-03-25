import ctypes
from ctypes import c_int, c_uint, POINTER, Structure, c_void_p, c_char_p, cast

# Load the DPFPDD DLL
dll = ctypes.WinDLL("dpfpdd.dll")

# Define the necessary structures
class DPFPDD_VER_INFO(Structure):
    _fields_ = [
        ("major", c_int),
        ("minor", c_int),
        ("maintenance", c_int),
    ]

class DPFPDD_VERSION(Structure):
    _fields_ = [
        ("size", c_uint),
        ("lib_ver", DPFPDD_VER_INFO),
        ("api_ver", DPFPDD_VER_INFO),
    ]

# Struktur untuk menyimpan informasi perangkat
class DPFPDD_DEV_INFO(ctypes.Structure):
    _fields_ = [("size", ctypes.c_uint),
                ("name", ctypes.c_char * 256)]  # Buffer untuk nama perangkat
    
class DPFPDD_DEV(Structure):
    pass

# Function Prototypes
dll.dpfpdd_version.argtypes = [POINTER(DPFPDD_VERSION)]
dll.dpfpdd_version.restype = c_int

dll.dpfpdd_init.argtypes = []
dll.dpfpdd_init.restype = c_int

dll.dpfpdd_exit.argtypes = []
dll.dpfpdd_exit.restype = c_int

dll.dpfpdd_query_devices.argtypes = [POINTER(c_int), POINTER(DPFPDD_DEV_INFO)]
dll.dpfpdd_query_devices.restype = c_int

dll.dpfpdd_open.argtypes = [c_char_p, POINTER(POINTER(DPFPDD_DEV))]
dll.dpfpdd_open.restype = c_int

dll.dpfpdd_open_ext.argtypes = [c_char_p, c_uint, POINTER(POINTER(DPFPDD_DEV))]
dll.dpfpdd_open_ext.restype = c_int

dll.dpfpdd_close.argtypes = [POINTER(DPFPDD_DEV)]
dll.dpfpdd_close.restype = c_int

# Get library version
def get_version():
    version = DPFPDD_VERSION()
    version.size = ctypes.sizeof(DPFPDD_VERSION)

    result = dll.dpfpdd_version(ctypes.byref(version))
    if result == 0:
        print(f"Library Version: {version.lib_ver.major}.{version.lib_ver.minor}.{version.lib_ver.maintenance}")
        print(f"API Version: {version.api_ver.major}.{version.api_ver.minor}.{version.api_ver.maintenance}")
    else:
        print(f"Failed to get version information. Error Code: {result}")

# Initialize the library
def initialize_library():
    result = dll.dpfpdd_init()
    if result == 0:
        print("Library initialized successfully")
    else:
        print(f"Failed to initialize library. Error Code: {result}")

# Query connected devices
def query_devices():
    device_count = c_int(0)
    result = dll.dpfpdd_query_devices(ctypes.byref(device_count), None)
    
    if result != 0 and device_count.value == 0:
        print("No devices found or failed to query devices.")
        dll.dpfpdd_exit()
        return None
    
    devices = (DPFPDD_DEV_INFO * device_count.value)()
    for i in range(device_count.value):
        devices[i].size = ctypes.sizeof(DPFPDD_DEV_INFO)
    
    result = dll.dpfpdd_query_devices(ctypes.byref(device_count), devices)
    if result == 0:
        print(f"Count Devices: {device_count.value}")
        device_name = devices[0].name.decode("ascii")
        print(f"Detected Device: {device_name}")
        return device_name
    else:
        print(f"Failed to query devices. Error Code: {result}")
        return None
    
# Open a fingerprint reader
def open_reader(device_name):
    dev = POINTER(DPFPDD_DEV)()
    result = dll.dpfpdd_open(device_name.encode('ascii'), ctypes.byref(dev))
    if result == 0:
        print("Reader opened successfully")
        return dev
    else:
        print(f"Failed to open reader. Error Code: {result}")
        return None

# Open a fingerprint reader with extended options
def open_reader_ext(device_name, mode=0):
    dev = POINTER(DPFPDD_DEV)()
    result = dll.dpfpdd_open_ext(device_name.encode('ascii'), mode, ctypes.byref(dev))
    if result == 0:
        print("Reader opened successfully with extended options")
        return dev
    else:
        print(f"Failed to open reader with extended options. Error Code: {result}")
        return None

# Close a fingerprint reader
def close_reader(dev):
    if dev:
        result = dll.dpfpdd_close(dev)
        if result == 0:
            print("Reader closed successfully")
        else:
            print(f"Failed to close reader. Error Code: {result}")
    else:
        print("Invalid device handle. Cannot close reader.")

# Exit the library
def exit_library():
    result = dll.dpfpdd_exit()
    if result == 0:
        print("Library exited successfully")
    else:
        print(f"Failed to exit library. Error Code: {result}")

# Example usage
if __name__ == "__main__":
    get_version()
    initialize_library()
    device_name = query_devices()
    if device_name:
        dev = open_reader(device_name)
        if not dev:
            print("Trying to open reader with extended options...")
            dev = open_reader_ext(device_name, mode=1)
        if dev:
            close_reader(dev)
    exit_library()