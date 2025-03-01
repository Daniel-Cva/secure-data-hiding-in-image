from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import cv2
import numpy as np
from lsb_aes import encrypt_data, decrypt_data

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ENCRYPTED_FOLDER'] = 'encrypted/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['ENCRYPTED_FOLDER']):
    os.makedirs(app.config['ENCRYPTED_FOLDER'])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        file = request.files['image']
        data = request.form['data']
        password_key = request.form['passwordkey']
        
        if file and data and password_key:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(image_path)
            
            encrypted_image_path = os.path.join(app.config['ENCRYPTED_FOLDER'], 'encrypted_' + file.filename)
            encrypt_data(image_path, data, password_key, encrypted_image_path)
            
            return send_file(encrypted_image_path, as_attachment=True)
    
    return render_template('encrypt.html')


@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        file = request.files['image']
        password_key = request.form['passwordkey']
        
        if file and password_key:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(image_path)
            
            decrypted_data = decrypt_data(image_path, password_key)
            
            if decrypted_data is None:
                error = "Decryption failed. Incorrect password or corrupted image."
                return render_template('decrypt.html', error=error)

            return render_template('decrypt.html', decrypted_data=decrypted_data)
    
    return render_template('decrypt.html')


if __name__ == '__main__':
    app.run(debug=True)
