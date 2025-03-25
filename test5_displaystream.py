import ctypes
from ctypes import c_int, c_uint, POINTER, Structure, c_void_p, c_char_p, c_ubyte
import numpy as np
import cv2
import time

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

class DPFPDD_DEV_INFO(ctypes.Structure):
    _fields_ = [("size", ctypes.c_uint),
                ("name", ctypes.c_char * 256)]

class DPFPDD_DEV(Structure):
    pass

# Define DPFPDD_STATUS constants
DPFPDD_STATUS_READY = 0
DPFPDD_STATUS_BUSY = 1
DPFPDD_STATUS_NEED_CALIBRATION = 2
DPFPDD_STATUS_FAILURE = 3

# Define DPFPDD_IMAGE_FMT constants
DPFPDD_IMG_FMT_PIXEL_BUFFER = 0
DPFPDD_IMG_FMT_ANSI381 = 0x001B0401
DPFPDD_IMG_FMT_ISOIEC19794 = 0x01010007

# Define DPFPDD_IMAGE_PROC constants
DPFPDD_IMG_PROC_DEFAULT = 0
DPFPDD_IMG_PROC_PIV = 1
DPFPDD_IMG_PROC_ENHANCED = 2
DPFPDD_IMG_PROC_UNPROCESSED = 0x52617749
DPFPDD_IMG_PROC_NONE = 0

class DPFPDD_DEV_STATUS(Structure):
    _fields_ = [
        ("size", c_uint),
        ("status", c_uint),
        ("finger_detected", c_int),
        ("data", ctypes.c_ubyte * 1)
    ]

class DPFPDD_IMAGE_INFO(Structure):
    _fields_ = [("size", c_uint), ("width", c_uint), ("height", c_uint), ("res", c_uint), ("bpp", c_uint)]

class DPFPDD_CAPTURE_RESULT(Structure):
    _fields_ = [("size", c_uint), ("success", c_int), ("quality", c_int), ("score", c_uint), ("info", DPFPDD_IMAGE_INFO)]

class DPFPDD_CAPTURE_PARAM(Structure):
    _fields_ = [("size", c_uint), ("image_fmt", c_uint), ("image_proc", c_uint), ("image_res", c_uint)]

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

dll.dpfpdd_close.argtypes = [POINTER(DPFPDD_DEV)]
dll.dpfpdd_close.restype = c_int

dll.dpfpdd_get_device_status.argtypes = [POINTER(DPFPDD_DEV), POINTER(DPFPDD_DEV_STATUS)]
dll.dpfpdd_get_device_status.restype = c_int

dll.dpfpdd_start_stream.argtypes = [POINTER(DPFPDD_DEV)]
dll.dpfpdd_start_stream.restype = c_int

dll.dpfpdd_stop_stream.argtypes = [POINTER(DPFPDD_DEV)]
dll.dpfpdd_stop_stream.restype = c_int

dll.dpfpdd_get_stream_image.argtypes = [
    POINTER(DPFPDD_DEV),
    POINTER(DPFPDD_CAPTURE_PARAM),
    POINTER(DPFPDD_CAPTURE_RESULT),
    POINTER(c_uint),
    POINTER(c_ubyte)
]
dll.dpfpdd_get_stream_image.restype = c_int

# Constants for status codes
DPFPDD_SUCCESS = 0
DPFPDD_E_FAILURE = -1
DPFPDD_E_INVALID_DEVICE = -2
DPFPDD_E_DEVICE_BUSY = -3
DPFPDD_E_MORE_DATA = 0x05BA000D
DPFPDD_E_INVALID_PARAMETER = -5
DPFPDD_E_DEVICE_FAILURE = -4

# Function to get library version
def get_version():
    version = DPFPDD_VERSION()
    version.size = ctypes.sizeof(DPFPDD_VERSION)
    result = dll.dpfpdd_version(ctypes.byref(version))
    if result == 0:
        print(f"Library Version: {version.lib_ver.major}.{version.lib_ver.minor}.{version.lib_ver.maintenance}")
        print(f"API Version: {version.api_ver.major}.{version.api_ver.minor}.{version.api_ver.maintenance}")
    else:
        print(f"Failed to get version information. Error Code: {result}")

# Function to initialize the library
def initialize_library():
    result = dll.dpfpdd_init()
    if result == 0:
        print("Library initialized successfully")
    else:
        print(f"Failed to initialize library. Error Code: {result}")

# Function to query connected devices
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

# Function to open a fingerprint reader
def open_reader(device_name):
    dev = POINTER(DPFPDD_DEV)()
    result = dll.dpfpdd_open(device_name.encode('ascii'), ctypes.byref(dev))
    if result == 0:
        print("Reader opened successfully")
        return dev
    else:
        print(f"Failed to open reader. Error Code: {result}")
        return None

# Function to get reader status
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

# Function to start streaming mode
def start_stream(dev):
    if not dev:
        print("Invalid device handle. Cannot start streaming.")
        return DPFPDD_E_INVALID_DEVICE
    
    result = dll.dpfpdd_start_stream(dev)
    if result == DPFPDD_SUCCESS:
        print("Streaming mode started successfully.")
    else:
        print(f"Failed to start streaming. Error Code: {result}")
    return result

# Function to stop streaming mode
def stop_stream(dev):
    if not dev:
        print("Invalid device handle. Cannot stop streaming.")
        return DPFPDD_E_INVALID_DEVICE
    
    result = dll.dpfpdd_stop_stream(dev)
    if result == DPFPDD_SUCCESS:
        print("Streaming mode stopped successfully.")
    else:
        print(f"Failed to stop streaming. Error Code: {result}")
    return result

# Function to get an image from the stream
def get_stream_image(dev):
    if not dev:
        print("Invalid device handle. Cannot get stream image.")
        return None
    
    # Set up capture parameters
    capture_param = DPFPDD_CAPTURE_PARAM()
    capture_param.size = ctypes.sizeof(DPFPDD_CAPTURE_PARAM)
    capture_param.image_fmt = DPFPDD_IMG_FMT_ISOIEC19794
    capture_param.image_proc = DPFPDD_IMG_PROC_ENHANCED
    capture_param.image_res = 500
    
    # Set up capture result
    capture_result = DPFPDD_CAPTURE_RESULT()
    capture_result.size = ctypes.sizeof(DPFPDD_CAPTURE_RESULT)
    
    # First call to get the required buffer size
    image_size = c_uint()
    result = dll.dpfpdd_get_stream_image(dev, ctypes.byref(capture_param), ctypes.byref(capture_result), ctypes.byref(image_size), None)
    
    if result != DPFPDD_SUCCESS and result != DPFPDD_E_MORE_DATA:
        print(f"[ERROR] Failed to get buffer size. Code: 0x{result:08X}")
        return None
    
    print(f"[DEBUG] Buffer size required: {image_size.value} bytes")
    
    # Allocate buffer with the correct size
    image_buffer = (c_ubyte * image_size.value)()
    
    # Second call to get the image
    result = dll.dpfpdd_get_stream_image(dev, ctypes.byref(capture_param), ctypes.byref(capture_result), ctypes.byref(image_size), image_buffer)
    
    if result == DPFPDD_SUCCESS:
        print(f"[DEBUG] Image Info - Width: {capture_result.info.width}, Height: {capture_result.info.height}, Resolution: {capture_result.info.res}, BPP: {capture_result.info.bpp}")
        print(f"[DEBUG] First 100 bytes of raw data: {bytes(image_buffer[:100])}")
        
        # Remove header (first 46 bytes)
        header_size = 46
        if image_size.value < header_size:
            print(f"[ERROR] Image data size {image_size.value} is smaller than header size {header_size}")
            return None
        
        image_data = bytes(image_buffer[header_size:])
        print(f"[DEBUG] Image data size after removing header: {len(image_data)} bytes")
        
        return image_data
    else:
        print(f"[ERROR] Failed to get stream image. Code: 0x{result:08X}")
        return None

# Function to display the stream in real-time
def display_stream(dev):
    if not dev:
        print("Invalid device handle. Cannot display stream.")
        return
    
    print("Starting real-time stream display. Press 'q' to quit.")
    
    while True:
        # Get image from stream
        image_data = get_stream_image(dev)
        if not image_data:
            print("[ERROR] Failed to get stream image. Retrying...")
            continue  # Lanjutkan loop meskipun gagal
        
        # Convert raw image data to numpy array
        width = 400  # Sesuaikan dengan lebar gambar yang dikembalikan oleh perangkat
        height = 500  # Sesuaikan dengan tinggi gambar yang dikembalikan oleh perangkat
        image_array = np.frombuffer(image_data, dtype=np.uint8).reshape((height, width))
        
        # Display the image using OpenCV
        cv2.imshow("Fingerprint Stream", image_array)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Close the OpenCV window
    cv2.destroyAllWindows()

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

# Main program
if __name__ == "__main__":
    get_version()
    initialize_library()
    device_name = query_devices()
    
    if device_name:
        dev = open_reader(device_name)
        if dev:
            get_reader_status(dev)
            
            # Start streaming mode
            if start_stream(dev) == DPFPDD_SUCCESS:
                # Display the stream in real-time
                display_stream(dev)
                
                # Stop streaming mode
                stop_stream(dev)
            
            close_reader(dev)
    exit_library()