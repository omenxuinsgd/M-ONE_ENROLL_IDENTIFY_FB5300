from PIL import Image
import wsq
import io

# Buka file WSQ
wsq_file = "compressed_scan_1.wsq"
with open(wsq_file, "rb") as f:
    wsq_data = f.read()

# Dekompresi gambar WSQ
img = Image.open(io.BytesIO(wsq_data))

# Simpan sebagai gambar PNG
img.save("decompressed_scan_1.png")
print("WSQ file decompressed and saved as PNG.")