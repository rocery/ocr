from flask import Flask, render_template, request, flash, redirect, url_for
from ocr_process import *
import time
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    data  = None
    time_str = None
    label = None
    if request.method == 'POST':
        action = request.form['action']
        image = request.files['image']
        
        if image:
            try:
                img = Image.open(image.stream)
                img.verify()
                img.seek(0)
                
                time_str = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
                image = image_preprocess(image, action, time_str)
                
                pred = predict(image)
                show_label = show_labels(image, pred)
                
                data = numpy_to_base64(show_label[0])
                label = show_label[1]
                    
            except (IOError, SyntaxError):
                flash('File Yang Diupload Salah, Silahkan Ulangi Proses Upload.', 'danger')
                return redirect(request.url)
            
        if action == 'Masuk':
            # Tangani aksi 'Masuk' di sini
            print("Masuk")
        elif action == 'Keluar':
            # Tangani aksi 'Keluar' di sini
            print("Keluar")
            
    return render_template('index.html', data=data, label=label)

def get_folders_info():
    # Implementasikan fungsi ini sesuai kebutuhan untuk mengembalikan informasi folder
    return []

if __name__ == '__main__':
    # Run Flask with SSL
    app.run(
        host='0.0.0.0',
        port=5001,
    )
