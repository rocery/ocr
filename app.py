from flask import Flask, render_template, request, flash, redirect, url_for
from ocr_process_paddleocr import *
import time
from PIL import Image
from script.sql import get_tparkir_connection, masuk, keluar

app = Flask(__name__)
app.secret_key = 'itbekasioke'

@app.route('/', methods=['GET', 'POST'])
def index():
    data  = None
    time_str = None
    label = None
    date_str = None
    custom_date_time = None
    image_format = None
    
    if request.method == 'POST':
        action = request.form['action']
        image = request.files['image']
        
        if image:
            try:
                img = Image.open(image.stream)
                img.verify()
                img.seek(0)
                image_format = img.format.lower()
                
                time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                image = image_preprocess(image, action, time_str)
                
                pred = predict(image)
                
                if pred == False:
                    flash('Tidak Terdeteksi Plat Nomor Pada Gambar. Silahkan Ulangi Proses Upload.', 'danger')
                    return redirect(request.url)
                
                show_label = show_labels(image, pred)                
                label = show_label[1]
                data = numpy_to_base64(show_label[0])
                
                
                date_str = time.strftime("%Y-%m-%d", time.localtime())
                custom_date_time = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
                file_name = f"{label}_{action}_{custom_date_time}.{image_format}"
                
                # save_image_ocr(image, name_file, folder_date, time_input)
                save_image_ocr(show_label[0], file_name, date_str, time_str, label, action)
                
            except (IOError, SyntaxError):
                flash('File Yang Diupload Salah, Silahkan Ulangi Proses Upload.', 'danger')
                return redirect(request.url)
        
        conn = get_tparkir_connection()
        if action == 'Masuk': 
            # masuk(conn, '2024-08-15', a, '08:56:12', 'SASTRA')
            masuk(conn, date_str, label, time_str, 'security')
        elif action == 'Keluar':
            # keluar(conn, a, custom_tanggal_keluar, '12:34:56', 'ADI'
            keluar(conn, label, date_str, time_str, 'security')
            
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
