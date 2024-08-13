from flask import Flask, render_template, request
from ocr_process import *
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form['action']
        image = request.files['image']
        
        if action == 'Masuk':
            # Tangani aksi 'Masuk' di sini
            print("Masuk")
        elif action == 'Keluar':
            # Tangani aksi 'Keluar' di sini
            print("Keluar")
            
        time_str = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
        
        
    return render_template('index.html')

def get_folders_info():
    # Implementasikan fungsi ini sesuai kebutuhan untuk mengembalikan informasi folder
    return []

if __name__ == '__main__':
    # Run Flask with SSL
    app.run(
        host='0.0.0.0',
        port=5001,
    )
