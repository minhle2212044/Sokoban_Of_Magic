from PIL import Image

# Mở ảnh gốc
img = Image.open("notfound.png")

# Giảm kích thước xuống 640x640
img_resized = img.resize((640, 640), Image.NEAREST)  # Giữ pixel rõ, không bị mờ

# Lưu lại
img_resized.save("notfound1.png")
print("✅ Ảnh đã được giảm xuống 640x640")
