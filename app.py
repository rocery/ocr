from flask import Flask, render_template, request, flash, redirect, url_for, session
from ocr_process_paddleocr import *
import time
from PIL import Image
from script.sql import get_tparkir_connection, masuk, keluar, get_data_ocr, keperluan, masuk_220, keluar_220
from script.char_prosess import character_check
from script.owi import detect_and_return_cropped_license_plate
import datetime

app = Flask(__name__)
app.secret_key = 'itbekasioke'
USER_SECRET_KEY = 'user123'
label_for_update = None

@app.route('/ocr/login_ocr', methods=['GET', 'POST'])
def login_ocr():
    if request.method == 'POST':
        secret_key = request.form.get('secret_key')
        if secret_key == USER_SECRET_KEY:
            session['authenticated'] = True
            return redirect(url_for('ocr'))
        else:
            flash('Password salah, silahkan coba kembali.', 'danger')
    
    return render_template('login.html')

@app.route('/ocr', methods=['GET', 'POST'])
def ocr():
    if not session.get('authenticated'):
        return redirect(url_for('login_ocr'))
    
    data  = None
    time_str = None
    label = None
    date_str = None
    custom_date_time = None
    image_format = None
    show_label = None
    action = None
    file_name = None
    ocr_ = False
    sql_output = None
    message_type = None
    
    csv_data = read_data_csv()
    
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
                
                try:
                    image = detect_and_return_cropped_license_plate(image)
                except:
                    sql_output = 'Tidak Terdeteksi Plat Nomor Pada Gambar. Silahkan Ulangi Proses Upload. Error Code: 0x1'
                    message_type = 'danger'
                    flash(sql_output, message_type)
                    return render_template('ocr.html', csv_data=csv_data, message=sql_output, message_type=message_type)
                
                pred = predict(image)
                
                if pred == False:
                    sql_output = 'Tidak Terdeteksi Huruf-Angka Pada Foro. Silahkan Ulangi Proses Upload. Erroe Code: 0x2'
                    message_type = 'danger'
                    flash(sql_output, message_type)
                    return render_template('ocr.html', csv_data=csv_data, message=sql_output, message_type=message_type)
                
                show_label = show_labels(image, pred)                
                label = show_label[1]
                global label_for_update
                label_for_update = label
                data = numpy_to_base64(show_label[0])
                
                if character_check(label) == False:
                    sql_output = 'Plat Nomor Pada Foto Tidak Valid/Salah Baca. Silahkan Foto Ulang lalu Ulangi Proses Upload. Error Code: 0x3'
                    message_type = 'danger'
                    flash(sql_output, message_type)
                    return render_template('ocr.html', data=data, label=label, csv_data=csv_data, message=sql_output, message_type=message_type)
                
                date_str = time.strftime("%Y-%m-%d", time.localtime())
                custom_date_time = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
                file_name = f"{label}_{action}_{custom_date_time}.{image_format}"
                
                # # save_image_ocr(image, name_file, folder_date, time_input)
                # save_image_ocr(show_label[0], file_name, date_str, time_str, label, action)
                
            except (IOError, SyntaxError):
                flash('Foto Yang Diupload Salah, Silahkan Ulangi Proses Upload. Error Code: 0x4', 'danger')
                return redirect(request.url)
        
        conn = get_tparkir_connection()
        if action == 'Masuk': 
            # masuk(conn, '2024-08-15', a, '08:56:12', 'SASTRA')
            status = masuk(conn, date_str, label, time_str, 'security')
            
            if status == 'inside':
                sql_output = 'Status Terakhir Kendaraan {}: "Didalam/Masuk".\nPerlu Proses "Keluar".'.format(label)
                message_type = 'danger'
                ocr_ = False
            elif status == 'noeks':
                list_keperluan = ['Tamu', 'Logistik', 'Sampah', 'BS', 'Interview', 'Lainnya']
                # sql_output = 'Data Ekspedisi Kendaraan {} Tidak Ditemukan.\nData Tetap Diproses sebagai "Tamu".'.format(label)
                sql_output = 'Data Ekspedisi Kendaraan {} Tidak Ditemukan.\nMohon Input Keperluan.'.format(label)
                message_type = 'warning'
                ocr_ = True
                save_image_ocr(show_label[0], file_name, date_str, time_str, label, action)
                # flash(sql_output, message_type)
                return render_template('ocr.html',
                           data=data,
                           label=label,
                           message=sql_output,
                           message_type=message_type,
                           csv_data=csv_data,
                           list_keperluan=list_keperluan,
                           show_popup_keperluan=True)
            else:
                sql_output = 'Kendaraan {} Berhasil "Masuk"\nEkspedisi: {}.'.format(label, status)
                message_type = 'success'
                ocr_ = True
            
                # Akan diproses jika status kendaraan tidak sedang didalam dan ekspedisi terdaftar
                masuk_220(date_str, label, time_str, 'security')
            
        elif action == 'Keluar':
            # keluar(conn, a, custom_tanggal_keluar, '12:34:56', 'ADI'
            status = keluar(conn, label, date_str, time_str, 'security')
            status_220 = keluar_220(label, date_str, time_str, 'security')
            
            print(status)
            print(status_220)
            # Jika status kendaraan sedang diluar, maka gagal input data
            
            if status == 'outside' or status_220 == 'outside':
                sql_output = 'Status Terakhir Kendaraan {}: "Diluar/Keluar/Tidak Ada".\nPerlu Proses "Masuk".'.format(label)
                message_type = 'danger'
                ocr_ = False
            # elif status != status_220:
            #     sql_output = 'Status Terakhir Kendaraan Tamu {}: "Diluar/Keluar/Tidak Ada".\nPerlu Proses "Masuk".'.format(label)
            #     message_type = 'danger'
            #     ocr_ = False
            else:
                sql_output = 'Kendaraan {} Berhasil "Keluar".'.format(label)
                message_type = 'success'
                ocr_ = True
                
        flash(sql_output, message_type)
        
        # save_image_ocr(image, name_file, folder_date, time_input)
        if ocr_ == True:
            save_image_ocr(show_label[0], file_name, date_str, time_str, label, action)
        elif ocr_ == False:
            pass
    
    csv_data = read_data_csv()    
    return render_template('ocr.html',
                           data=data,
                           label=label,
                           message=sql_output,
                           message_type=message_type,
                           csv_data=csv_data)

@app.route('/ocr/data_ocr', methods=['GET', 'POST'])
def data_ocr():
    if not session.get('authenticated'):
        return redirect(url_for('login_ocr'))
    
    data_ocr = get_data_ocr()
    return render_template('data_ocr.html', data_ocr=data_ocr, datetime=datetime)

@app.route('/ocr/submit_keperluan', methods=['GET', 'POST'])
def submit_keperluan():
    post_keperluan = request.form.get('keperluan')
    post_label = request.form.get('no_mobil')
    
    if not post_keperluan or not post_label:
        flash("Proses Input Tamu Gagal", "danger")
        return redirect(url_for('ocr'))
    
    txt = None
    sts = None
    update_220 = None
    update = keperluan(post_label, post_keperluan)
    
    date_str = time.strftime("%Y-%m-%d", time.localtime())
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if post_keperluan == 'Logistik':
        update_220 = masuk_220(date_str, post_label, time_str, 'security')
    
    if update or update_220 == "Success":
        txt = "Proses Masuk Kendaraan: {} Berhasil.\nKeperluan: {}".format(post_label, post_keperluan)
        sts = "success"
    else:
        txt = "Proses Masuk Kendaraan: {} Gagal.\nKeperluan: {}".format(post_label, post_keperluan)
        sts = "danger"
        
    flash(txt, sts)
    return redirect(url_for('ocr'))

if __name__ == '__main__':
    # Run Flask with SSL
    app.run(
        host='0.0.0.0',
        port=5000,
    )
