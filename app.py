from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pdf2docx import Converter
from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
import pandas as pd
import os
import re
from urllib.parse import quote

# إعداد التطبيق
app = Flask(__name__)
CORS(app)



# إعداد مسارات المجلدات
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# التحقق من نوع الملف المسموح
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return('index.html')  # عرض ملف index.html


# تحويل PDF إلى Word
@app.route('/convert-pdf-to-word', methods=['POST'])
def convert_pdf_to_word():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "لا يوجد ملف مرفق!"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "لم يتم اختيار ملف!"}), 400

        if not allowed_file(file.filename) or file.filename.rsplit('.', 1)[1].lower() != 'pdf':
            return jsonify({"error": "الملف غير مدعوم! يرجى رفع ملف PDF فقط."}), 400

        original_filename = file.filename
        clean_filename = re.sub(r'[^\w\s-]', '', original_filename).replace(' ', '_')
        clean_filename = clean_filename.rsplit('.', 1)[0] + '.docx'

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        docx_path = os.path.join(CONVERTED_FOLDER, clean_filename)
        cv = Converter(file_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()

        download_url = f"{request.host_url}download/{quote(clean_filename)}"
        return jsonify({"message": "تم تحويل الملف بنجاح!", "download_link": download_url}), 200
    except Exception as e:
        return jsonify({"error": f"حدث خطأ أثناء التحويل: {str(e)}"}), 500

# ضغط ملفات PDF
@app.route('/compress-pdf', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "لا يوجد ملف مرفق!"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "لم يتم اختيار ملف!"}), 400

    if not allowed_file(file.filename) or file.filename.rsplit('.', 1)[1].lower() != 'pdf':
        return jsonify({"error": "الملف غير مدعوم! يرجى رفع ملف PDF فقط."}), 400

    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # ضغط الملف
        compressed_filename = f"compressed_{file.filename}"
        compressed_path = os.path.join(CONVERTED_FOLDER, compressed_filename)
        reader = PdfReader(file_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        with open(compressed_path, 'wb') as output_pdf:
            writer.write(output_pdf)

        download_url = f"{request.host_url}download/{quote(compressed_filename)}"
        return jsonify({"message": "تم ضغط الملف بنجاح!", "download_link": download_url}), 200
    except Exception as e:
        return jsonify({"error": f"حدث خطأ أثناء ضغط الملف: {str(e)}"}), 500


# تحويل Excel إلى PDF
@app.route('/convert-excel-to-pdf', methods=['POST'])
def convert_excel_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "لا يوجد ملف مرفق!"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "لم يتم اختيار ملف!"}), 400

    if not allowed_file(file.filename) or file.filename.rsplit('.', 1)[1].lower() not in {'xlsx', 'xls'}:
        return jsonify({"error": "الملف غير مدعوم! يرجى رفع ملف Excel فقط."}), 400

    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # تحويل Excel إلى PDF
        pdf_filename = f"{file.filename.rsplit('.', 1)[0]}.pdf"
        pdf_path = os.path.join(CONVERTED_FOLDER, pdf_filename)
        df = pd.read_excel(file_path)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for index, row in df.iterrows():
            pdf.cell(200, 10, txt=", ".join(map(str, row.values)), ln=True)

        pdf.output(pdf_path)

        download_url = f"{request.host_url}download/{quote(pdf_filename)}"
        return jsonify({"message": "تم تحويل الملف بنجاح!", "download_link": download_url}), 200
    except Exception as e:
        return jsonify({"error": f"حدث خطأ أثناء تحويل الملف: {str(e)}"}), 500


# تنزيل الملفات
@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(CONVERTED_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "الملف غير موجود!"}), 404


# تشغيل الخادم
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500, debug=True)
