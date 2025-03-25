import sys
import ctypes
from ctypes import c_int, c_uint, POINTER, Structure, c_void_p, c_char_p, c_ubyte, byref
import os
import sqlite3
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, QMessageBox
)
from PIL import Image
import io

# Setup logging
logging.basicConfig(
    filename="fingerprint_system.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load the DPFPDD and DPFJ DLLs
dpfpdd_dll = ctypes.WinDLL("dpfpdd.dll")
dpfj_dll = ctypes.WinDLL("dpfj.dll")
# Load the DPFJ Compression DLL
dpfj_compression_dll = ctypes.WinDLL("./dpfj_compression.dll")

class DPFPDD_DEV_INFO(ctypes.Structure):
    _fields_ = [("size", ctypes.c_uint),
                ("name", ctypes.c_char * 256)]

class DPFPDD_DEV(Structure):
    pass

class DPFPDD_CAPTURE_PARAM(Structure):
    _fields_ = [("size", c_uint), ("image_fmt", c_uint), ("image_proc", c_uint), ("image_res", c_uint)]

class DPFPDD_IMAGE_INFO(Structure):
    _fields_ = [("size", c_uint), ("width", c_uint), ("height", c_uint), ("res", c_uint), ("bpp", c_uint)]

class DPFPDD_CAPTURE_RESULT(Structure):
    _fields_ = [("size", c_uint), ("success", c_int), ("quality", c_int), ("score", c_uint), ("info", DPFPDD_IMAGE_INFO)]


class DPFPDD_DEV_STATUS(Structure):
    _fields_ = [
        ("size", c_uint),
        ("status", c_uint),
        ("finger_detected", c_int),
        ("data", ctypes.c_ubyte * 1)
    ]

dpfpdd_dll.dpfpdd_query_devices.argtypes = [POINTER(c_int), POINTER(DPFPDD_DEV_INFO)]
dpfpdd_dll.dpfpdd_query_devices.restype = c_int

dpfpdd_dll.dpfpdd_init.argtypes = []
dpfpdd_dll.dpfpdd_init.restype = c_int

dpfpdd_dll.dpfpdd_exit.argtypes = []
dpfpdd_dll.dpfpdd_exit.restype = c_int

dpfpdd_dll.dpfpdd_open.argtypes = [c_char_p, POINTER(POINTER(DPFPDD_DEV))]
dpfpdd_dll.dpfpdd_open.restype = c_int

dpfpdd_dll.dpfpdd_capture.argtypes = [
    POINTER(DPFPDD_DEV),
    POINTER(DPFPDD_CAPTURE_PARAM),
    c_uint,
    POINTER(DPFPDD_CAPTURE_RESULT),
    POINTER(c_uint),
    c_void_p
]
dpfpdd_dll.dpfpdd_capture.restype = c_int

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

def create_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('fingerprint_enrollment.db')
    
    # Create Users table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        nik TEXT NOT NULL
    )
    ''')

    # Create Fingerprints table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS fingerprints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        fingerprint BLOB NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    conn.commit()
    conn.close()

def setup_logging():
    """
    Set up logging to save process logs to a file.
    """
    logging.basicConfig(
        filename="fingerprint_system.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


class FingerprintApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fingerprint Enrollment and Identification System")
        self.setGeometry(100, 100, 800, 600)

        # Create a tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create the Enrollment tab
        self.enrollment_tab = QWidget()
        self.tabs.addTab(self.enrollment_tab, "Enrollment")

        # Create the Identification tab
        self.identification_tab = QWidget()
        self.tabs.addTab(self.identification_tab, "Identification")

        # Initialize the UI for both tabs
        self.init_enrollment_ui()
        self.init_identification_ui()
        # Initialize fingerprint device
        self.init_fingerprint_device()

    def init_fingerprint_device(self):
        # Initialize DPFPDD
        result = dpfpdd_dll.dpfpdd_init()
        if result != 0:
            print(f"[ERROR] Failed to initialize DPFPDD. Error Code: {result}")
            QMessageBox.critical(self, "Initialization Error", "Failed to initialize fingerprint device.")
            sys.exit(1)
        else:
            print("DPFPDD initialized successfully.")

        # Query and open device
        devices = query_devices()
        if not devices:
            print("[ERROR] No devices available.")
            dpfpdd_dll.dpfpdd_exit()
            sys.exit(1)

        # Open the first device
        self.dev = POINTER(DPFPDD_DEV)()
        device_name = devices[0].name.decode("ascii", errors='replace')
        result = dpfpdd_dll.dpfpdd_open(device_name.encode('ascii'), byref(self.dev))
        if result != 0:
            print(f"[ERROR] Failed to open device. Error Code: {result}")
            dpfpdd_dll.dpfpdd_exit()
            sys.exit(1)
        else:
            print(f"Device '{device_name}' opened successfully.")

    def init_enrollment_ui(self):
        layout = QVBoxLayout()

        # User ID input
        self.user_id_label = QLabel("User  ID:")
        self.user_id_input = QLineEdit()
        layout.addWidget(self.user_id_label)
        layout.addWidget(self.user_id_input)

        # Name input
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        # NIK input
        self.nik_label = QLabel("NIK:")
        self.nik_input = QLineEdit()
        layout.addWidget(self.nik_label)
        layout.addWidget(self.nik_input)

        # Enrollment button
        self.enroll_button = QPushButton("Enroll")
        self.enroll_button.clicked.connect(self.enroll_user)
        layout.addWidget(self.enroll_button)

        # Status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        layout.addWidget(self.status_display)

        self.enrollment_tab.setLayout(layout)

    def init_identification_ui(self):
        layout = QVBoxLayout()

        # User ID input
        self.identify_user_id_label = QLabel("User  ID:")
        self.identify_user_id_input = QLineEdit()
        layout.addWidget(self.identify_user_id_label)
        layout.addWidget(self.identify_user_id_input)

        # Identify button
        self.identify_button = QPushButton("Identify")
        self.identify_button.clicked.connect(self.identify_user)
        layout.addWidget(self.identify_button)

        # Result display
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.identification_tab.setLayout(layout)

    def enroll_user(self):
        user_id = self.user_id_input.text()
        name = self.name_input.text()
        nik = self.nik_input.text()

        if not user_id or not name or not nik:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        if not self.enroll_user_with_device(user_id, name, nik):
            QMessageBox.critical(self, "Enrollment Error", "Enrollment failed. Please check the logs for details.")
            return

        self.status_display.append(f"Enrollment successful for user {user_id}.")

    def enroll_user_with_device(self, user_id, name, nik, num_scans=4):
        print(f"Enrolling user {user_id}...")

        # Connect to the database
        conn = sqlite3.connect('fingerprint_enrollment.db')
        cursor = conn.cursor()

        try:
            # Start a transaction
            conn.execute("BEGIN TRANSACTION")

            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                print(f"[ERROR] User ID {user_id} already exists.")
                logging.error(f"User  ID {user_id} already exists.")
                return False

            # Insert user data
            cursor.execute("INSERT INTO users (user_id, name, nik) VALUES (?, ?, ?)", (user_id, name, nik))

            # Capture and process fingerprints
            for i in range(num_scans):
                print(f"Capture fingerprint {i + 1}...")
                image_data = self.capture_fingerprint(self.dev)
                if not image_data:
                    print("[ERROR] Failed to capture fingerprint.")
                    logging.error("Failed to capture fingerprint.")
                    continue

                # Validate image quality
                if not self.validate_image_quality(image_data):
                    print("[ERROR] Image quality is poor. Skipping this scan.")
                    logging.error("Image quality is poor. Skipping this scan.")
                    continue

                # Extract raw image data
                raw_image_data = self.extract_raw_image(image_data)
                if not raw_image_data:
                    print("[ERROR] Failed to extract raw image data.")
                    logging.error("Failed to extract raw image data.")
                    continue

                # Compress the raw image
                compressed_data = self.compress_raw(raw_image_data)
                if compressed_data:
                    # Save compressed fingerprint to the database
                    cursor.execute("INSERT INTO fingerprints (user_id, fingerprint) VALUES (?, ?)", (user_id, compressed_data))
                    print(f"Compressed image saved for user {user_id}, scan {i + 1}.")
                    logging.debug(f"Compressed image saved for user {user_id}, scan {i + 1}.")
                else:
                    print(f"[ERROR] Failed to compress image for scan {i + 1}.")
                    logging.error(f"Failed to compress image for scan {i + 1}.")

            # Commit the transaction
            conn.commit()
            print("Enrollment finished successfully.")
            logging.debug("Enrollment finished successfully.")
            return True

        except sqlite3.Error as e:
            # Rollback the transaction in case of error
            conn.rollback()
            print(f"[ERROR] Database error: {e}")
            logging.error(f"Database error: {e}")
            return False

        finally:
            # Close the database connection
            conn.close()

    def capture_fingerprint(self, dev):
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
            
            # Debug: Save raw image data to file for inspection
            with open("captured_image.raw", "wb") as f:
                f.write(bytes(image_buffer))
            print("[DEBUG] Raw image data saved to 'captured_image.raw'.")
            
            return bytes(image_buffer)
        else:
            print(f"[ERROR] Failed to capture fingerprint. Error Code: {result}")
            return None

    def validate_image_quality(self, image_data):
        if len(image_data) < 10000 or len(image_data) > 200046:
            print("[ERROR] Invalid image size. Expected size between 10000 and 200046 bytes.")
            return False

        if not self.has_enough_detail(image_data):
            print("[ERROR] Image does not contain enough detail.")
            return False

        print("Image quality is good.")
        return True

    def extract_raw_image(self, image_data, width=400, height=500):
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

    def compress_raw(self, image_data, width=400, height=500, dpi=500, bpp=8):
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

    def has_enough_detail(self, image_data):
        # Placeholder function to check if the image contains enough detail
        return True  # Placeholder

    def identify_user(self):
        user_id = self.identify_user_id_input.text()

        if not user_id:
            QMessageBox.warning(self, "Input Error", "Please enter a User ID.")
            return

        # Connect to the database
        conn = sqlite3.connect('fingerprint_enrollment.db')
        cursor = conn.cursor()

        try:
            # Check if user exists
            cursor.execute("SELECT name, nik FROM users WHERE user_id = ?", (user_id,))
            user_info = cursor.fetchone()

            if not user_info:
                QMessageBox.warning(self, "Identification Error", "User  ID not found.")
                return

            name, nik = user_info

            # Simulate fingerprint identification (replace with actual fingerprint capture and processing)
            self.result_display.append(f"Identifying user {user_id}...")
            self.result_display.append("Fingerprint captured and processed.")
            self.result_display.append(f"Match found! User: {name}, NIK: {nik}")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

# Main execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    setup_logging()
    # Create the database
    create_database()
    
    window = FingerprintApp()
    window.show()
    sys.exit(app.exec())