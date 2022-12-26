import os
import psycopg2
from dotenv import load_dotenv
from modules.threesys_document import *
from modules.new_threesys import *
from flask import Flask, render_template, request, send_file, jsonify


INSERT_ORIGPDFS_RETURN_ID = "INSERT INTO origpdfs (orig_pdf_data, orig_pdf_metadata) VALUES (%s, %s) RETURNING orig_id;"

INSERT_THREESYSPDF_RETURN_ROW = "INSERT INTO threesyspdfs (pdf_metadata, pdf_data, origpdfs_id) VALUES (%s,%s, %s) RETURNING *;"

SELECT_ROW_ORIGPDFS = "SELECT orig_pdf_metadata -> 'author' AS author, orig_pdf_metadata -> 'creationDate' AS creationdate, orig_pdf_metadata -> 'modDate' AS moddate FROM origpdfs WHERE orig_pdf_metadata ->> 'author' = %s AND orig_pdf_metadata ->> 'creationDate' = %s AND orig_pdf_metadata ->> 'modDate' = %s"

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


@app.route("/generate", methods=["POST"])
def generate():
    # initialize fitz document object into memory from request
    document = initialize_request_file(request)

    # initialize TSdoc
    test = TSdoc(document)

    # if hell
    # return generate_if_hell()


@app.route("/verify", methods=["GET"])
def verify():
    return


if __name__ == "__main__":
    app.run()
