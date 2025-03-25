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

# Define DPFPDD_STATUS constants
DPFPDD_STATUS_READY = 0
DPFPDD_STATUS_BUSY = 1
DPFPDD_STATUS_NEED_CALIBRATION = 2
DPFPDD_STATUS_FAILURE = 3

class DPFPDD_DEV_STATUS(Structure):
    _fields_ = [
        ("size", c_uint),
        ("status", c_uint),
        ("finger_detected", c_int),
        ("data", ctypes.c_ubyte * 1)  # Placeholder for vendor-specific data
    ]

class DPFPDD_DEV_CAPS(Structure):
    _fields_ = [
        ("size", c_uint),
        ("can_capture_image", c_int),
        ("can_stream_image", c_int),
        ("can_extract_features", c_int),
        ("can_match", c_int),
        ("can_identify", c_int),
        ("has_fp_storage", c_int),
        ("indicator_type", c_uint),
        ("has_pwr_mgmt", c_int),
        ("has_calibration", c_int),
        ("piv_compliant", c_int),
        ("resolution_cnt", c_uint),
        ("resolutions", c_uint * 1)  # Array of resolutions
    ]

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

dll.dpfpdd_get_device_status.argtypes = [POINTER(DPFPDD_DEV), POINTER(DPFPDD_DEV_STATUS)]
dll.dpfpdd_get_device_status.restype = c_int

dll.dpfpdd_get_device_capabilities.argtypes = [POINTER(DPFPDD_DEV), POINTER(DPFPDD_DEV_CAPS)]
dll.dpfpdd_get_device_capabilities.restype = c_int

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

# Get reader status
def get_reader_status(dev):
    if not dev:
        print("Invalid device handle. Cannot get reader status.")
        return
    
    status = DPFPDD_DEV_STATUS()
    status.size = ctypes.sizeof(DPFPDD_DEV_STATUS)
    result = dll.dpfpdd_get_device_status(dev, ctypes.byref(status))
    
    if result == 0:
        print(f"Reader status obtained successfully. Status Code: {status.status}")
        if status.status == DPFPDD_STATUS_READY:
            print("Reader is ready for capture.")
        elif status.status == DPFPDD_STATUS_BUSY:
            print("Reader is busy with another operation.")
        elif status.status == DPFPDD_STATUS_NEED_CALIBRATION:
            print("Reader needs calibration soon.")
        elif status.status == DPFPDD_STATUS_FAILURE:
            print("Reader has failed and needs a reset.")
        else:
            print("Unknown status.")
    else:
        print(f"Failed to obtain reader status. Error Code: {result}")
        
# Get device capabilities
def get_reader_capabilities(dev):
    caps = DPFPDD_DEV_CAPS()
    caps.size = ctypes.sizeof(DPFPDD_DEV_CAPS)
    result = dll.dpfpdd_get_device_capabilities(dev, ctypes.byref(caps))
    if result == 0:
        print("[INFO] Kemampuan Perangkat:")
        print(f"  Dapat menangkap gambar: {caps.can_capture_image}")
        print(f"  Dapat streaming gambar: {caps.can_stream_image}")
        print(f"  Dapat mengekstrak fitur: {caps.can_extract_features}")
        print(f"  Dapat mencocokkan: {caps.can_match}")
        print(f"  Dapat mengidentifikasi: {caps.can_identify}")
        print(f"  Memiliki penyimpanan sidik jari: {caps.has_fp_storage}")
        print(f"  Jumlah resolusi: {caps.resolution_cnt}")
        print(f"  Resolusi yang tersedia: {[caps.resolutions[i] for i in range(caps.resolution_cnt)]}")
    else:
        print(f"Failed to obtain reader capabilities. Error Code: {result}")

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
        if dev:
            get_reader_status(dev)
            get_reader_capabilities(dev)
            close_reader(dev)
    exit_library()
