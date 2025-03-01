
import cv2
import numpy as np
import os
import string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


def generate_key(password):
    key = password.encode('utf-8')
    key = pad(key, AES.block_size)
    return key


def encrypt_data(image_path, data, password_key, output_path):
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found or unable to read image")

    # Generate AES key
    key = generate_key(password_key)

    # Encrypt the data using AES
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    iv = cipher.iv
    encrypted_data = iv + ct_bytes

    # Convert encrypted data to binary
    binary_data = ''.join(format(byte, '08b') for byte in encrypted_data)

    # Hide data in the image using LSB
    _, width, _ = image.shape
    binary_index = 0
    for row in image:
        for pixel in row:
            for i in range(3):  # Iterate over RGB channels
                if binary_index < len(binary_data):
                    pixel[i] = (pixel[i] & ~1) | int(binary_data[binary_index])
                    binary_index += 1
                else:
                    break

    # Save the encrypted image
    cv2.imwrite(output_path, image)


def decrypt_data(image_path, password_key):
    try:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Image not found or unable to read image")

        # Extract encrypted data from the image using LSB
        binary_data = ''
        for row in image:
            for pixel in row:
                for i in range(3):  # Iterate over RGB channels
                    binary_data += str(pixel[i] & 1)

        # Convert binary data to bytes
        encrypted_data = int(binary_data, 2).to_bytes((len(binary_data) + 7) // 8, byteorder='big')

        # Extract IV and ciphertext
        iv = encrypted_data[:16]
        ct = encrypted_data[16:]

        # Generate AES key
        key = generate_key(password_key)

        # Decrypt the data using AES
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        decrypted_data = unpad(cipher.decrypt(ct), AES.block_size)

        return decrypted_data.decode('utf-8')
    except (ValueError, KeyError):
        return None
