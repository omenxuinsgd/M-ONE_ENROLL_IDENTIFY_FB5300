import ctypes
from ctypes import c_int, c_uint, POINTER, Structure, c_void_p, c_char_p, c_ubyte, byref
import os

# Load the DPFPDD and DPFJ DLLs
dpfpdd_dll = ctypes.WinDLL("dpfpdd.dll")
dpfj_dll = ctypes.WinDLL("dpfj.dll")

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

def enroll_user(dev, user_id, num_scans=4):
    """
    Enroll a user by capturing multiple fingerprints and creating a strong FMD template.

    :param dev: The fingerprint device handle.
    :param user_id: The ID of the user to enroll.
    :param num_scans: The number of fingerprint scans required for enrollment (default: 4).
    :return: True if enrollment is successful, False otherwise.
    """
    print(f"Enrolling user {user_id}...")

    # Start enrollment
    result = dpfj_dll.dpfj_start_enrollment(DPFJ_FMD_ANSI_378_2004)
    if result != DPFJ_SUCCESS:
        print(f"[ERROR] Failed to start enrollment. Error Code: {result}")
        return False
    else:
        print("Enrollment started successfully.")

    # Capture and add multiple fingerprints
    for i in range(num_scans):
        print(f"Capture fingerprint {i + 1}...")
        image_data = capture_fingerprint(dev)
        if not image_data:
            print("[ERROR] Failed to capture fingerprint.")
            dpfj_dll.dpfj_finish_enrollment()  # Clean up enrollment
            return False

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
            dpfj_dll.dpfj_finish_enrollment()  # Clean up enrollment
            return False
        
        print(f"[DEBUG] FMD Size: {len(fmd_data)} bytes")
        print(f"[DEBUG] FMD Header: {fmd_data[:16].hex()}")

        if not validate_fmd_quality(fmd_data):
            print("[ERROR] FMD quality is poor. Skipping this scan.")
            continue

        # Add FMD to enrollment
        fmd_array = (ctypes.c_ubyte * len(fmd_data)).from_buffer_copy(fmd_data)
        result = dpfj_dll.dpfj_add_to_enrollment(
            DPFJ_FMD_ANSI_378_2004,  # fmd_type
            fmd_array,               # fmd
            len(fmd_data),           # fmd_size
            0                        # fmd_view_idx
        )
        if result == DPFJ_SUCCESS:
            print("FMD added to enrollment.")
        elif result == DPFJ_E_MORE_DATA:
            print("More FMDs needed for enrollment.")
        else:
            print(f"[ERROR] Failed to add FMD to enrollment. Error Code: {result}")
            dpfj_dll.dpfj_finish_enrollment()  # Clean up enrollment
            return False

    # Create enrollment FMD
    enrollment_fmd = (ctypes.c_ubyte * 65536)()  # Buffer for enrollment FMD
    enrollment_fmd_size = ctypes.c_uint(65536)   # Buffer size
    result = dpfj_dll.dpfj_create_enrollment_fmd(enrollment_fmd, byref(enrollment_fmd_size))
    if result == DPFJ_SUCCESS:
        print("Enrollment FMD created successfully.")
        print(f"[DEBUG] Enrollment FMD Size: {enrollment_fmd_size.value} bytes")
        print(f"[DEBUG] Enrollment FMD Data (first 16 bytes): {bytes(enrollment_fmd[:16]).hex()}")

        # Save enrollment FMD to file
        with open(f"fmd_{user_id}.dat", "wb") as f:
            f.write(bytes(enrollment_fmd[:enrollment_fmd_size.value]))
        print(f"Enrollment FMD saved for user {user_id}.")
    else:
        print(f"[ERROR] Failed to create enrollment FMD. Error Code: {result}")
        dpfj_dll.dpfj_finish_enrollment()  # Clean up enrollment
        return False

    # Finish enrollment
    result = dpfj_dll.dpfj_finish_enrollment()
    if result != DPFJ_SUCCESS:
        print(f"[ERROR] Failed to finish enrollment. Error Code: {result}")
        return False
    else:
        print("Enrollment finished successfully.")
        return True
       
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
        return score.value
    else:
        print(f"[ERROR] Failed to compare FMDs. Error Code: {result}")
        return None
    
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

import json

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

# Main Program
if __name__ == "__main__":
    # Initialize DPFPDD
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
    enroll_user(dev, user_id="001", num_scans=5)
    # Example usage
    user_metadata = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "enrollment_date": "2023-10-01"
    }
    save_user_metadata("001", user_metadata)

    # Identification
    identified_user = identify_user(dev, database_dir=".")
    if identified_user:
        print(f"User identified: {identified_user}")
    else:
        print("User not identified.")

    # Cleanup
    dpfpdd_dll.dpfpdd_close(dev)
    dpfpdd_dll.dpfpdd_exit()