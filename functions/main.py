from flask import Flask, render_template, request, send_file
from PIL import Image
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files.get('signature')
        if not file or not file.filename.lower().endswith(('.jpg', '.jpeg')):
            return "Only JPG or JPEG files are allowed.", 400

        image = Image.open(file)

        # Resize to 6cm x 2cm at 300 DPI → 710px x 236px
        target_size = (710, 236)
        resized = image.resize(target_size, Image.LANCZOS)

        # Compress to 10–20 KB
        for quality in range(95, 10, -5):
            buffer = io.BytesIO()
            resized.save(buffer, format='JPEG', quality=quality)
            size_kb = buffer.tell() / 1024
            if 10 <= size_kb <= 20:
                buffer.seek(0)
                return send_file(buffer, as_attachment=True, download_name='resized_signature.jpg', mimetype='image/jpeg')

        return "Couldn't compress image between 10–20 KB. Try a simpler signature image.", 400

    return render_template('index.html')
