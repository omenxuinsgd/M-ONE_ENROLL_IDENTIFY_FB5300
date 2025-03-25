import ctypes
from ctypes import c_int, c_uint, POINTER, Structure

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

class DPFPDD_DEV_INFO(Structure):
    _fields_ = [("name", ctypes.c_char_p)]

# Function Prototypes
dll.dpfpdd_version.argtypes = [POINTER(DPFPDD_VERSION)]
dll.dpfpdd_version.restype = c_int

dll.dpfpdd_init.argtypes = []
dll.dpfpdd_init.restype = c_int

dll.dpfpdd_exit.argtypes = []
dll.dpfpdd_exit.restype = c_int

dll.dpfpdd_query_devices.argtypes = [POINTER(c_int), POINTER(DPFPDD_DEV_INFO)]
dll.dpfpdd_query_devices.restype = c_int

# Get library version
def get_version():
    version = DPFPDD_VERSION()
    version.size = ctypes.sizeof(DPFPDD_VERSION)  # Pastikan size diset dengan benar

    result = dll.dpfpdd_version(ctypes.byref(version))
    if result == 0:  # DPFPDD_SUCCESS
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
    device_count = c_int(10)  # Allocate space for up to 10 devices
    devices = (DPFPDD_DEV_INFO * 10)()
    result = dll.dpfpdd_query_devices(ctypes.byref(device_count), devices)
    
    if result == 0:
        print(f"Connected Devices: {device_count.value}")
        for i in range(device_count.value):
            print(f"Device {i + 1}: {devices[i].name.decode('utf-8') if devices[i].name else 'Unknown'}")
    else:
        print(f"Failed to query devices. Error Code: {result}")

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
    query_devices()
    exit_library()
