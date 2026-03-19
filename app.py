import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from utils.extractor import extract_resume_data, extract_text
from utils.ats_scorer import compute_ats_score

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filepath


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/extract", methods=["POST"])
def extract():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["resume"]
    if not file.filename or not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are supported"}), 400

    filepath = save_file(file)
    try:
        result = extract_resume_data(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route("/ats-score", methods=["POST"])
def ats_score():
    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400
    if "job_description" not in request.form or not request.form["job_description"].strip():
        return jsonify({"error": "Job description is required"}), 400

    file = request.files["resume"]
    if not file.filename or not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are supported"}), 400

    filepath = save_file(file)
    try:
        resume_text = extract_text(filepath)
        job_description = request.form["job_description"]
        result = compute_ats_score(resume_text, job_description)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)