import ctypes
from ctypes import c_int, c_uint, POINTER, Structure, c_void_p, c_char_p, c_ubyte, byref
import os
from PIL import Image
import wsq
import io

# Load the DPFPDD and DPFJ DLLs
dpfpdd_dll = ctypes.WinDLL("dpfpdd.dll")
dpfj_dll = ctypes.WinDLL("dpfj.dll")
# Load the DPFJ Compression DLL
dpfj_compression_dll = ctypes.WinDLL("./dpfj_compression.dll")

# Define compression algorithms
DPFJ_COMPRESSION_WSQ_NIST = 1  # NIST WSQ algorithm
DPFJ_COMPRESSION_WSQ_AWARE = 2  # Aware WSQ algorithm

# Define error codes
DPFJ_E_COMPRESSION_NOT_STARTED = 0x05BA0142
DPFJ_E_COMPRESSION_INVALID_WSQ_PARAMETER = 0x05BA014A
DPFJ_E_COMPRESSION_WSQ_LIB_NOT_FOUND = 0x05BA014C
DPFJ_E_COMPRESSION_WSQ_FAILURE = 0x05BA014B

# Define dpfj_set_wsq_size function prototype
dpfj_compression_dll.dpfj_set_wsq_size.argtypes = [ctypes.c_uint, ctypes.c_uint]
dpfj_compression_dll.dpfj_set_wsq_size.restype = ctypes.c_int

# Define dpfj_compress_raw function prototype
dpfj_compression_dll.dpfj_compress_raw.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),  # image_data
    ctypes.c_uint,                   # image_size
    ctypes.c_uint,                   # image_width
    ctypes.c_uint,                   # image_height
    ctypes.c_uint,                   # image_dpi
    ctypes.c_uint,                   # image_bpp
    ctypes.c_int                     # compression_alg
]
dpfj_compression_dll.dpfj_compress_raw.restype = ctypes.c_int

# Define dpfj_expand_raw function prototype
dpfj_compression_dll.dpfj_expand_raw.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),  # image_data
    ctypes.c_uint,                   # image_size
    ctypes.c_int,                    # compression_alg
    ctypes.POINTER(ctypes.c_uint),   # image_width
    ctypes.POINTER(ctypes.c_uint),   # image_height
    ctypes.POINTER(ctypes.c_uint),   # image_dpi
    ctypes.POINTER(ctypes.c_uint)    # image_bpp
]
dpfj_compression_dll.dpfj_expand_raw.restype = ctypes.c_int

# Define function prototypes for WSQ Compression
dpfj_compression_dll.dpfj_start_compression.argtypes = []
dpfj_compression_dll.dpfj_start_compression.restype = c_int

dpfj_compression_dll.dpfj_finish_compression.argtypes = []
dpfj_compression_dll.dpfj_finish_compression.restype = c_int

dpfj_compression_dll.dpfj_set_wsq_bitrate.argtypes = [c_uint, c_uint]
dpfj_compression_dll.dpfj_set_wsq_bitrate.restype = c_int

dpfj_compression_dll.dpfj_compress_fid.argtypes = [
    c_int,  # fid_type
    POINTER(c_ubyte),  # fid
    c_uint,  # fid_size
    c_int  # compression_alg
]
dpfj_compression_dll.dpfj_compress_fid.restype = c_int

dpfj_compression_dll.dpfj_get_processed_data.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),  # image_data
    ctypes.POINTER(ctypes.c_uint)    # image_size
]
dpfj_compression_dll.dpfj_get_processed_data.restype = ctypes.c_int

dpfj_compression_dll.dpfj_expand_fid.argtypes = [
    c_int,  # fid_type
    POINTER(c_ubyte),  # fid
    c_uint,  # fid_size
    c_int  # compression_alg
]
dpfj_compression_dll.dpfj_expand_fid.restype = c_int

# Define DPFJ_CANDIDATE structure
class DPFJ_CANDIDATE(Structure):
    _fields_ = [
        ("size", c_uint),      # Size of the structure, in bytes
        ("fmd_idx", c_uint),   # Index of the FMD in the input array
        ("view_idx", c_uint)   # Index of the view in the FMD
    ]

# Define the necessary structures for DPFPDD
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

# Define DPFJ_FMD_FORMAT constants
DPFJ_FMD_ANSI_378_2004 = 0x001B0001
DPFJ_FMD_ISO_19794_2_2005 = 0x01010001
DPFJ_FMD_DP_PRE_REG_FEATURES = 0
DPFJ_FMD_DP_REG_FEATURES = 1
DPFJ_FMD_DP_VER_FEATURES = 2

# Define DPFJ_FMD_FORMAT type
DPFJ_FMD_FORMAT = c_int

# Define DPFJ_SUCCESS and other error codes
DPFJ_SUCCESS = 0
DPFJ_E_MORE_DATA = 0x05BA000D
DPFJ_E_INVALID_PARAMETER = 0x05BA0001
DPFJ_E_ENROLLMENT_IN_PROGRESS = 0x05BA0002
DPFJ_E_ENROLLMENT_NOT_STARTED = 0x05BA0003
DPFJ_E_FAILURE = 0x05BA0004

# Define DPFJ_FINGER_POSITION constants
DPFJ_POSITION_UNKNOWN = 0
DPFJ_POSITION_RTHUMB = 1
DPFJ_POSITION_RINDEX = 2
DPFJ_POSITION_RMIDDLE = 3
DPFJ_POSITION_RRING = 4
DPFJ_POSITION_RLITTLE = 5
DPFJ_POSITION_LTHUMB = 6
DPFJ_POSITION_LINDEX = 7
DPFJ_POSITION_LMIDDLE = 8
DPFJ_POSITION_LRING = 9
DPFJ_POSITION_LLITTLE = 10

# Define DPFJ_FID_FORMAT constants
DPFJ_FID_ANSI_381_2004 = 0x001B0401
DPFJ_FID_ISO_19794_4_2005 = 0x01010007

# Define DPFJ_FINGER_POSITION type
DPFJ_FINGER_POSITION = c_int

# Define DPFJ_FID_FORMAT type
DPFJ_FID_FORMAT = c_int

# Function Prototypes for DPFPDD
dpfpdd_dll.dpfpdd_version.argtypes = [POINTER(DPFPDD_VERSION)]
dpfpdd_dll.dpfpdd_version.restype = c_int

dpfpdd_dll.dpfpdd_init.argtypes = []
dpfpdd_dll.dpfpdd_init.restype = c_int

dpfpdd_dll.dpfpdd_exit.argtypes = []
dpfpdd_dll.dpfpdd_exit.restype = c_int

dpfpdd_dll.dpfpdd_query_devices.argtypes = [POINTER(c_int), POINTER(DPFPDD_DEV_INFO)]
dpfpdd_dll.dpfpdd_query_devices.restype = c_int

dpfpdd_dll.dpfpdd_open.argtypes = [c_char_p, POINTER(POINTER(DPFPDD_DEV))]
dpfpdd_dll.dpfpdd_open.restype = c_int

dpfpdd_dll.dpfpdd_close.argtypes = [POINTER(DPFPDD_DEV)]
dpfpdd_dll.dpfpdd_close.restype = c_int

dpfpdd_dll.dpfpdd_get_device_status.argtypes = [POINTER(DPFPDD_DEV), POINTER(DPFPDD_DEV_STATUS)]
dpfpdd_dll.dpfpdd_get_device_status.restype = c_int

dpfpdd_dll.dpfpdd_capture.argtypes = [
    POINTER(DPFPDD_DEV),
    POINTER(DPFPDD_CAPTURE_PARAM),
    c_uint,
    POINTER(DPFPDD_CAPTURE_RESULT),
    POINTER(c_uint),
    c_void_p
]
dpfpdd_dll.dpfpdd_capture.restype = c_int

# Define dpfj_fmd_convert function
dpfj_dll.dpfj_fmd_convert.argtypes = [
    DPFJ_FMD_FORMAT,                 # fmd1_type
    ctypes.POINTER(ctypes.c_ubyte),  # fmd1
    ctypes.c_uint,                   # fmd1_size
    DPFJ_FMD_FORMAT,                 # fmd2_type
    ctypes.POINTER(ctypes.c_ubyte),  # fmd2
    ctypes.POINTER(ctypes.c_uint)    # fmd2_size
]
dpfj_dll.dpfj_fmd_convert.restype = ctypes.c_int

# Define dpfj_compare function
dpfj_dll.dpfj_compare.argtypes = [
    DPFJ_FMD_FORMAT,          # fmd1_type
    ctypes.POINTER(c_ubyte),  # fmd1
    c_uint,                   # fmd1_size
    c_uint,                   # fmd1_view_idx
    DPFJ_FMD_FORMAT,          # fmd2_type
    ctypes.POINTER(c_ubyte),  # fmd2
    c_uint,                   # fmd2_size
    c_uint,                   # fmd2_view_idx
    ctypes.POINTER(c_uint)    # score
]
dpfj_dll.dpfj_compare.restype = c_int

# Define dpfj_create_fmd_from_raw function
dpfj_dll.dpfj_create_fmd_from_raw.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),  # image_data
    ctypes.c_uint,                   # image_size
    ctypes.c_uint,                   # image_width
    ctypes.c_uint,                   # image_height
    ctypes.c_uint,                   # image_dpi
    DPFJ_FINGER_POSITION,            # finger_pos
    ctypes.c_uint,                   # cbeff_id
    DPFJ_FMD_FORMAT,                 # fmd_type
    ctypes.POINTER(ctypes.c_ubyte),  # fmd
    ctypes.POINTER(ctypes.c_uint)    # fmd_size
]
dpfj_dll.dpfj_create_fmd_from_raw.restype = ctypes.c_int

# Define dpfj_start_enrollment function
dpfj_dll.dpfj_start_enrollment.argtypes = [DPFJ_FMD_FORMAT]  # fmd_type
dpfj_dll.dpfj_start_enrollment.restype = c_int

# Define dpfj_add_to_enrollment function
dpfj_dll.dpfj_add_to_enrollment.argtypes = [
    DPFJ_FMD_FORMAT,          # fmd_type
    ctypes.POINTER(c_ubyte),  # fmd
    c_uint,                   # fmd_size
    c_uint                    # fmd_view_idx
]
dpfj_dll.dpfj_add_to_enrollment.restype = c_int

# Define dpfj_create_enrollment_fmd function
dpfj_dll.dpfj_create_enrollment_fmd.argtypes = [
    ctypes.POINTER(c_ubyte),  # fmd
    ctypes.POINTER(c_uint)    # fmd_size
]
dpfj_dll.dpfj_create_enrollment_fmd.restype = c_int

# Define dpfj_finish_enrollment function
dpfj_dll.dpfj_finish_enrollment.argtypes = []
dpfj_dll.dpfj_finish_enrollment.restype = c_int

# Define dpfj_identify function
dpfj_dll.dpfj_identify.argtypes = [
    DPFJ_FMD_FORMAT,          # fmd1_type
    ctypes.POINTER(c_ubyte),  # fmd1
    c_uint,                   # fmd1_size
    c_uint,                   # fmd1_view_idx
    DPFJ_FMD_FORMAT,          # fmds_type
    c_uint,                   # fmds_cnt
    ctypes.POINTER(ctypes.POINTER(c_ubyte)),  # fmds
    ctypes.POINTER(c_uint),   # fmds_size
    c_uint,                   # threshold_score
    ctypes.POINTER(c_uint),   # candidate_cnt
    ctypes.POINTER(DPFJ_CANDIDATE)  # candidates
]
dpfj_dll.dpfj_identify.restype = c_int

# Query connected devices
def query_devices():
    # Step 1: Get the number of devices
    device_count = c_int(10)
    devices = (DPFPDD_DEV_INFO * 10)()
    result = dpfpdd_dll.dpfpdd_query_devices(byref(device_count), devices)
    if result != 0:
        print(f"[ERROR] Failed to query number of devices. Error Code: {result}")
        return None

    print(f"Number of devices found: {device_count.value}")

    if device_count.value == 0:
        print("[ERROR] No devices found.")
        return None

    # Step 2: Allocate buffer for device info
    devices = (DPFPDD_DEV_INFO * device_count.value)()
    for i in range(device_count.value):
        devices[i].size = ctypes.sizeof(DPFPDD_DEV_INFO)  # Initialize the size field

    # Step 3: Query device info
    result = dpfpdd_dll.dpfpdd_query_devices(byref(device_count), devices)
    if result != 0:
        print(f"[ERROR] Failed to query devices. Error Code: {result}")
        return None

    # Debug: Print device info
    for i in range(device_count.value):
        print(f"Device {i + 1}: {devices[i].name.decode('ascii', errors='replace')}")

    return devices

# Helper Functions
def capture_fingerprint(dev):
    """
    Capture a fingerprint image from the device.
    :param dev: The fingerprint device handle.
    :return: The captured image data (bytes) or None if failed.
    """
    capture_param = DPFPDD_CAPTURE_PARAM()
    capture_param.size = ctypes.sizeof(DPFPDD_CAPTURE_PARAM)
    capture_param.image_fmt = 0x01010007  # ISO format
    capture_param.image_proc = 2  # Enhanced processing
    capture_param.image_res = 500  # 500 DPI

    capture_result = DPFPDD_CAPTURE_RESULT()
    capture_result.size = ctypes.sizeof(DPFPDD_CAPTURE_RESULT)
    image_size = c_uint()

    # First call to get the required buffer size
    result = dpfpdd_dll.dpfpdd_capture(dev, byref(capture_param), 5000, byref(capture_result), byref(image_size), None)
    if result != 0 and result != 0x05BA000D:  # DPFPDD_E_MORE_DATA
        print(f"[ERROR] Failed to get buffer size. Code: 0x{result:08X}")
        return None

    # Allocate buffer with the correct size
    image_buffer = (c_ubyte * image_size.value)()

    # Second call to capture the image
    result = dpfpdd_dll.dpfpdd_capture(dev, byref(capture_param), 5000, byref(capture_result), byref(image_size), image_buffer)
    if result == 0:
        print("Fingerprint captured successfully.")
        print(f"[DEBUG] Captured image size: {image_size.value} bytes")
        
        # Debug: Simpan data gambar mentah ke file untuk inspeksi
        with open("captured_image.raw", "wb") as f:
            f.write(bytes(image_buffer))
        print("[DEBUG] Raw image data saved to 'captured_image.raw'.")
        
        return bytes(image_buffer)
    else:
        print(f"[ERROR] Failed to capture fingerprint. Error Code: {result}")
        return None
         
def create_fmd_from_raw(image_data, width, height, dpi=500, finger_pos=DPFJ_POSITION_UNKNOWN, cbeff_id=0, fmd_type=DPFJ_FMD_ANSI_378_2004):
    """
    Create FMD (Fingerprint Minutiae Data) from raw image data.

    :param image_data: The raw image data (bytes).
    :param width: The width of the image in pixels.
    :param height: The height of the image in pixels.
    :param dpi: The resolution of the image in DPI (default: 500).
    :param finger_pos: The finger position (default: DPFJ_POSITION_UNKNOWN).
    :param cbeff_id: The CBEFF ID (default: 0).
    :param fmd_type: The target FMD format (default: DPFJ_FMD_ANSI_378_2004).
    :return: The FMD data (bytes) or None if failed.
    """
    # Convert image_data to c_ubyte array
    image_data_array = (ctypes.c_ubyte * len(image_data)).from_buffer_copy(image_data)

    # Initialize FMD buffer and size
    fmd_size = ctypes.c_uint(0)  # Initialize size to 0 to determine required size
    fmd = None  # Initialize FMD buffer to None

    # First call to determine required buffer size
    result = dpfj_dll.dpfj_create_fmd_from_raw(
        image_data_array,  # image_data
        len(image_data),   # image_size
        width,             # image_width
        height,            # image_height
        dpi,               # image_dpi
        finger_pos,        # finger_pos
        cbeff_id,         # cbeff_id
        fmd_type,          # fmd_type
        None,              # fmd (None to determine size)
        byref(fmd_size)    # fmd_size (pointer to receive required size)
    )

    if result == DPFJ_E_MORE_DATA:
        print(f"[DEBUG] Required FMD buffer size: {fmd_size.value}")
        # Allocate buffer with the required size
        fmd = (ctypes.c_ubyte * fmd_size.value)()
    else:
        print(f"[ERROR] Failed to determine FMD buffer size. Error Code: {result}")
        print("[DEBUG] Possible causes:")
        print("  - Invalid image data (e.g., not 8 bits per pixel).")
        print("  - Invalid image dimensions or resolution.")
        print("  - Corrupted or incomplete image data.")
        return None

    # Second call to create FMD
    result = dpfj_dll.dpfj_create_fmd_from_raw(
        image_data_array,  # image_data
        len(image_data),   # image_size
        width,             # image_width
        height,            # image_height
        dpi,               # image_dpi
        finger_pos,        # finger_pos
        cbeff_id,         # cbeff_id
        fmd_type,          # fmd_type
        fmd,               # fmd (buffer to store FMD)
        byref(fmd_size)    # fmd_size (pointer to receive actual size)
    )

    # Debug: Print result and output size
    print(f"[DEBUG] dpfj_create_fmd_from_raw result: {result}")
    print(f"[DEBUG] Output FMD size: {fmd_size.value}")

    if result == DPFJ_SUCCESS:
        print("FMD created successfully.")
        return bytes(fmd[:fmd_size.value])
    elif result == DPFJ_E_MORE_DATA:
        print("[ERROR] More data needed. Required buffer size:", fmd_size.value)
        return None
    elif result == DPFJ_E_INVALID_PARAMETER:
        print("[ERROR] Invalid parameter passed to dpfj_create_fmd_from_raw.")
        return None
    else:
        print(f"[ERROR] Failed to create FMD. Error Code: {result}")
        return None
  
def validate_compression_parameters(image_data, width, height, dpi, bpp):
    """
    Validate compression parameters.
    :return: True if parameters are valid, False otherwise.
    """
    if not image_data:
        print("[ERROR] Image data is empty.")
        logging.error("Image data is empty.")
        return False

    if width <= 0 or height <= 0:
        print(f"[ERROR] Invalid image dimensions: width={width}, height={height}.")
        logging.error(f"Invalid image dimensions: width={width}, height={height}.")
        return False

    if dpi < 300 or dpi > 1000:
        print(f"[ERROR] Invalid DPI value: {dpi}. Expected value between 300 and 1000.")
        logging.error(f"Invalid DPI value: {dpi}. Expected value between 300 and 1000.")
        return False

    if bpp != 8:
        print(f"[ERROR] Invalid bits per pixel (bpp): {bpp}. Only 8 bpp is supported.")
        logging.error(f"Invalid bits per pixel (bpp): {bpp}. Only 8 bpp is supported.")
        return False

    print("[DEBUG] Compression parameters are valid.")
    logging.debug("Compression parameters are valid.")
    return True
 
def save_wsq_file(compressed_data, filename):
    """
    Save compressed WSQ data to a file.

    :param compressed_data: The compressed WSQ data (bytes).
    :param filename: The name of the output file.
    """
    try:
        with open(filename, "wb") as f:
            f.write(compressed_data)
        print(f"[DEBUG] WSQ file saved successfully: {filename}")
        logging.debug(f"WSQ file saved successfully: {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save WSQ file: {e}")
        logging.error(f"Failed to save WSQ file: {e}")

def identify_user(dev, database_dir):
    """
    Identify a user by comparing their fingerprint with enrolled templates.

    :param dev: The fingerprint device handle.
    :param database_dir: The directory containing enrolled FMD templates.
    :return: The user ID if a match is found, otherwise None.
    """
    print("Identifying user...")

    # Capture fingerprint image
    image_data = capture_fingerprint(dev)
    if not image_data:
        print("[ERROR] Failed to capture fingerprint.")
        return None

    # Create FMD from raw image data
    fmd_data = create_fmd_from_raw(
        image_data,                # image_data
        width=400,                 # image_width (adjust based on your device)
        height=500,                # image_height (adjust based on your device)
        dpi=500,                   # image_dpi
        finger_pos=DPFJ_POSITION_UNKNOWN,  # finger_pos
        cbeff_id=0,                # cbeff_id
        fmd_type=DPFJ_FMD_ANSI_378_2004  # fmd_type
    )
    if not fmd_data:
        print("[ERROR] Failed to create FMD from raw image data.")
        return None

    # Validate FMD
    if not validate_fmd(fmd_data):
        print("[ERROR] Invalid FMD. Cannot proceed with identification.")
        return None

    # Load all enrolled FMD templates
    enrolled_fmds = []
    user_ids = []
    for filename in os.listdir(database_dir):
        if filename.startswith("fmd_") and filename.endswith(".dat"):
            with open(os.path.join(database_dir, filename), "rb") as f:
                enrolled_fmds.append(f.read())
                user_ids.append(filename.split("_")[1].split(".")[0])  # Extract user ID from filename

    # Compare the extracted FMD with enrolled templates
    for i, enrolled_fmd in enumerate(enrolled_fmds):
        score = compare_fmds(fmd_data, enrolled_fmd)
        if score is not None and score < 100:  # Adjust threshold as needed
            user_id = user_ids[i]
            print(f"Match found! User ID: {user_id}, Score: {score}")
            return user_id

    print("No match found.")
    return None

def compare_fmds(fmd1, fmd2):
    """
    Compare two FMDs and return the dissimilarity score.

    :param fmd1: The first FMD (bytes).
    :param fmd2: The second FMD (bytes).
    :return: The dissimilarity score (0 = match, higher values = no match) or None if failed.
    """
    # Convert FMDs to c_ubyte arrays
    fmd1_array = (ctypes.c_ubyte * len(fmd1)).from_buffer_copy(fmd1)
    fmd2_array = (ctypes.c_ubyte * len(fmd2)).from_buffer_copy(fmd2)

    # Initialize score
    score = c_uint(0)

    # Call dpfj_compare
    result = dpfj_dll.dpfj_compare(
        DPFJ_FMD_ANSI_378_2004,  # fmd1_type
        fmd1_array,              # fmd1
        len(fmd1),               # fmd1_size
        0,                      # fmd1_view_idx
        DPFJ_FMD_ANSI_378_2004,  # fmd2_type
        fmd2_array,              # fmd2
        len(fmd2),               # fmd2_size
        0,                      # fmd2_view_idx
        byref(score)             # score
    )

    if result == DPFJ_SUCCESS:
        print("Comparison successful.")
        print(f"Dissimilarity score: {score.value}")
        return score.value
    else:
        print(f"[ERROR] Failed to compare FMDs. Error Code: {result}")
        return None
    
# Contoh penggunaan compare_fmds untuk diagnostik
def diagnostic_compare(fmd1, fmd2):
    """
    Perform a diagnostic comparison between two FMDs.

    :param fmd1: The first FMD (bytes).
    :param fmd2: The second FMD (bytes).
    """
    score = compare_fmds(fmd1, fmd2)
    if score is not None:
        if score == 0:
            print("Fingerprints match perfectly.")
        elif score == 2147483647:
            print("Fingerprints are completely dissimilar.")
        else:
            print(f"Fingerprints are somewhat similar. Dissimilarity score: {score}")
            # Analisis lebih lanjut berdasarkan skor
            if score <= 2147483:
                print("False Match Rate (FMR): ~0.1%")
            elif score <= 214748:
                print("False Match Rate (FMR): ~0.01%")
            elif score <= 21474:
                print("False Match Rate (FMR): ~0.001%")
            elif score <= 2147:
                print("False Match Rate (FMR): ~0.0001%")
            else:
                print("Fingerprints are very dissimilar.")

def validate_fmd(fmd_data):
    """
    Validate FMD data.

    :param fmd_data: The FMD data (bytes).
    :return: True if FMD is valid, False otherwise.
    """
    if not fmd_data:
        print("[ERROR] FMD data is empty.")
        return False

    # Check if FMD starts with "FMR" (ANSI/ISO FMD header)
    if fmd_data[:3] != b"FMR":
        print("[ERROR] Invalid FMD header. Expected 'FMR'.")
        return False

    print("FMD is valid.")
    return True

def validate_fmd_quality(fmd_data):
    """
    Validate the quality of FMD data.

    :param fmd_data: The FMD data (bytes).
    :return: True if FMD quality is good, False otherwise.
    """
    # Example: Check if FMD size is within expected range
    if len(fmd_data) < 300 or len(fmd_data) > 500:
        print("[ERROR] Invalid FMD size. Expected size between 300 and 500 bytes.")
        return False

    # Example: Check if FMD header is valid
    if fmd_data[:3] != b"FMR":
        print("[ERROR] Invalid FMD header. Expected 'FMR'.")
        return False

    print("FMD quality is good.")
    return True

def validate_image_quality(image_data):
    """
    Validate the quality of the captured fingerprint image.

    :param image_data: The raw image data (bytes).
    :return: True if image quality is good, False otherwise.
    """
    # Example: Check if image size is within expected range
    if len(image_data) < 10000 or len(image_data) > 200046:
        print("[ERROR] Invalid image size. Expected size between 10000 and 50000 bytes.")
        return False

    # Example: Check if image contains enough detail (placeholder logic)
    # You can use image processing libraries like OpenCV for more advanced checks.
    if not has_enough_detail(image_data):
        print("[ERROR] Image does not contain enough detail.")
        return False

    print("Image quality is good.")
    return True

def has_enough_detail(image_data):
    """
    Placeholder function to check if the image contains enough detail.

    :param image_data: The raw image data (bytes).
    :return: True if the image contains enough detail, False otherwise.
    """
    # Implement your logic here (e.g., using OpenCV to analyze image quality).
    return True  # Placeholder

import logging
import json

def setup_logging():
    """
    Set up logging to save process logs to a file.
    """
    logging.basicConfig(
        filename="fingerprint_system.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def save_user_metadata(user_id, metadata):
    """
    Save user metadata to a JSON file.

    :param user_id: The ID of the user.
    :param metadata: A dictionary containing user metadata.
    """
    filename = f"user_{user_id}.json"
    with open(filename, "w") as f:
        json.dump(metadata, f)
    print(f"User metadata saved to {filename}.")

def compress_fid(fid_data, fid_type=DPFJ_FID_ANSI_381_2004, bitrate_x100=75, tolerance_aw=10, compression_alg=DPFJ_COMPRESSION_WSQ_NIST):
    """
    Compress FID data using WSQ algorithm.

    :param fid_data: The FID data (bytes).
    :param fid_type: The FID format (default: ANSI 381-2004).
    :param bitrate_x100: The target bitrate multiplied by 100 (default: 75 for 0.75 bpp).
    :param tolerance_aw: The tolerance for Aware WSQ (default: 10%).
    :param compression_alg: The compression algorithm (default: NIST WSQ).
    :return: Compressed FID data (bytes) or None if failed.
    """
    # Start compression
    result = dpfj_compression_dll.dpfj_start_compression()
    if result != DPFJ_SUCCESS:
        print(f"[ERROR] Failed to start compression. Error Code: {result}")
        return None

    # Set bitrate
    result = dpfj_compression_dll.dpfj_set_wsq_bitrate(bitrate_x100, tolerance_aw)
    if result != DPFJ_SUCCESS:
        print(f"[ERROR] Failed to set bitrate. Error Code: {result}")
        dpfj_compression_dll.dpfj_finish_compression()
        return None

    # Compress FID
    fid_array = (ctypes.c_ubyte * len(fid_data)).from_buffer_copy(fid_data)
    result = dpfj_compression_dll.dpfj_compress_fid(fid_type, fid_array, len(fid_data), compression_alg)
    if result != DPFJ_SUCCESS:
        print(f"[ERROR] Failed to compress FID. Error Code: {result}")
        dpfj_compression_dll.dpfj_finish_compression()
        return None

    # Get processed data (compressed FID)
    compressed_data = get_processed_data()
    if not compressed_data:
        print("[ERROR] Failed to retrieve compressed data.")
        dpfj_compression_dll.dpfj_finish_compression()
        return None

    # Finish compression
    dpfj_compression_dll.dpfj_finish_compression()

    return compressed_data

def initialize_compression():
    """
    Initialize the compression library.
    :return: True if successful, False otherwise.
    """
    result = dpfj_compression_dll.dpfj_start_compression()
    if result != DPFJ_SUCCESS:
        print(f"[ERROR] Failed to initialize compression library. Error Code: {result}")
        logging.error(f"Failed to initialize compression library. Error Code: {result}")
        return False
    else:
        print("[DEBUG] Compression library initialized successfully.")
        logging.debug("Compression library initialized successfully.")
        return True
     
def compress_raw(image_data, width, height, dpi=500, bpp=8):
    """
    Compress raw fingerprint image using WSQ algorithm with the wsq library.
    
    :param image_data: Raw image data (bytes).
    :param width: Width of the image in pixels.
    :param height: Height of the image in pixels.
    :param dpi: Resolution of the image in DPI (default: 500).
    :param bpp: Bits per pixel (default: 8).
    :return: Compressed image data (bytes) or None if failed.
    """
    try:
        # Validasi ukuran data gambar
        expected_size = width * height
        if len(image_data) != expected_size:
            print(f"[ERROR] Invalid image data size. Expected {expected_size} bytes, got {len(image_data)} bytes.")
            return None

        # Convert raw image data to a PIL Image object
        img = Image.frombytes("L", (width, height), image_data)

        # Debug: Simpan gambar sebelum kompresi ke file PNG
        img.save("before_compression.png")
        print("[DEBUG] Image saved to 'before_compression.png' before compression.")

        # Save the image to a BytesIO object in WSQ format
        with io.BytesIO() as output:
            img.save(output, format="WSQ")
            compressed_data = output.getvalue()

        print("[DEBUG] Image compressed successfully using WSQ.")
        return compressed_data
    except Exception as e:
        print(f"[ERROR] Failed to compress image using WSQ: {e}")
        return None
         
def get_processed_data():
    """
    Retrieve the processed data (compressed or decompressed).
    :return: Processed data (bytes) or None if failed.
    """
    # First call: Get the required buffer size
    image_size = ctypes.c_uint(0)
    result = dpfj_compression_dll.dpfj_get_processed_data(None, ctypes.byref(image_size))
    
    if result == DPFJ_E_MORE_DATA:
        print(f"[DEBUG] Required buffer size: {image_size.value} bytes")
        logging.debug(f"Required buffer size: {image_size.value} bytes")
    elif result != DPFJ_SUCCESS:
        print(f"[ERROR] Failed to get processed data size. Error Code: {result}")
        logging.error(f"Failed to get processed data size. Error Code: {result}")
        return None

    # Allocate buffer with the required size
    image_data = (ctypes.c_ubyte * image_size.value)()

    # Second call: Retrieve the processed data
    result = dpfj_compression_dll.dpfj_get_processed_data(image_data, ctypes.byref(image_size))
    if result == DPFJ_SUCCESS:
        print("Processed data retrieved successfully.")
        logging.debug("Processed data retrieved successfully.")
        return bytes(image_data[:image_size.value])
    else:
        print(f"[ERROR] Failed to retrieve processed data. Error Code: {result}")
        logging.error(f"Failed to retrieve processed data. Error Code: {result}")
        return None
    
def enroll_user(dev, user_id, num_scans=4):
    print(f"Enrolling user {user_id}...")

    # Start enrollment
    result = dpfj_dll.dpfj_start_enrollment(DPFJ_FMD_ANSI_378_2004)
    if result != DPFJ_SUCCESS:
        print(f"[ERROR] Failed to start enrollment. Error Code: {result}")
        logging.error(f"Failed to start enrollment. Error Code: {result}")
        return False
    else:
        print("Enrollment started successfully.")
        logging.debug("Enrollment started successfully.")

    # Capture and add multiple fingerprints
    for i in range(num_scans):
        print(f"Capture fingerprint {i + 1}...")
        image_data = capture_fingerprint(dev)
        if not image_data:
            print("[ERROR] Failed to capture fingerprint.")
            logging.error("Failed to capture fingerprint.")
            dpfj_dll.dpfj_finish_enrollment()  # Clean up enrollment
            return False

        # Validate image quality before compression
        if not validate_image_quality(image_data):
            print("[ERROR] Image quality is poor. Skipping this scan.")
            logging.error("Image quality is poor. Skipping this scan.")
            continue

        # Extract raw image data
        raw_image_data = extract_raw_image(image_data, width=400, height=500)
        if not raw_image_data:
            print("[ERROR] Failed to extract raw image data.")
            logging.error("Failed to extract raw image data.")
            continue

        # Log raw image data size
        logging.debug(f"Raw image data size: {len(raw_image_data)}")

        # Compress the raw image using WSQ
        compressed_data = compress_raw(
            raw_image_data,  # Raw image data
            width=400,       # Image width
            height=500,      # Image height
            dpi=500,         # Image resolution
            bpp=8            # Bits per pixel
        )
        if compressed_data:
            save_wsq_file(compressed_data, f"compressed_scan_{i + 1}.wsq")
            print(f"Compressed image saved for user {user_id}, scan {i + 1}.")
            logging.debug(f"Compressed image saved for user {user_id}, scan {i + 1}.")
        else:
            print(f"[ERROR] Failed to compress image for scan {i + 1}.")
            logging.error(f"Failed to compress image for scan {i + 1}.")

    # Finish enrollment
    result = dpfj_dll.dpfj_finish_enrollment()
    if result != DPFJ_SUCCESS:
        print(f"[ERROR] Failed to finish enrollment. Error Code: {result}")
        logging.error(f"Failed to finish enrollment. Error Code: {result}")
        return False
    else:
        print("Enrollment finished successfully.")
        logging.debug("Enrollment finished successfully.")
        return True
           
def extract_raw_image(image_data, width=400, height=500):
    """
    Extract raw image data from ISO/ANSI formatted data.
    :param image_data: The image data with ISO/ANSI header (bytes).
    :param width: Expected width of the image in pixels.
    :param height: Expected height of the image in pixels.
    :return: Raw image data (bytes) or None if failed.
    """
    # Hitung ukuran data gambar yang diharapkan
    expected_size = width * height

    # Cari posisi awal data gambar mentah
    header_size = len(image_data) - expected_size

    if header_size < 0:
        print(f"[ERROR] Image data is too small. Expected at least {expected_size} bytes, got {len(image_data)} bytes.")
        return None

    # Ekstrak data gambar mentah
    raw_image_data = image_data[header_size:]

    # Validasi ukuran data gambar
    if len(raw_image_data) != expected_size:
        print(f"[ERROR] Invalid raw image data size. Expected {expected_size} bytes, got {len(raw_image_data)} bytes.")
        return None

    print(f"[DEBUG] Raw image data size: {len(raw_image_data)} bytes")

    # Debug: Simpan data gambar mentah ke file untuk inspeksi
    with open("extracted_image.raw", "wb") as f:
        f.write(raw_image_data)
    print("[DEBUG] Extracted raw image data saved to 'extracted_image.raw'.")

    return raw_image_data

def expand_raw(compressed_data):
    """
    Decompress WSQ image data to raw image using the wsq library.
    
    :param compressed_data: Compressed WSQ image data (bytes).
    :return: A dictionary containing the decompressed image data and metadata, or None if failed.
    """
    try:
        # Load the WSQ image from bytes
        img = Image.open(io.BytesIO(compressed_data))

        # Convert the image to raw data
        raw_data = img.tobytes()

        # Get image metadata
        width, height = img.size
        dpi = img.info.get("dpi", (500, 500))[0]  # Default DPI if not available
        bpp = 8  # WSQ images are typically 8-bit grayscale

        print("[DEBUG] Image decompressed successfully using WSQ.")
        return {
            "data": raw_data,
            "width": width,
            "height": height,
            "dpi": dpi,
            "bpp": bpp
        }
    except Exception as e:
        print(f"[ERROR] Failed to decompress image using WSQ: {e}")
        return None
    
# Main Program
if __name__ == "__main__":
    # Initialize DPFPDD
    setup_logging()
    result = dpfpdd_dll.dpfpdd_init()
    if result != 0:
        print(f"[ERROR] Failed to initialize DPFPDD. Error Code: {result}")
        exit(1)
    else:
        print("DPFPDD initialized successfully.")

    # Query and open device
    devices = query_devices()
    if not devices:
        print("[ERROR] No devices available.")
        dpfpdd_dll.dpfpdd_exit()
        exit(1)

    # Open the first device
    dev = POINTER(DPFPDD_DEV)()
    device_name = devices[0].name.decode("ascii", errors='replace')
    result = dpfpdd_dll.dpfpdd_open(device_name.encode('ascii'), byref(dev))
    if result != 0:
        print(f"[ERROR] Failed to open device. Error Code: {result}")
        dpfpdd_dll.dpfpdd_exit()
        exit(1)
    else:
        print(f"Device '{device_name}' opened successfully.")

    # Enrollment
    enroll_user(dev, user_id="001")
    user_metadata = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "enrollment_date": "2023-10-01"
    }
    save_user_metadata("001", user_metadata)

    # Cleanup
    dpfpdd_dll.dpfpdd_close(dev)
    dpfpdd_dll.dpfpdd_exit()
