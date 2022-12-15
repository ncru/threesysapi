import os
import psycopg2
from dotenv import load_dotenv
from modules.threesys import *
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import json


INSERT_ORIGPDFS_RETURN_ID = (
    "INSERT INTO origpdfs (orig_pdf_data) VALUES (%s) RETURNING orig_id;"
)

INSERT_THREESYSPDF_RETURN_ROW = "INSERT INTO threesyspdfs (pdf_metadata, pdf_data, origpdfs_id) VALUES (%s,%s, %s) RETURNING *;"

SELECT_ROW_THREESYSPDF = "SELECT * FROM threesyspdfs WHERE origpdfs_id = (%s);"

# check if orig pdf already exists in system
# check ppi and dimension of pdf

load_dotenv()
app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)
app.config["UPLOAD_FOLDER"] = "./uploads/"
app.config["PYTHONUNBUFFERED"] = True
ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def main():
    return render_template("index.html")


def initiate_images_and_get_paths(document, images):
    img_paths = []
    for i, image in enumerate(images):
        base_name = os.path.basename(document.name)
        img_name = secure_filename(
            f'tempimg-{i}-{base_name[: base_name.find(".pdf")]}.png'
        )
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], img_name)
        img_paths.append(img_path)
        image.save(img_path)
    return img_paths


def check_files(req):
    file = req.files["file"]
    if (
        "file" not in request.files
        or request.files["file"] == ""
        or not allowed_file(file.filename)
    ):
        return False
    return True


def generate_dm_and_add_to_pdf(document):
    orig_pdf_data = bytes(document.tobytes())
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_ORIGPDFS_RETURN_ID, (orig_pdf_data,))
            steg_id = cursor.fetchone()[0]

    ord_dm = generate_dm(document)
    steg_dm = steganography(ord_dm, str(steg_id))
    modified_document = put_steg_dm_in_pdf(document, steg_dm)
    base_name = os.path.basename(modified_document.name)
    new_name = secure_filename(
        f'{base_name[: base_name.find(".pdf")]}-signed.pdf')
    new_path = os.path.join(app.config["UPLOAD_FOLDER"], new_name)
    modified_document.save(new_path)
    metadata = json.dumps(modified_document.metadata)
    new_pdf_data = bytes(modified_document.tobytes())

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                INSERT_THREESYSPDF_RETURN_ROW, (metadata,
                                                new_pdf_data, steg_id)
            )

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ROW_THREESYSPDF, (steg_id,))

    return_data = io.BytesIO()
    with open(new_path, "rb") as fo:
        return_data.write(fo.read())
    return_data.seek(0)
    os.remove(new_path)
    return send_file(
        return_data,
        mimetype="application/pdf",
        download_name=new_name,
        # as_attachment=True,
    )


@app.route("/generate", methods=["POST"])
def generate():
    final_response = {}
    images = []
    file_path = ""
    if request.method == "POST":
        if not check_files(request):
            resp = jsonify(
                {
                    "message": "Invalid inputs"
                }
            )
            resp.status_code = 406
            return resp

        file = request.files["file"]
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"], secure_filename(file.filename)
        )
        file.save(file_path)
        document = fitz.open(file_path)
        images = grab_first_page_images(document)
        img_paths = initiate_images_and_get_paths(document, images)
        dm_paths = grab_all_dms_from_images(img_paths)
        if len(dm_paths) > 0:
            valid_dm_path = check_dms_for_steganography(dm_paths)
            if valid_dm_path != False:
                final_response = jsonify(
                    {
                        "message": "The document is already signed by 3.Sys, use /verify to check if valid"
                    }
                )
                final_response.status_code = 300
            else:
                final_response = generate_dm_and_add_to_pdf(document)
        elif margins_passed(document):
            final_response = generate_dm_and_add_to_pdf(document)
        else:
            final_response = jsonify(
                {
                    "message": "The document must have clear 1 inch margins"
                }
            )
            final_response.status_code = 400
        if images:
            for i, image in enumerate(images):
                image.close()
                os.remove(img_paths[i])
        document.close()
        os.remove(file_path)
        return final_response


@app.route("/verify", methods=["POST"])
def verify():
    final_response = {}
    images = []
    file_path = ""
    if request.method == "POST":
        if not check_files(request):
            return {
                "message": "Invalid inputs",
            }, 406

        file = request.files["file"]
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"], secure_filename(file.filename)
        )
        file.save(file_path)
        document = fitz.open(file_path)
        images = grab_first_page_images(document)
        img_paths = initiate_images_and_get_paths(document, images)
        dm_paths = grab_all_dms_from_images(img_paths)
        if len(dm_paths) > 0:
            valid_dm_path = check_dms_for_steganography(dm_paths)
            if valid_dm_path != False:
                _image = Image.open(valid_dm_path)
                # reg_msg = read_dm_zxing(valid_dm_path)
                reg_msg = read_dm_pylibdmtx(_image)
                steg_msg = read_steganography(_image)
                metadata = document.metadata
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(SELECT_ROW_THREESYSPDF, (steg_msg,))
                        if cursor.rowcount > 0:
                            (
                                rpdf_id,
                                rpdf_metadata,
                                rpdf_data,
                                rorigpdfs_id,
                            ) = cursor.fetchall()[0]
                            if metadata == rpdf_metadata:
                                final_response = jsonify(
                                    {
                                        "message": "This is a signed and valid document",
                                        "plain": reg_msg
                                    }
                                )
                                final_response.status_code = 200
                            else:
                                final_response = jsonify(
                                    {
                                        "message": "This is a falsified document"
                                    }
                                )
                            final_response.status_code = 200
                        else:
                            final_response = jsonify(
                                {
                                    "message": "This is a falsified document and has not gone through /generate"
                                }
                            )
                            final_response.status_code = 502

            else:
                final_response = jsonify(
                    {
                        "message": "The document is not signed by 3.Sys"
                    }
                )
                final_response.status_code = 406
        else:
            final_response = jsonify(
                {
                    "message": "This document has not been validated"
                }
            )
            final_response.status_code = 300
        if images:
            for i, image in enumerate(images):
                image.close()
                os.remove(img_paths[i])
        document.close()
        os.remove(file_path)
        return final_response


if __name__ == "__main__":
    app.run()
