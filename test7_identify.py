import ctypes
from ctypes import c_int, c_uint, POINTER, Structure, c_void_p, c_char_p, c_ubyte, byref
import numpy as np
from PIL import Image
import time

# Load the DPFPDD and DPFJ DLLs
dpfpdd_dll = ctypes.WinDLL("dpfpdd.dll")
dpfj_dll = ctypes.WinDLL("dpfj.dll")

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

# Define DPFJ_FMD_FORMAT constants
DPFJ_FMD_ANSI_378_2004 = 0x001B0001
DPFJ_FMD_ISO_19794_2_2005 = 0x01010001
DPFJ_FMD_DP_PRE_REG_FEATURES = 0
DPFJ_FMD_DP_REG_FEATURES = 1
DPFJ_FMD_DP_VER_FEATURES = 2

# Define DPFJ_FID_FORMAT constants
DPFJ_FID_ANSI_381_2004 = 0x001B0401
DPFJ_FID_ISO_19794_4_2005 = 0x01010007

# Define DPFJ_FINGER_POSITION type
DPFJ_FINGER_POSITION = c_int

# Define DPFJ_FMD_FORMAT type
DPFJ_FMD_FORMAT = c_int

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

# Define DPFJ_VER_INFO structure
class DPFJ_VER_INFO(Structure):
    _fields_ = [
        ("major", c_int),       # major version number
        ("minor", c_int),       # minor version number
        ("maintanance", c_int)  # maintenance or revision number
    ]

# Define DPFJ_VERSION structure
class DPFJ_VERSION(Structure):
    _fields_ = [
        ("size", c_uint),       # Size of the structure, in bytes
        ("lib_ver", DPFJ_VER_INFO),  # File version of the library/SDK
        ("api_ver", DPFJ_VER_INFO)   # Version of the API
    ]

# Define DPFJ_CANDIDATE structure
class DPFJ_CANDIDATE(Structure):
    _fields_ = [
        ("size", c_uint),      # Size of the structure, in bytes
        ("fmd_idx", c_uint),   # Index of the FMD in the input array
        ("view_idx", c_uint)   # Index of the view in the FMD
    ]

# Define the dpfj_version function
dpfj_dll.dpfj_version.argtypes = [POINTER(DPFJ_VERSION)]
dpfj_dll.dpfj_version.restype = c_int  # Return type is int

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

# Define dpfj_create_fmd_from_fid function
dpfj_dll.dpfj_create_fmd_from_fid.argtypes = [
    DPFJ_FID_FORMAT,                 # fid_type
    ctypes.POINTER(ctypes.c_ubyte),  # fid
    ctypes.c_uint,                   # fid_size
    DPFJ_FMD_FORMAT,                 # fmd_type
    ctypes.POINTER(ctypes.c_ubyte),  # fmd
    ctypes.POINTER(ctypes.c_uint)    # fmd_size
]
dpfj_dll.dpfj_create_fmd_from_fid.restype = ctypes.c_int

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

def identify_fingerprint(fmd1, fmd1_view_idx, fmds, threshold_score=100, max_candidates=10):
    """
    Identify a fingerprint by comparing it against an array of enrolled FMDs.

    :param fmd1: The FMD to be identified (bytes).
    :param fmd1_view_idx: The view index in the FMD.
    :param fmds: A list of enrolled FMDs (list of bytes).
    :param threshold_score: The threshold for False Positive Identification Rate.
    :param max_candidates: The maximum number of candidates to return.
    :return: A list of candidates (DPFJ_CANDIDATE structures) or None if failed.
    """
    # Convert fmd1 to c_ubyte array
    fmd1_array = (ctypes.c_ubyte * len(fmd1)).from_buffer_copy(fmd1)

    # Convert fmds to an array of c_ubyte pointers
    fmds_arrays = [(ctypes.c_ubyte * len(fmd)).from_buffer_copy(fmd) for fmd in fmds]
    fmds_ptrs = (ctypes.POINTER(ctypes.c_ubyte) * len(fmds))(*[ctypes.cast(fmd, ctypes.POINTER(ctypes.c_ubyte)) for fmd in fmds_arrays])

    # Convert fmds sizes to c_uint array
    fmds_sizes = (c_uint * len(fmds))(*[len(fmd) for fmd in fmds])

    # Initialize candidates array
    candidates = (DPFJ_CANDIDATE * max_candidates)()
    candidate_cnt = c_uint(max_candidates)

    # Call dpfj_identify
    result = dpfj_dll.dpfj_identify(
        DPFJ_FMD_ANSI_378_2004,  # fmd1_type
        fmd1_array,              # fmd1
        len(fmd1),               # fmd1_size
        fmd1_view_idx,           # fmd1_view_idx
        DPFJ_FMD_ANSI_378_2004,  # fmds_type
        len(fmds),               # fmds_cnt
        fmds_ptrs,               # fmds
        fmds_sizes,              # fmds_size
        threshold_score,         # threshold_score
        byref(candidate_cnt),    # candidate_cnt
        candidates               # candidates
    )

    if result == DPFJ_SUCCESS:
        print("Identification successful.")
        print(f"Number of candidates found: {candidate_cnt.value}")
        return candidates[:candidate_cnt.value]
    else:
        print(f"[ERROR] Failed to identify fingerprint. Error Code: {result}")
        return None

# Helper Functions
def capture_fingerprint(dev):
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
    # Convert image_data to c_ubyte array
    image_data_array = (ctypes.c_ubyte * len(image_data)).from_buffer_copy(image_data)

    # Initialize FMD buffer and size
    fmd = (ctypes.c_ubyte * 65536)()  # Buffer for FMD (max size)
    fmd_size = ctypes.c_uint(65536)   # Buffer size

    # Call dpfj_create_fmd_from_raw
    result = dpfj_dll.dpfj_create_fmd_from_raw(
        image_data_array, len(image_data), width, height, dpi,
        finger_pos, cbeff_id, fmd_type,
        fmd, byref(fmd_size)
    )

    if result == 0:  # DPFJ_SUCCESS
        print("FMD created successfully.")
        return bytes(fmd[:fmd_size.value])
    elif result == 0x05BA000D:  # DPFJ_E_MORE_DATA
        print("[ERROR] More data needed. Required buffer size:", fmd_size.value)
        return None
    else:
        print(f"[ERROR] Failed to create FMD. Error Code: {result}")
        return None
    
def create_fmd_from_fid(fid_data, fid_type=DPFJ_FID_ANSI_381_2004, fmd_type=DPFJ_FMD_ANSI_378_2004):
    # Periksa data FID
    if not fid_data:
        print("[ERROR] FID data is empty.")
        return None

    # Convert fid_data to c_ubyte array
    fid_data_array = (ctypes.c_ubyte * len(fid_data)).from_buffer_copy(fid_data)

    # Initialize FMD buffer and size
    fmd = (ctypes.c_ubyte * 65536)()  # Buffer for FMD (max size)
    fmd_size = ctypes.c_uint(65536)   # Buffer size

    # Call dpfj_create_fmd_from_fid
    result = dpfj_dll.dpfj_create_fmd_from_fid(
        fid_type, fid_data_array, len(fid_data),
        fmd_type, fmd, byref(fmd_size)
    )

    if result == 0:  # DPFJ_SUCCESS
        print("FMD created successfully.")
        return bytes(fmd[:fmd_size.value])
    elif result == 0x05BA000D:  # DPFJ_E_MORE_DATA
        print("[ERROR] More data needed. Required buffer size:", fmd_size.value)
        return None
    else:
        print(f"[ERROR] Failed to create FMD. Error Code: {result}")
        return None
          
def enroll_fingerprint(dev):
    try:
        # Step 1: Start enrollment
        result = dpfj_dll.dpfj_start_enrollment(DPFJ_FMD_ANSI_378_2004)
        if result != DPFJ_SUCCESS:
            if result == DPFJ_E_INVALID_PARAMETER:
                print("[ERROR] Invalid FMD type.")
            elif result == DPFJ_E_ENROLLMENT_IN_PROGRESS:
                print("[ERROR] Another enrollment is in progress.")
            else:
                print(f"[ERROR] Failed to start enrollment. Error Code: {result}")
            return None
        else:
            print("Enrollment started successfully.")

        # Step 2: Capture and add fingerprints to enrollment
        for i in range(5):  # Capture up to 5 fingerprints
            print(f"Capture fingerprint {i + 1}...")
            image_data = capture_fingerprint(dev)
            if not image_data:
                print("[ERROR] Failed to capture fingerprint.")
                return None

            # Step 3: Create FMD from raw image
            fmd = create_fmd_from_raw(image_data, width=400, height=500, dpi=500)
            if not fmd:
                return None

            # Debug: Print FMD size and first few bytes
            print(f"[DEBUG] FMD Size: {len(fmd)} bytes")
            print(f"[DEBUG] FMD Data (first 16 bytes): {fmd[:16].hex()}")

            # Step 4: Add FMD to enrollment
            fmd_array = (ctypes.c_ubyte * len(fmd)).from_buffer_copy(fmd)
            result = dpfj_dll.dpfj_add_to_enrollment(
                DPFJ_FMD_ANSI_378_2004,  # fmd_type
                fmd_array,               # fmd
                len(fmd),                # fmd_size
                0                        # fmd_view_idx
            )
            if result == DPFJ_SUCCESS:
                print("FMD added to enrollment. Enrollment is ready.")
                break  # Exit loop if enrollment is ready
            elif result == DPFJ_E_MORE_DATA:
                print("FMD added to enrollment. More FMDs needed.")
            elif result == DPFJ_E_ENROLLMENT_NOT_STARTED:
                print("[ERROR] Enrollment not started.")
                return None
            else:
                print(f"[ERROR] Failed to add FMD to enrollment. Error Code: {result}")
                return None

        # Step 5: Create enrollment FMD
        enrollment_fmd = (ctypes.c_ubyte * 65536)()  # Buffer for enrollment FMD
        enrollment_fmd_size = ctypes.c_uint(65536)   # Buffer size
        result = dpfj_dll.dpfj_create_enrollment_fmd(enrollment_fmd, byref(enrollment_fmd_size))
        if result == DPFJ_SUCCESS:
            print("Enrollment FMD created successfully.")
            print(f"[DEBUG] Enrollment FMD Size: {enrollment_fmd_size.value} bytes")
            print(f"[DEBUG] Enrollment FMD Data (first 16 bytes): {bytes(enrollment_fmd[:16]).hex()}")
            return bytes(enrollment_fmd[:enrollment_fmd_size.value])
        elif result == DPFJ_E_MORE_DATA:
            print("[ERROR] More data needed. Required buffer size:", enrollment_fmd_size.value)
            return None
        elif result == DPFJ_E_ENROLLMENT_NOT_STARTED:
            print("[ERROR] Enrollment not started.")
            return None
        elif result == 96076079:  # URU_E_ENROLLMENT_NOT_READY
            print("[ERROR] Enrollment not ready. More FMDs needed.")
            return None
        else:
            print(f"[ERROR] Failed to create enrollment FMD. Error Code: {result}")
            return None

    finally:
        # Step 6: Finish enrollment (always executed)
        result = dpfj_dll.dpfj_finish_enrollment()
        if result != DPFJ_SUCCESS:
            print(f"[ERROR] Failed to finish enrollment. Error Code: {result}")
        else:
            print("Enrollment finished successfully.")

def get_dpfj_version():
    # Create an instance of DPFJ_VERSION
    version = DPFJ_VERSION()
    version.size = ctypes.sizeof(DPFJ_VERSION)  # Set the size of the structure

    # Call the dpfj_version function
    result = dpfj_dll.dpfj_version(ctypes.byref(version))

    if result == 0:  # DPFJ_SUCCESS
        print("Version information acquired successfully.")
        print(f"Library Version: {version.lib_ver.major}.{version.lib_ver.minor}.{version.lib_ver.maintanance}")
        print(f"API Version: {version.api_ver.major}.{version.api_ver.minor}.{version.api_ver.maintanance}")
    else:
        print(f"[ERROR] Failed to acquire version information. Error Code: {result}")

    return version

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

    # Perform enrollment
    enrollment_fmd = enroll_fingerprint(dev)
    if enrollment_fmd:
        print("Enrollment successful. Enrollment FMD saved.")
        with open("enrollment_fmd.dat", "wb") as f:
            f.write(enrollment_fmd)

    # Capture a new fingerprint for identification
    print("Capture a new fingerprint for identification...")
    new_fingerprint = capture_fingerprint(dev)
    if new_fingerprint:
        # Create FMD from the new fingerprint
        new_fmd = create_fmd_from_raw(new_fingerprint, width=400, height=500, dpi=500)
        if new_fmd:
            # Load enrolled FMDs (for example, from a file or database)
            enrolled_fmds = [enrollment_fmd]  # Use the previously enrolled FMD

            # Perform identification
            candidates = identify_fingerprint(new_fmd, fmd1_view_idx=0, fmds=enrolled_fmds)
            if candidates:
                for i, candidate in enumerate(candidates):
                    print(f"Candidate {i + 1}: FMD Index = {candidate.fmd_idx}, View Index = {candidate.view_idx}")

    # Cleanup
    dpfpdd_dll.dpfpdd_close(dev)
    dpfpdd_dll.dpfpdd_exit()