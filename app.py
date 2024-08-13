from flask import Flask, render_template, request
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'Masuk':
            # Tangani aksi 'Masuk' di sini
            print("Masuk")
        elif action == 'Keluar':
            # Tangani aksi 'Keluar' di sini
            print("Keluar")
            
        # Lanjutkan dengan logika pemrosesan lainnya jika diperlukan
    return render_template('index.html', folders_info=get_folders_info())

def get_folders_info():
    # Implementasikan fungsi ini sesuai kebutuhan untuk mengembalikan informasi folder
    return []


@app.route('/cam')
def cam():
    return render_template('cam.html')

if __name__ == '__main__':
    # Run Flask with SSL
    app.run(
        host='0.0.0.0',
        port=5001,
    )
