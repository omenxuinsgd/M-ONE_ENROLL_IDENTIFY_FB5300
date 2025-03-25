import ctypes
from ctypes import c_int, c_uint, POINTER, Structure, c_void_p, c_char_p, cast, c_ubyte
from PIL import Image
import numpy as np

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

# Define DPFPDD_QUALITY constants
DPFPDD_QUALITY_GOOD = 0
DPFPDD_QUALITY_TIMED_OUT = 1
DPFPDD_QUALITY_CANCELED = (1<<1)
DPFPDD_QUALITY_NO_FINGER = (1<<2)
DPFPDD_QUALITY_FAKE_FINGER = (1<<3)
DPFPDD_QUALITY_FINGER_TOO_LEFT = (1<<4)
DPFPDD_QUALITY_FINGER_TOO_RIGHT = (1<<5)
DPFPDD_QUALITY_FINGER_TOO_HIGH = (1<<6)
DPFPDD_QUALITY_FINGER_TOO_LOW = (1<<7)
DPFPDD_QUALITY_FINGER_OFF_CENTER = (1<<8)
DPFPDD_QUALITY_SCAN_SKEWED = (1<<9)
DPFPDD_QUALITY_SCAN_TOO_SHORT = (1<<10)
DPFPDD_QUALITY_SCAN_TOO_LONG = (1<<11)
DPFPDD_QUALITY_SCAN_TOO_SLOW = (1<<12)
DPFPDD_QUALITY_SCAN_TOO_FAST = (1<<13)
DPFPDD_QUALITY_SCAN_WRONG_DIRECTION = (1<<14)
DPFPDD_QUALITY_READER_DIRTY = (1<<15)

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

# Define DPFPDD_PARMID constants
DPFPDD_PARMID_ROTATE = 0x100
DPFPDD_PARMID_FINGERDETECT_ENABLE = 0x104
DPFPDD_PARMID_IOMAP = 0x105


# Definisikan konstanta untuk status code
DPFPDD_SUCCESS = 0
DPFPDD_E_FAILURE = -1
DPFPDD_E_INVALID_DEVICE = -2
DPFPDD_E_DEVICE_BUSY = -3
DPFPDD_E_MORE_DATA = 0x05BA000D
DPFPDD_E_INVALID_PARAMETER = -5
DPFPDD_E_DEVICE_FAILURE = -4


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

class DPFPDD_IMAGE_INFO(Structure):
    _fields_ = [("size", c_uint), ("width", c_uint), ("height", c_uint), ("res", c_uint), ("bpp", c_uint)]

class DPFPDD_CAPTURE_RESULT(Structure):
    _fields_ = [("size", c_uint), ("success", c_int), ("quality", c_int), ("score", c_uint), ("info", DPFPDD_IMAGE_INFO)]

class DPFPDD_CAPTURE_PARAM(Structure):
    _fields_ = [("size", c_uint), ("image_fmt", c_uint), ("image_proc", c_uint), ("image_res", c_uint)]

class DPFPDD_IOMAP(Structure):
    _fields_ = [("addr", c_uint), ("len", c_uint), ("buff", c_ubyte * 1)]

# Definisikan fungsi dpfpdd_get_stream_image
dll.dpfpdd_get_stream_image.argtypes = [
    POINTER(DPFPDD_DEV),  # Reader handle
    POINTER(DPFPDD_CAPTURE_PARAM),  # Capture parameters
    POINTER(DPFPDD_CAPTURE_RESULT),  # Capture result
    POINTER(c_uint),  # Image size (input/output)
    POINTER(c_ubyte),  # Image data buffer
]

dll.dpfpdd_get_stream_image.restype = c_int  # Status code
# Definisikan fungsi dpfpdd_start_stream dari dpfpdd.dll
dll.dpfpdd_start_stream.argtypes = [POINTER(DPFPDD_DEV)]  # Argumen: pointer ke DPFPDD_DEV
dll.dpfpdd_start_stream.restype = c_int  # Nilai kembalian: int (status code)


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

dll.dpfpdd_capture.argtypes = [
    POINTER(DPFPDD_DEV),
    POINTER(DPFPDD_CAPTURE_PARAM),
    c_uint,
    POINTER(DPFPDD_CAPTURE_RESULT),
    POINTER(c_uint),
    c_void_p
]
dll.dpfpdd_capture.restype = c_int

# Definisikan fungsi dpfpdd_stop_stream
dll.dpfpdd_stop_stream.argtypes = [POINTER(DPFPDD_DEV)]  # Argumen: pointer ke DPFPDD_DEV
dll.dpfpdd_stop_stream.restype = c_int  # Nilai kembalian: int (status code)

def stop_stream(dev):
    """
    Stop streaming mode on the fingerprint reader.
    
    Args:
        dev (POINTER(DPFPDD_DEV)): Handle to the opened device.
    
    Returns:
        int: Status code (0 for success, negative values for errors).
    """
    if not dev:
        print("Invalid device handle. Cannot stop streaming.")
        return DPFPDD_E_INVALID_DEVICE
    
    result = dll.dpfpdd_stop_stream(dev)
    
    if result == DPFPDD_SUCCESS:
        print("Streaming mode stopped successfully.")
    else:
        print(f"Failed to stop streaming. Error Code: {result}")
    
    return result

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

def capture_fingerprint(dev, timeout=5000, image_format=DPFPDD_IMG_FMT_ISOIEC19794, image_proc=DPFPDD_IMG_PROC_ENHANCED, image_res=500):
    if not dev:
        print("Invalid device handle. Cannot capture fingerprint.")
        return None
    
    # Set up capture parameters
    capture_param = DPFPDD_CAPTURE_PARAM()
    capture_param.size = ctypes.sizeof(DPFPDD_CAPTURE_PARAM)
    capture_param.image_fmt = image_format
    capture_param.image_proc = image_proc
    capture_param.image_res = image_res
    
    # Set up capture result
    capture_result = DPFPDD_CAPTURE_RESULT()
    capture_result.size = ctypes.sizeof(DPFPDD_CAPTURE_RESULT)
    image_size = c_uint()
    
    # First call to get the required buffer size
    result = dll.dpfpdd_capture(dev, ctypes.byref(capture_param), timeout, ctypes.byref(capture_result), ctypes.byref(image_size), None)
    
    # Handle specific error for DPFPDD_E_MORE_DATA
    ERROR_MORE_DATA = 0x05BA000D
    if result != 0 and result != ERROR_MORE_DATA:
        print(f"[ERROR] Failed to get buffer size. Code: 0x{result:08X}")
        return None
    
    print(f"[DEBUG] Buffer size required: {image_size.value} bytes")
    
    # Allocate buffer with the correct size
    image_buffer = ctypes.create_string_buffer(image_size.value)
    
    # Second call to capture the image
    result = dll.dpfpdd_capture(dev, ctypes.byref(capture_param), timeout, ctypes.byref(capture_result), ctypes.byref(image_size), image_buffer)
    
    if result == 0:
        print(f"Fingerprint captured successfully. Quality: {capture_result.quality}, Score: {capture_result.score}")
        print(f"Image Info - Width: {capture_result.info.width}, Height: {capture_result.info.height}, Resolution: {capture_result.info.res}, BPP: {capture_result.info.bpp}")
        
        # Save as raw file
        save_fingerprint_raw(image_buffer.raw[:image_size.value], "fingerprint.raw")

        # Save as PNG
        save_fingerprint_png(image_buffer.raw[:image_size.value], capture_result.info.width, capture_result.info.height, capture_result.info.bpp, "fingerprint.png")

        return image_buffer.raw[:image_size.value]
    else:
        print(f"[ERROR] Failed to capture fingerprint. Error Code: {result}")
        return None

def save_fingerprint_png(image_data, width, height, bpp, filename="fingerprint.png"):
    """
    Save fingerprint image as PNG.
    
    Args:
        image_data (bytes): Raw image data.
        width (int): Width of the image.
        height (int): Height of the image.
        bpp (int): Bits per pixel.
        filename (str): Output filename.
    """
    bytes_per_pixel = bpp // 8  # Convert bits-per-pixel to bytes-per-pixel
    expected_size = width * height * bytes_per_pixel

    # Remove header (first 46 bytes)
    header_size = 46
    if len(image_data) < header_size + expected_size:
        print(f"[ERROR] Image data size {len(image_data)} is smaller than expected {header_size + expected_size}")
        return
    
    # Remove header and take only the required size
    image_data = image_data[header_size:header_size + expected_size]
    
    # Debug: Print data after removing header
    print(f"[DEBUG] First 10 bytes after removing header: {image_data[:10]}")
    
    # Convert to numpy array
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    
    # Debug: Print array shape and first few values
    print(f"[DEBUG] Numpy array shape: {image_array.shape}")
    print(f"[DEBUG] First 10 values of numpy array: {image_array[:10]}")
    
    # Reshape the array based on the number of channels
    if bytes_per_pixel > 1:
        image_array = image_array.reshape((height, width, bytes_per_pixel))
    else:
        image_array = image_array.reshape((height, width))

    # Debug: Print reshaped array shape
    print(f"[DEBUG] Reshaped numpy array shape: {image_array.shape}")
    
    # Create and save the image
    img = Image.fromarray(image_array, mode="L" if bytes_per_pixel == 1 else "RGB")
    img.save(filename)
    print(f"Fingerprint saved as {filename}")

def save_fingerprint_raw(image_data, filename="fingerprint.raw"):
    with open(filename, "wb") as f:
        f.write(image_data)
    print(f"Fingerprint saved as {filename}")

def set_reader_parameter(dev, param_id, buffer):
    size = len(buffer)
    buffer_type = (c_ubyte * size)(*buffer)
    result = dll.dpfpdd_set_parameter(dev, param_id, size, buffer_type)
    
    if result == 0:
        print(f"Parameter {param_id} set successfully.")
    else:
        print(f"Failed to set parameter {param_id}. Error Code: {result}")
    
    return result

def start_stream(dev):
    """
    Start streaming mode on the fingerprint reader.
    
    Args:
        dev (POINTER(DPFPDD_DEV)): Handle to the opened device.
    
    Returns:
        int: Status code (0 for success, negative values for errors).
    """
    if not dev:
        print("Invalid device handle. Cannot start streaming.")
        return DPFPDD_E_INVALID_DEVICE
    
    result = dll.dpfpdd_start_stream(dev)
    
    if result == DPFPDD_SUCCESS:
        print("Streaming mode started successfully.")
    elif result == DPFPDD_E_FAILURE:
        print("Failed to start streaming: Unexpected failure.")
    elif result == DPFPDD_E_INVALID_DEVICE:
        print("Failed to start streaming: Invalid device handle.")
    elif result == DPFPDD_E_DEVICE_BUSY:
        print("Failed to start streaming: Device is busy.")
    elif result == DPFPDD_E_DEVICE_FAILURE:
        print("Failed to start streaming: Device is not functioning properly.")
    else:
        print(f"Failed to start streaming: Unknown error code {result}.")
    
    return result

def get_stream_image(dev, image_format=DPFPDD_IMG_FMT_ISOIEC19794, image_proc=DPFPDD_IMG_PROC_ENHANCED, image_res=500):
    """
    Get an image from the streaming mode.
    
    Args:
        dev (POINTER(DPFPDD_DEV)): Handle to the opened device.
        image_format (int): Format of the image (default: DPFPDD_IMG_FMT_ISOIEC19794).
        image_proc (int): Image processing mode (default: DPFPDD_IMG_PROC_ENHANCED).
        image_res (int): Image resolution (default: 500 DPI).
    
    Returns:
        bytes: Raw image data (without header), or None if failed.
    """
    if not dev:
        print("Invalid device handle. Cannot get stream image.")
        return None
    
    # Set up capture parameters
    capture_param = DPFPDD_CAPTURE_PARAM()
    capture_param.size = ctypes.sizeof(DPFPDD_CAPTURE_PARAM)
    capture_param.image_fmt = image_format
    capture_param.image_proc = image_proc
    capture_param.image_res = image_res
    
    # Debug: Print capture parameters
    print(f"[DEBUG] Capture Parameters - Format: 0x{capture_param.image_fmt:08X}, Processing: 0x{capture_param.image_proc:08X}, Resolution: {capture_param.image_res}")
    
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

def is_finger_detected(dev):
    """
    Check if a finger is detected on the reader.
    
    Args:
        dev (POINTER(DPFPDD_DEV)): Handle to the opened device.
    
    Returns:
        bool: True if a finger is detected, False otherwise.
    """
    if not dev:
        print("Invalid device handle. Cannot check finger status.")
        return False
    
    status = DPFPDD_DEV_STATUS()
    status.size = ctypes.sizeof(DPFPDD_DEV_STATUS)
    
    result = dll.dpfpdd_get_device_status(dev, ctypes.byref(status))
    if result == DPFPDD_SUCCESS:
        return status.finger_detected == 1
    else:
        print(f"[ERROR] Failed to get device status. Code: 0x{result:08X}")
        return False
     
# Example usage
import time

if __name__ == "__main__":
    get_version()
    initialize_library()
    device_name = query_devices()
    
    if device_name:
        dev = open_reader(device_name)
        if dev:
            get_reader_status(dev)
            get_reader_capabilities(dev)
            
            # Start streaming mode
            if start_stream(dev) == DPFPDD_SUCCESS:
                print("Waiting for finger detection...")
                
                # Wait for finger to be detected
                finger_detected = False
                for _ in range(10):  # Try for 10 seconds
                    if is_finger_detected(dev):
                        finger_detected = True
                        break
                    time.sleep(1)  # Wait 1 second before checking again
                
                if finger_detected:
                    print("Finger detected. Stopping streaming and capturing image...")
                    
                    # Stop streaming mode
                    stop_stream(dev)
                    
                    # Capture fingerprint using capture_fingerprint
                    image_data = capture_fingerprint(dev)
                    if image_data:
                        # Save the image
                        save_fingerprint_raw(image_data, "capture_fingerprint.raw")
                        save_fingerprint_png(image_data, 400, 500, 8, "capture_fingerprint.png")
                else:
                    print("No finger detected within 10 seconds.")
            
            close_reader(dev)
    exit_library()