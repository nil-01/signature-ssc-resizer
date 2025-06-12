from flask import Flask, request, jsonify, render_template
from PIL import Image
import io

app = Flask(__name__, template_folder="templates")

def cm_to_pixels(cm, dpi):
    return int((cm / 2.54) * dpi)

EXPECTED_WIDTH_CM = 6.0
EXPECTED_HEIGHT_CM = 2.0
DPI = 300
WIDTH_PX = cm_to_pixels(EXPECTED_WIDTH_CM, DPI)
HEIGHT_PX = cm_to_pixels(EXPECTED_HEIGHT_CM, DPI)
ALLOWED_EXTENSIONS = ['jpeg', 'jpg']

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/validate-signature', methods=['POST'])
def validate_signature():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
        return jsonify({"error": "File must be JPEG or JPG format"}), 400

    file.seek(0, io.SEEK_END)
    size_kb = file.tell() / 1024
    file.seek(0)

    if size_kb < 10 or size_kb > 20:
        return jsonify({"error": f"File size must be between 10KB and 20KB. Current: {size_kb:.2f}KB"}), 400

    image = Image.open(file)
    width, height = image.size

    dpi_info = image.info.get('dpi', (72, 72))
    if dpi_info[0] != 300 or dpi_info[1] != 300:
        return jsonify({"error": f"Image DPI must be 300. Found: {dpi_info}"}), 400

    width_min = WIDTH_PX * 0.95
    width_max = WIDTH_PX * 1.05
    height_min = HEIGHT_PX * 0.95
    height_max = HEIGHT_PX * 1.05

    if not (width_min <= width <= width_max and height_min <= height <= height_max):
        return jsonify({
            "error": f"Image dimensions should be approx 6.0cm x 2.0cm (at 300 DPI). Found: {width}px x {height}px"
        }), 400

    aspect_ratio = width / height
    if aspect_ratio < 2.5:
        return jsonify({
            "error": f"Signature should be horizontally aligned. Aspect ratio is low: {aspect_ratio:.2f}"
        }), 400

    return jsonify({
        "success": True,
        "message": "Signature image passed all validations",
        "size_kb": f"{size_kb:.2f}",
        "dimensions_px": f"{width}x{height}",
        "dpi": dpi_info
    }), 200
