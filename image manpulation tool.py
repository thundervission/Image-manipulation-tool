import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageEnhance, ImageTk
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import qrcode

# Global variables
key = os.urandom(32)
iv = os.urandom(16)

# Function to load image data
def load_image(image_path):
    with open(image_path, 'rb') as file:
        return file.read()

# Function to save image data
def save_image(data, output_file):
    with open(output_file, 'wb') as file:
        file.write(data)

# Function to encrypt image
def encrypt_image(image_path, output_file):
    image_data = load_image(image_path)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(image_data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    save_image(iv + encrypted_data, output_file)
    messagebox.showinfo("Success", "Image encrypted successfully!")

# Function to decrypt image
def decrypt_image(encrypted_image_path, output_file):
    encrypted_data = load_image(encrypted_image_path)
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    save_image(decrypted_data, output_file)
    messagebox.showinfo("Success", "Image decrypted successfully!")

# Function to compress image
def compress_image(image_path, output_file, quality):
    image = Image.open(image_path)
    image.save(output_file, quality=quality)
    messagebox.showinfo("Success", "Image compressed successfully!")

# Function to enhance image quality
def enhance_image(image_path, output_file, factor):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Sharpness(image)
    enhanced_image = enhancer.enhance(factor)
    enhanced_image.save(output_file)
    messagebox.showinfo("Success", "Image enhanced successfully!")

# Function to add watermark to image with transparency
def add_watermark(image_path, watermark_path, output_file, transparency):
    base_image = Image.open(image_path).convert("RGBA")
    watermark = Image.open(watermark_path).convert("RGBA")

    # Resize watermark to fit base image if necessary
    watermark = watermark.resize((base_image.width, base_image.height), Image.LANCZOS)

    # Adjust transparency
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(transparency)
    watermark.putalpha(alpha)

    # Overlay the watermark
    watermarked_image = Image.alpha_composite(base_image, watermark)
    watermarked_image = watermarked_image.convert("RGB")  # Convert back to RGB mode

    # Save the result
    watermarked_image.save(output_file)
    messagebox.showinfo("Success", "Watermark added successfully!")

# Function to hide message in image
def hide_message(image_path, message, output_file):
    image = Image.open(image_path)
    binary_message = ''.join(format(ord(char), '08b') for char in message) + '11111110'  # Adding delimiter
    if len(binary_message) > len(image.getdata()) * 3:
        raise Exception("Need larger image size")
    encoded_image = image.copy()
    pixels = list(encoded_image.getdata())
    binary_index = 0

    new_pixels = []
    for pixel in pixels:
        if binary_index < len(binary_message):
            r = (pixel[0] & ~1) | int(binary_message[binary_index])
            binary_index += 1
        else:
            r = pixel[0]

        if binary_index < len(binary_message):
            g = (pixel[1] & ~1) | int(binary_message[binary_index])
            binary_index += 1
        else:
            g = pixel[1]

        if binary_index < len(binary_message):
            b = (pixel[2] & ~1) | int(binary_message[binary_index])
            binary_index += 1
        else:
            b = pixel[2]

        new_pixels.append((r, g, b))

    encoded_image.putdata(new_pixels)
    encoded_image.save(output_file)
    messagebox.showinfo("Success", "Message hidden successfully!")

# Function to recover the hidden message from an image
def extract_message(image_path):
    image = Image.open(image_path)
    pixels = list(image.getdata())
    binary_message = ""
    delimiter = '11111110'
    message = ""

    # Extract binary message
    for pixel in pixels:
        for i in range(3):  # RGB components
            binary_message += str(pixel[i] & 1)

    # Convert binary message to characters
    i = 0
    while i < len(binary_message):
        byte = binary_message[i:i + 8]
        i += 8
        if byte == delimiter:
            break
        message += chr(int(byte, 2))

    return message


# Function to generate and add QR code to image
def add_qr_code(image_path, message, output_file):
    image = Image.open(image_path).convert("RGBA")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(message)
    qr.make(fit=True)
    qr_code = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # Resize QR code to fit within the image
    qr_size = (image.width // 4, image.height // 4)
    qr_code = qr_code.resize(qr_size, Image.LANCZOS)

    # Position the QR code at the bottom-right corner
    position = (image.width - qr_code.width, image.height - qr_code.height)
    combined_image = Image.alpha_composite(image, Image.new("RGBA", image.size))
    combined_image.paste(qr_code, position, qr_code)

    combined_image.save(output_file)
    messagebox.showinfo("Success", "QR code added successfully!")

def select_stego_image():
    filetypes = [("Image files", ".jpg;.jpeg;.png;.bmp;*.gif")]
    filename = filedialog.askopenfilename(filetypes=filetypes)
    entry_stego_path.delete(0, tk.END)
    entry_stego_path.insert(0, filename)
    if filename:
        img = Image.open(filename)
        img.thumbnail((250, 250))
        img_tk = ImageTk.PhotoImage(img)
        panel_stego.config(image=img_tk)
        panel_stego.image = img_tk

def recover_message():
    stego_image_path = entry_stego_path.get()
    try:
        message = extract_message(stego_image_path)
        messagebox.showinfo("Recovered Message", f"Message: {message}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_file():
    filetypes = [("Image files", ".jpg;.jpeg;.png;.bmp;*.gif")]
    filename = filedialog.askopenfilename(filetypes=filetypes)
    entry_path.delete(0, tk.END)
    entry_path.insert(0, filename)
    if filename:
        img = Image.open(filename)
        img.thumbnail((250, 250))
        img_tk = ImageTk.PhotoImage(img)
        panel.config(image=img_tk)
        panel.image = img_tk

def select_output_file():
    filetypes = [("Image files", ".jpg;.jpeg;.png;.bmp;*.gif")]
    filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)
    entry_output.delete(0, tk.END)
    entry_output.insert(0, filename)

def update_options(*args):
    action = variable_action.get()
    hide_all_options()
    if action == "Compress":
        label_quality.grid()
        entry_quality.grid()
    elif action == "Enhance Quality":
        label_factor.grid()
        entry_factor.grid()
    elif action == "Watermark":
        label_transparency.grid()
        entry_transparency.grid()
    elif action == "Steganography":
        label_message.grid()
        entry_message.grid()
    elif action == "QR Code":
        label_qr_message.grid()
        entry_qr_message.grid()
    elif action == "Recover Stego Message":
        label_stego_select.grid()
        entry_stego_path.grid()
        button_stego_browse.grid()
        panel_stego.grid()
        button_recover.grid()

def hide_all_options():
    label_quality.grid_remove()
    entry_quality.grid_remove()
    label_factor.grid_remove()
    entry_factor.grid_remove()
    label_transparency.grid_remove()
    entry_transparency.grid_remove()
    label_message.grid_remove()
    entry_message.grid_remove()
    label_qr_message.grid_remove()
    entry_qr_message.grid_remove()
    label_stego_select.grid_remove()
    entry_stego_path.grid_remove()
    button_stego_browse.grid_remove()
    panel_stego.grid_remove()
    button_recover.grid_remove()

def perform_action():
    action = variable_action.get()
    input_path = entry_path.get()
    output_path = entry_output.get()
    quality = int(entry_quality.get()) if entry_quality.get() else 75
    factor = float(entry_factor.get()) if entry_factor.get() else 1.5
    transparency = float(entry_transparency.get()) if entry_transparency.get() else 0.5
    message = entry_message.get()
    qr_message = entry_qr_message.get()

    try:
        if action == "Encrypt":
            encrypt_image(input_path, output_path)
        elif action == "Decrypt":
            decrypt_image(input_path, output_path)
        elif action == "Compress":
            compress_image(input_path, output_path, quality)
        elif action == "Enhance Quality":
            enhance_image(input_path, output_path, factor)
        elif action == "Watermark":
            watermark_path = filedialog.askopenfilename(filetypes=[("Image files", ".jpg;.jpeg;.png;.bmp;*.gif")])
            if watermark_path:
                add_watermark(input_path, watermark_path, output_path, transparency)
        elif action == "Steganography":
            hide_message(input_path, message, output_path)
        elif action == "QR Code":
            add_qr_code(input_path, qr_message, output_path)
        elif action == "Recover Stego Message":
            recover_message()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create GUI
root = tk.Tk()
root.title("Image Manipulation")

# File selection
label_select = tk.Label(root, text="Select Image/File:")
label_select.grid(row=0, column=0)
entry_path = tk.Entry(root, width=50)
entry_path.grid(row=0, column=1)
button_browse = tk.Button(root, text="Browse", command=select_file)
button_browse.grid(row=0, column=2)

# Image preview
panel = tk.Label(root)
panel.grid(row=1, columnspan=3)

# Action selection
label_action = tk.Label(root, text="Action:")
label_action.grid(row=2, column=0)
actions = ["Encrypt", "Decrypt", "Compress", "Enhance Quality", "Watermark", "Steganography", "QR Code", "Recover Stego Message"]
variable_action = tk.StringVar(root)
variable_action.set(actions[0])
variable_action.trace("w", update_options)
dropdown_action = tk.OptionMenu(root, variable_action, *actions)
dropdown_action.grid(row=2, column=1)

# Quality input for compression
label_quality = tk.Label(root, text="Quality (1-100):")
label_quality.grid(row=3, column=0)
entry_quality = tk.Entry(root)
entry_quality.grid(row=3, column=1)
entry_quality.insert(0, "75")

# Factor input for enhancement
label_factor = tk.Label(root, text="Enhance Factor:")
label_factor.grid(row=4, column=0)
entry_factor = tk.Entry(root)
entry_factor.grid(row=4, column=1)
entry_factor.insert(0, "1.5")

# Transparency input for watermark
label_transparency = tk.Label(root, text="Watermark Transparency (0.0-1.0):")
label_transparency.grid(row=5, column=0)
entry_transparency = tk.Entry(root)
entry_transparency.grid(row=5, column=1)
entry_transparency.insert(0, "0.5")

# Message input for steganography
label_message = tk.Label(root, text="Message:")
label_message.grid(row=6, column=0)
entry_message = tk.Entry(root)
entry_message.grid(row=6, column=1)

# Message input for QR code
label_qr_message = tk.Label(root, text="QR Code Message:")
label_qr_message.grid(row=7, column=0)
entry_qr_message = tk.Entry(root)
entry_qr_message.grid(row=7, column=1)

# Steganography recover message input
label_stego_select = tk.Label(root, text="Select Stego Image:")
label_stego_select.grid(row=8, column=0)
entry_stego_path = tk.Entry(root, width=50)
entry_stego_path.grid(row=8, column=1)
button_stego_browse = tk.Button(root, text="Browse", command=select_stego_image)
button_stego_browse.grid(row=8, column=2)
panel_stego = tk.Label(root)
panel_stego.grid(row=9, columnspan=3)

# Output file selection
label_output = tk.Label(root, text="Save As:")
label_output.grid(row=10, column=0)
entry_output = tk.Entry(root, width=50)
entry_output.grid(row=10, column=1)
button_save_as = tk.Button(root, text="Save As", command=select_output_file)
button_save_as.grid(row=10, column=2)

# Perform action
button_perform = tk.Button(root, text="Perform Action", command=perform_action)
button_perform.grid(row=11, columnspan=3)

# Button to recover message from stego image
button_recover = tk.Button(root, text="Recover Message", command=recover_message)
button_recover.grid(row=12, columnspan=3)

# Hide all options initially
hide_all_options()
update_options()

root.mainloop()