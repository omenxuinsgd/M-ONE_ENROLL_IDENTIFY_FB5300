import sys
import ctypes
from ctypes import c_int, c_uint, POINTER, Structure, c_void_p, c_char_p, c_ubyte, byref
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, 
                             QMessageBox, QStatusBar, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sqlite3
import logging
from PIL import Image
import io
import os
import wsq
import time

# Setup logging
logging.basicConfig(
    filename="fingerprint_system.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==================== Fingerprint Device Structures and Constants ====================
class DPFPDD_VER_INFO(Structure):
    _fields_ = [("major", c_int), ("minor", c_int), ("maintenance", c_int)]

class DPFPDD_VERSION(Structure):
    _fields_ = [("size", c_uint), ("lib_ver", DPFPDD_VER_INFO), ("api_ver", DPFPDD_VER_INFO)]

class DPFPDD_DEV_INFO(Structure):
    _fields_ = [("size", ctypes.c_uint), ("name", ctypes.c_char * 256)]

class DPFPDD_DEV(Structure):
    pass

class DPFPDD_DEV_STATUS(Structure):
    _fields_ = [("size", c_uint), ("status", c_uint), ("finger_detected", c_int), ("data", ctypes.c_ubyte * 1)]

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

# Define DPFPDD_STATUS constants
DPFPDD_STATUS_READY = 0
DPFPDD_STATUS_BUSY = 1
DPFPDD_STATUS_NEED_CALIBRATION = 2
DPFPDD_STATUS_FAILURE = 3

# Define DPFJ_FINGER_POSITION type
DPFJ_FINGER_POSITION = c_int

# Define DPFJ_FID_FORMAT type
DPFJ_FID_FORMAT = c_int

# ==================== Fingerprint Thread Workers ====================
class FingerprintCaptureThread(QThread):
    capture_complete = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    status_update = pyqtSignal(str)
    identification_complete = pyqtSignal(bool, str, str, str)  # success, message, name, nik
    # status_update = pyqtSignal(str)
    finger_status = pyqtSignal(bool)

    def __init__(self, dev):
        super().__init__()
        self.dev = dev

    def run(self):
        try:
            self.status_update.emit("Initializing fingerprint capture...")
            
            # Setup capture parameters
            capture_param = DPFPDD_CAPTURE_PARAM()
            capture_param.size = ctypes.sizeof(DPFPDD_CAPTURE_PARAM)
            capture_param.image_fmt = 0x01010007  # ISO format
            capture_param.image_proc = 2  # Enhanced processing
            capture_param.image_res = 500  # 500 DPI

            capture_result = DPFPDD_CAPTURE_RESULT()
            capture_result.size = ctypes.sizeof(DPFPDD_CAPTURE_RESULT)
            image_size = c_uint()

            # First call to get buffer size
            result = dpfpdd_dll.dpfpdd_capture(
                self.dev, byref(capture_param), 5000, 
                byref(capture_result), byref(image_size), None
            )
            
            if result != 0 and result != DPFJ_E_MORE_DATA:
                print(f"[ERROR] Failed to get buffer size. Code: 0x{result:08X}")
                return None

            # Allocate buffer
            image_buffer = (c_ubyte * image_size.value)()
            
            # Second call to capture image
            result = dpfpdd_dll.dpfpdd_capture(
                self.dev, byref(capture_param), 5000,
                byref(capture_result), byref(image_size), image_buffer
            )
            
            if result == 0:
                self.capture_complete.emit(bytes(image_buffer))
                print("Fingerprint captured successfully.")
                print(f"[DEBUG] Captured image size: {image_size.value} bytes") 
                # Debug: Simpan data gambar mentah ke file untuk inspeksi
                with open("captured_image.raw", "wb") as f:
                    f.write(bytes(image_buffer))
                print("[DEBUG] Raw image data saved to 'captured_image.raw'.")
                
                return bytes(image_buffer)       
            else:
                self.error_occurred.emit(f"Capture failed: 0x{result:08X}")
                print(f"[ERROR] Failed to capture fingerprint. Error Code: {result}")
                return None
                
        except Exception as e:
            self.error_occurred.emit(f"Capture exception: {str(e)}")

class EnrollmentThread(QThread):
    update_progress = pyqtSignal(int, str)
    enrollment_complete = pyqtSignal(bool, str)
    scan_complete = pyqtSignal(int, bool)

    def __init__(self, dev, user_id, name, nik, num_scans=4):
        super().__init__()
        self.dev = dev
        self.user_id = user_id
        self.name = name
        self.nik = nik
        self.num_scans = num_scans

    def run(self):
        print(f"Enrolling user {self.user_id}...")
        try:
            conn = sqlite3.connect('fingerprint_enrollment.db')
            cursor = conn.cursor()

            # Start a transaction
            conn.execute("BEGIN TRANSACTION")
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE user_id = ?", (self.user_id,))
            if cursor.fetchone():
                self.enrollment_complete.emit(False, f"User ID {self.user_id} already exists")
                print(f"[ERROR] User ID {self.user_id} already exists.")
                return False

            # Insert user data
            cursor.execute("INSERT INTO users (user_id, name, nik) VALUES (?, ?, ?)", 
                          (self.user_id, self.name, self.nik))
            
            successful_scans = 0
            for i in range(self.num_scans):
                print(f"Capture fingerprint {i + 1}...")
                self.update_progress.emit(i+1, f"Capturing fingerprint {i+1} of {self.num_scans}")
                
                # Capture fingerprint
                image_data = self.capture_fingerprint()
                if not image_data:
                    print("[ERROR] Failed to capture fingerprint.")
                    self.scan_complete.emit(i+1, False)
                    continue

                # Validate image quality
                if not self.validate_image_quality(image_data):
                    print("[ERROR] Image quality is poor. Skipping this scan.")
                    continue

                # Process image
                raw_image = self.extract_raw_image(image_data)
                if not raw_image:
                    self.scan_complete.emit(i+1, False)
                    print("[ERROR] Failed to extract raw image data.")
                    continue

                # Compress image
                compressed_data = self.compress_raw(raw_image)
                if compressed_data:
                    # Save compressed fingerprint to the database
                    cursor.execute("INSERT INTO fingerprints (user_id, fingerprint) VALUES (?, ?)", 
                              (self.user_id, compressed_data))
                    print(f"Compressed image saved for user {self.user_id}, scan {i + 1}.")
                    self.scan_complete.emit(i+1, True)
                else:
                    print(f"[ERROR] Failed to compress image for scan {i + 1}.")
                    self.scan_complete.emit(i+1, False)
                successful_scans += 1

            conn.commit()
            
            if successful_scans > 0:
                self.enrollment_complete.emit(True, f"Enrolled {successful_scans} fingerprints")
            else:
                self.enrollment_complete.emit(False, "No successful scans")
                
        except Exception as e:
            conn.rollback()
            self.enrollment_complete.emit(False, f"Database error: {str(e)}")
        finally:
            conn.close()
    
    # Fungsi untuk memvalidasi kualitas gambar menggunakan OpenCV
    def validate_image_quality(self, image_data):
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
        if not self.has_enough_detail(image_data):
            print("[ERROR] Image does not contain enough detail.")
            return False

        print("Image quality is good.")
        return True
    
    def has_enough_detail(self, image_data):
        """
        Placeholder function to check if the image contains enough detail.

        :param image_data: The raw image data (bytes).
        :return: True if the image contains enough detail, False otherwise.
        """
        # Implement your logic here (e.g., using OpenCV to analyze image quality).
        return True  # Placeholder

    def capture_fingerprint(self):
        """Capture fingerprint using device"""
        try:
            capture_param = DPFPDD_CAPTURE_PARAM()
            capture_param.size = ctypes.sizeof(DPFPDD_CAPTURE_PARAM)
            capture_param.image_fmt = 0x01010007
            capture_param.image_proc = 2
            capture_param.image_res = 500

            capture_result = DPFPDD_CAPTURE_RESULT()
            capture_result.size = ctypes.sizeof(DPFPDD_CAPTURE_RESULT)
            image_size = c_uint()

            # Get buffer size
            result = dpfpdd_dll.dpfpdd_capture(
                self.dev, byref(capture_param), 5000,
                byref(capture_result), byref(image_size), None
            )
            if result != 0 and result != DPFJ_E_MORE_DATA:
                return None

            # Capture image
            image_buffer = (c_ubyte * image_size.value)()
            result = dpfpdd_dll.dpfpdd_capture(
                self.dev, byref(capture_param), 5000,
                byref(capture_result), byref(image_size), image_buffer
            )
            return bytes(image_buffer) if result == 0 else None
            
        except Exception:
            return None

    def extract_raw_image(self, image_data, width=400, height=500):
        """Extract raw image data from captured data"""
        expected_size = width * height
        header_size = len(image_data) - expected_size
        if header_size < 0:
            print(f"[ERROR] Image data is too small. Expected at least {expected_size} bytes, got {len(image_data)} bytes.")
            return None
        raw_image_data = image_data[header_size:]
        if len(raw_image_data) != expected_size:
            print(f"[ERROR] Invalid raw image data size. Expected {expected_size} bytes, got {len(raw_image_data)} bytes.")
            return None
        print(f"[DEBUG] Raw image data size: {len(raw_image_data)} bytes")
        return raw_image_data

    def compress_raw(self, image_data, width=400, height=500):
        """Compress raw image using WSQ"""
        try:
            expected_size = width * height
            if len(image_data) != expected_size:
                print(f"[ERROR] Invalid image data size. Expected {expected_size} bytes, got {len(image_data)} bytes.")
                return None
            img = Image.frombytes("L", (width, height), image_data)
            with io.BytesIO() as output:
                img.save(output, format="WSQ")
                compressed_data = output.getvalue()
            print("[DEBUG] Image compressed successfully using WSQ.")
            return compressed_data
        except Exception as e:
            print(f"[ERROR] Failed to compress image using WSQ: {e}")
            return None

# ==================== Identification Thread Worker ====================
class IdentificationThread(QThread):
    identification_complete = pyqtSignal(bool, str, str, str)  # success, message, name, nik
    status_update = pyqtSignal(str)
    finger_status = pyqtSignal(bool)

    def __init__(self, dev, user_id):
        super().__init__()
        self.dev = dev
        self.user_id = user_id
        self.capture_thread = None
        self.init_fingerprint_device()

    def init_fingerprint_device(self):
        """Initialize the fingerprint device"""
        try:
            global dpfj_dll
            dpfj_dll = ctypes.WinDLL("dpfj.dll")
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

        except Exception as e:
            self.status_update.emit(f"dpfj error: {str(e)}")
            self.identification_complete.emit(False, f"dpfj initialization error: {str(e)}", "", "")

    def run(self):
        try:
            conn = sqlite3.connect('fingerprint_enrollment.db')
            cursor = conn.cursor()
            
            # Step 1: Check if user exists
            cursor.execute("SELECT name, nik FROM users WHERE user_id = ?", (self.user_id,))
            user_info = cursor.fetchone()
            
            if not user_info:
                self.identification_complete.emit(False, "User ID not found", "", "")
                conn.close()
                return
            
            name, nik = user_info
            
            # Step 2: Capture fingerprint
            self.status_update.emit("Please place your finger on the scanner...")
            
            # Capture fingerprint directly in this thread
            image_data = self.capture_fingerprint()
            if not image_data:
                self.identification_complete.emit(False, "Failed to capture fingerprint", "", "")
                conn.close()
                return
                
            self.status_update.emit("Processing captured fingerprint...")
            
            # Step 3: Extract raw image data
            raw_image_data = self.extract_raw_image(image_data)
            if not raw_image_data:
                self.identification_complete.emit(False, "Failed to extract raw image", "", "")
                conn.close()
                return

            # Step 4: Create FMD from raw image
            fmd_data = self.create_fmd_from_raw(raw_image_data)
            if not fmd_data:
                self.identification_complete.emit(False, "Failed to create FMD", "", "")
                conn.close()
                return

            # Step 5: Load and compare with enrolled templates
            cursor.execute("SELECT fingerprint FROM fingerprints WHERE user_id = ?", (self.user_id,))
            match_found = False
            
            for row in cursor:
                compressed_data = row[0]
                
                # Decompress the stored fingerprint
                decompressed_data = self.decompress_wsq(compressed_data)
                if not decompressed_data:
                    self.status_update.emit("Failed to decompress stored fingerprint")
                    continue
                
                # Create FMD from decompressed data
                enrolled_fmd = self.create_fmd_from_raw(decompressed_data["data"])
                if not enrolled_fmd:
                    self.status_update.emit("Failed to create FMD from stored fingerprint")
                    continue
                
                # Compare FMDs
                score = self.compare_fmds(fmd_data, enrolled_fmd)
                if score is not None and score < 100:  # Adjust threshold as needed
                    match_found = True
                    break
            
            if match_found:
                self.identification_complete.emit(True, "Match found!", name, nik)
            else:
                self.identification_complete.emit(False, "No matching fingerprint found", "", "")
                
            self.status_update.emit(f"User found: {name}")
            conn.close()
                
        except Exception as e:
            self.identification_complete.emit(False, f"Error: {str(e)}", "", "")
            try:
                conn.close()
            except:
                pass

    def capture_fingerprint(self):
        """Capture fingerprint using device"""
        try:
            capture_param = DPFPDD_CAPTURE_PARAM()
            capture_param.size = ctypes.sizeof(DPFPDD_CAPTURE_PARAM)
            capture_param.image_fmt = 0x01010007  # ISO format
            capture_param.image_proc = 2  # Enhanced processing
            capture_param.image_res = 500  # 500 DPI

            capture_result = DPFPDD_CAPTURE_RESULT()
            capture_result.size = ctypes.sizeof(DPFPDD_CAPTURE_RESULT)
            image_size = c_uint()

            # First call to get buffer size
            result = dpfpdd_dll.dpfpdd_capture(
                self.dev, byref(capture_param), 5000, 
                byref(capture_result), byref(image_size), None
            )
            
            if result != 0 and result != DPFJ_E_MORE_DATA:
                self.status_update.emit(f"Failed to get buffer size. Code: 0x{result:08X}")
                return None

            # Allocate buffer
            image_buffer = (c_ubyte * image_size.value)()
            
            # Second call to capture image
            result = dpfpdd_dll.dpfpdd_capture(
                self.dev, byref(capture_param), 5000,
                byref(capture_result), byref(image_size), image_buffer
            )
            
            if result == 0:
                self.status_update.emit("Fingerprint captured successfully.")
                return bytes(image_buffer)       
            else:
                self.status_update.emit(f"Capture failed: 0x{result:08X}")
                return None
                
        except Exception as e:
            self.status_update.emit(f"Capture exception: {str(e)}")
            return None

    def extract_raw_image(self, image_data, width=400, height=500):
        """Extract raw image data from captured data"""
        expected_size = width * height
        header_size = len(image_data) - expected_size
        if header_size < 0:
            self.status_update.emit(f"Image data too small. Expected {expected_size} bytes, got {len(image_data)}")
            return None
        return image_data[header_size:]

    def create_fmd_from_raw(self, image_data, width=400, height=500, dpi=500, 
                          finger_pos=0, cbeff_id=0, fmd_type=0x001B0001):
        """Create FMD from raw image data"""
        try:
            image_data_array = (ctypes.c_ubyte * len(image_data)).from_buffer_copy(image_data)
            fmd_size = c_uint(0)
            
            # First call to get size
            result = dpfj_dll.dpfj_create_fmd_from_raw(
                image_data_array, len(image_data), width, height, dpi,
                finger_pos, cbeff_id, fmd_type, None, byref(fmd_size))
            
            if result != DPFJ_E_MORE_DATA:
                self.status_update.emit(f"Failed to get FMD size. Error: 0x{result:08X}")
                return None
                
            # Second call to create FMD
            fmd = (ctypes.c_ubyte * fmd_size.value)()
            result = dpfj_dll.dpfj_create_fmd_from_raw(
                image_data_array, len(image_data), width, height, dpi,
                finger_pos, cbeff_id, fmd_type, fmd, byref(fmd_size))
                
            if result == DPFJ_SUCCESS:
                return bytes(fmd[:fmd_size.value])
            else:
                self.status_update.emit(f"Failed to create FMD. Error: 0x{result:08X}")
                return None
        except Exception as e:
            self.status_update.emit(f"FMD creation exception: {str(e)}")
            return None

    def decompress_wsq(self, compressed_data):
        """Decompress WSQ image data"""
        try:
            img = Image.open(io.BytesIO(compressed_data))
            return {
                "data": img.tobytes(),
                "width": img.size[0],
                "height": img.size[1],
                "dpi": img.info.get("dpi", (500, 500))[0],
                "bpp": 8
            }
        except Exception as e:
            self.status_update.emit(f"WSQ decompression failed: {str(e)}")
            return None

    def compare_fmds(self, fmd1, fmd2):
        """Compare two FMDs and return dissimilarity score"""
        try:
            fmd1_array = (ctypes.c_ubyte * len(fmd1)).from_buffer_copy(fmd1)
            fmd2_array = (ctypes.c_ubyte * len(fmd2)).from_buffer_copy(fmd2)
            score = c_uint(0)
            
            result = dpfj_dll.dpfj_compare(
                0x001B0001, fmd1_array, len(fmd1), 0,
                0x001B0001, fmd2_array, len(fmd2), 0,
                byref(score))
                
            return score.value if result == DPFJ_SUCCESS else None
        except Exception as e:
            self.status_update.emit(f"FMD comparison failed: {str(e)}")
            return None
            
# ==================== Main Application Window ====================
class FingerprintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dev = None
        self.capture_thread = None
        self.enrollment_thread = None
        
        self.setWindowTitle("Fingerprint Enrollment System")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize components
        self.setup_ui()
        self.init_fingerprint_device()
        self.create_database()

    def setup_ui(self):
        """Setup the main user interface"""
        # Create tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.enrollment_tab = QWidget()
        self.identification_tab = QWidget()
        self.tabs.addTab(self.enrollment_tab, "Enrollment")
        self.tabs.addTab(self.identification_tab, "Identification")
        
        # Setup tab UIs
        self.setup_enrollment_tab()
        self.setup_identification_tab()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def setup_enrollment_tab(self):
        """Setup the enrollment tab UI"""
        layout = QVBoxLayout()
        
        # User information
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("User ID:"))
        self.user_id_input = QLineEdit()
        form_layout.addWidget(self.user_id_input)
        
        form_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        form_layout.addWidget(self.name_input)
        
        form_layout.addWidget(QLabel("NIK:"))
        self.nik_input = QLineEdit()
        form_layout.addWidget(self.nik_input)
        
        layout.addLayout(form_layout)
        
        # Enrollment controls
        self.enroll_button = QPushButton("Start Enrollment (4 scans)")
        self.enroll_button.clicked.connect(self.start_enrollment)
        layout.addWidget(self.enroll_button)
        
        # Progress display
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(4)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready for enrollment")
        layout.addWidget(self.status_label)
        
        # Log display
        self.enroll_log = QTextEdit()
        self.enroll_log.setReadOnly(True)
        layout.addWidget(self.enroll_log)
        
        self.enrollment_tab.setLayout(layout)

    def setup_identification_tab(self):
        """Setup the identification tab UI with improved layout"""
        layout = QVBoxLayout()
        
        # User ID input
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("User ID:"))
        self.identify_id_input = QLineEdit()
        id_layout.addWidget(self.identify_id_input)
        layout.addLayout(id_layout)
        
        # Finger status indicator
        self.identify_finger_status = QLabel("Finger status: Not detected")
        self.identify_finger_status.setStyleSheet("color: red")
        layout.addWidget(self.identify_finger_status)
        
        # Identify button
        self.identify_button = QPushButton("Identify")
        self.identify_button.clicked.connect(self.identify_user)
        layout.addWidget(self.identify_button)
        
        # Results display
        self.identify_result = QTextEdit()
        self.identify_result.setReadOnly(True)
        layout.addWidget(self.identify_result)
        
        # Match result display
        self.match_result = QLabel()
        self.match_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.match_result.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.match_result)
        
        self.identification_tab.setLayout(layout)

    def init_fingerprint_device(self):
        """Initialize the fingerprint device"""
        try:
            global dpfpdd_dll
            dpfpdd_dll = ctypes.WinDLL("dpfpdd.dll")
            
            # Setup function prototypes
            dpfpdd_dll.dpfpdd_get_device_status.argtypes = [POINTER(DPFPDD_DEV), POINTER(DPFPDD_DEV_STATUS)]
            dpfpdd_dll.dpfpdd_get_device_status.restype = c_int
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
            dpfpdd_dll.dpfpdd_capture.argtypes = [
                POINTER(DPFPDD_DEV),
                POINTER(DPFPDD_CAPTURE_PARAM),
                c_uint,
                POINTER(DPFPDD_CAPTURE_RESULT),
                POINTER(c_uint),
                c_void_p
            ]
            dpfpdd_dll.dpfpdd_capture.restype = c_int

            # Initialize library
            result = dpfpdd_dll.dpfpdd_init()
            if result != 0:
                raise Exception(f"DPFPDD init failed: 0x{result:08X}")

            # Find devices
            device_count = c_int(10)
            devices = (DPFPDD_DEV_INFO * 10)()
            result = dpfpdd_dll.dpfpdd_query_devices(byref(device_count), devices)
            if result != 0 and device_count.value == 0:
                raise Exception("No fingerprint devices found")

            # Open device
            self.dev = POINTER(DPFPDD_DEV)()
            device_name = devices[0].name.decode("ascii", errors='replace')
            result = dpfpdd_dll.dpfpdd_open(device_name.encode('ascii'), byref(self.dev))
            if result != 0:
                raise Exception(f"Device open failed: 0x{result:08X}")

            self.status_bar.showMessage(f"Connected to {device_name}")
            
        except Exception as e:
            self.status_bar.showMessage(f"Device error: {str(e)}")
            QMessageBox.critical(self, "Device Error", f"Failed to initialize fingerprint device: {str(e)}")

    def create_database(self):
        """Create the SQLite database if it doesn't exist"""
        try:
            conn = sqlite3.connect('fingerprint_enrollment.db')
            conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                nik TEXT NOT NULL
            )
            ''')
            conn.execute('''
            CREATE TABLE IF NOT EXISTS fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                fingerprint BLOB NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            ''')
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to create database: {str(e)}")

    def start_enrollment(self):
        """Start the fingerprint enrollment process"""
        user_id = self.user_id_input.text()
        name = self.name_input.text()
        nik = self.nik_input.text()

        if not all([user_id, name, nik]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields")
            return

        # Disable UI during enrollment
        self.enroll_button.setEnabled(False)
        self.user_id_input.setEnabled(False)
        self.name_input.setEnabled(False)
        self.nik_input.setEnabled(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.enroll_log.clear()
        self.enroll_log.append("Starting enrollment process...")
        
        # Start enrollment thread
        self.enrollment_thread = EnrollmentThread(self.dev, user_id, name, nik)
        self.enrollment_thread.update_progress.connect(self.update_enrollment_progress)
        self.enrollment_thread.scan_complete.connect(self.handle_scan_complete)
        self.enrollment_thread.enrollment_complete.connect(self.handle_enrollment_complete)
        self.enrollment_thread.start()

    def update_enrollment_progress(self, scan_num, message):
        """Update the enrollment progress display"""
        self.progress_bar.setValue(scan_num)
        self.enroll_log.append(message)

    def handle_scan_complete(self, scan_num, success):
        """Handle completion of a single fingerprint scan"""
        if success:
            self.enroll_log.append(f"Scan {scan_num} completed successfully")
        else:
            self.enroll_log.append(f"Scan {scan_num} failed")

    def handle_enrollment_complete(self, success, message):
        """Handle completion of the entire enrollment process"""
        # Re-enable UI
        self.enroll_button.setEnabled(True)
        self.user_id_input.setEnabled(True)
        self.name_input.setEnabled(True)
        self.nik_input.setEnabled(True)
        
        # Show result
        if success:
            self.enroll_log.append("Enrollment completed successfully!")
            QMessageBox.information(self, "Success", message)
        else:
            self.enroll_log.append("Enrollment failed!")
            QMessageBox.warning(self, "Error", message)

    def identify_user(self):
        """Start the identification process"""
        user_id = self.identify_id_input.text()
        if not user_id:
            QMessageBox.warning(self, "Input Error", "Please enter a User ID")
            return

        # Clear previous results
        self.identify_result.clear()
        self.match_result.clear()
        self.identify_result.append(f"Starting identification for user {user_id}...")
        
        # Disable button during identification
        self.identify_button.setEnabled(False)
        
        # Start identification thread
        self.identification_thread = IdentificationThread(self.dev, user_id)
        self.identification_thread.finger_status.connect(self.update_identify_finger_status)
        self.identification_thread.status_update.connect(self.identify_result.append)
        self.identification_thread.identification_complete.connect(self.handle_identification_complete)
        self.identification_thread.start()

    def update_identify_finger_status(self):
        """Update finger detection status in identification tab"""
        status = DPFPDD_DEV_STATUS()
        status.size = ctypes.sizeof(DPFPDD_DEV_STATUS)
        result = dpfpdd_dll.dpfpdd_get_device_status(self.dev, ctypes.byref(status))
        if result == 0:
            print(f"Reader status obtained successfully. Status Code: {status.status}")
            if status.status == DPFPDD_STATUS_READY:
                detected =True
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


        if detected:
            self.identify_finger_status.setText("Finger status: Detected")
            self.identify_finger_status.setStyleSheet("color: green")
        else:
            self.identify_finger_status.setText("Finger status: Not detected")
            self.identify_finger_status.setStyleSheet("color: red")

    def handle_identification_complete(self, success, message, name, nik):
        """Handle completion of identification process"""
        # Re-enable button
        self.identify_button.setEnabled(True)
        
        # Show results
        self.identify_result.append(message)
        
        if success:
            self.match_result.setText(f"MATCH FOUND!\nName: {name}\nNIK: {nik}")
            self.match_result.setStyleSheet("color: green; font-size: 16px; font-weight: bold;")
        else:
            self.match_result.setText("NO MATCH FOUND")
            self.match_result.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")

    def process_identification(self, image_data, user_id):
        """Process the captured fingerprint for identification"""
        self.update_identify_finger_status()
        try:
            conn = sqlite3.connect('fingerprint_enrollment.db')
            cursor = conn.cursor()
            
            # Get user info
            cursor.execute("SELECT name, nik FROM users WHERE user_id = ?", (user_id,))
            for row in cursor:
                compressed_data = row[0]
                decompressed_data = self.expand_raw(compressed_data)
                if not decompressed_data:
                    print("[ERROR] Failed to decompress fingerprint data.")
                    continue

                # Create FMD from decompressed raw image data
                enrolled_fmd = self.create_fmd_from_raw(
                    decompressed_data["data"],
                    width=400,
                    height=500,
                    dpi=500,
                    finger_pos=DPFJ_POSITION_UNKNOWN,
                    cbeff_id=0,
                    fmd_type=DPFJ_FMD_ANSI_378_2004
                )
                if enrolled_fmd:
                    enrolled_fmds.append(enrolled_fmd)

            # Step 7: Compare the extracted FMD with enrolled templates
            for enrolled_fmd in enrolled_fmds:
                score = self.compare_fmds(fmd_data, enrolled_fmd)
                if score is not None and score < 100:  # Adjust threshold as needed
                    print(f"Match found! User: {name}, NIK: {nik}")
                    conn.close()
                    return name, nik  # Return user's name and NIK

            user_info = cursor.fetchone()
            
            if not user_info:
                print("No match found.")
                self.identify_result.append("User not found")
                print("[ERROR] User ID not found in the database.")
                # conn.close()
                return
            
            name, nik = user_info

            # Step 3: Capture fingerprint image
            print("Capturing fingerprint...")
            image_data = self.capture_fingerprint()
            if not image_data:
                print("[ERROR] Failed to capture fingerprint.")
                # conn.close()
                return None

            # Step 4: Extract raw image data
            raw_image_data = self.extract_raw_image(image_data, width=400, height=500)
            if not raw_image_data:
                print("[ERROR] Failed to extract raw image data.")
                # conn.close()
                return None

            # Step 5: Create FMD from raw image data
            fmd_data = self.create_fmd_from_raw(
                raw_image_data,
                width=400,
                height=500,
                dpi=500,
                finger_pos=DPFJ_POSITION_UNKNOWN,
                cbeff_id=0,
                fmd_type=DPFJ_FMD_ANSI_378_2004
            )
            if not fmd_data:
                print("[ERROR] Failed to create FMD from raw image data.")
                conn.close()
                return None
            
            # Step 6: Load enrolled FMDs for the user
            enrolled_fmds = []
            # Get stored fingerprints
            cursor.execute("SELECT fingerprint FROM fingerprints WHERE user_id = ?", (user_id,))
            stored_fingerprints = cursor.fetchall()
            
            if not stored_fingerprints:
                self.identify_result.append("No fingerprints enrolled for this user")
                return
            
            # Here you would normally compare fingerprints
            # For this example, we'll just assume a match
            self.identify_result.append(f"Match found!\nName: {name}\nNIK: {nik}")
            
        except Exception as e:
            self.identify_result.append(f"Error: {str(e)}")
        finally:
            conn.close()

    def handle_capture_error(self, error_msg):
        """Handle fingerprint capture errors"""
        self.identify_result.append(f"Error: {error_msg}")

    def closeEvent(self, event):
        """Clean up when closing the application"""
        if self.capture_thread and self.capture_thread.isRunning():
            self.capture_thread.terminate()
            
        if self.enrollment_thread and self.enrollment_thread.isRunning():
            self.enrollment_thread.terminate()
        
        if self.dev:
            dpfpdd_dll.dpfpdd_close(self.dev)
            dpfpdd_dll.dpfpdd_exit()
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FingerprintApp()
    window.show()
    sys.exit(app.exec())