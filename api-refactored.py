from dotenv import load_dotenv
from modules.TSdoc import *
from modules.new_threesys import *
from modules.responses import *
from flask import Flask, render_template, request

load_dotenv()
app = Flask(__name__)
app.config["PYTHONUNBUFFERED"] = True


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    # check request file and initialize fitz document object into memory from request if passed
    document = initialize_request(request)

    # check if document is PDF
    if not document:
        return "PDF ERROR"

    dimensions_passed = check_document_dimensions(document)

    # check if document is big enough for 1 inch margins
    if not dimensions_passed:
        return "SIZE ERROR"

    # check to see if the dm location parameter is set. If not then default to bottom right
    dm_steg_location = request.form["location"] if "location" in request.form else "bottom-right"

    # initialize TSdoc, dm steg location is optional as it will default to bottom right
    ts_doc = TSdoc(document, dm_steg_location)

    # return str(ts_doc.__dict__)
    return generate_if_hell(ts_doc)


@ app.route("/verify", methods=["GET"])
def verify():
    # check request file and initialize fitz document object into memory from request if passed
    document = initialize_request(request)

    # check if document is PDF
    if not document:
        return "PDF ERROR"

    # initialize TSdoc
    ts_doc = TSdoc(document)

    # return str(ts_doc.__dict__)
    return verify_if_hell(ts_doc)


if __name__ == "__main__":
    app.run()
