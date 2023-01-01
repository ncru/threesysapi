from dotenv import load_dotenv
from modules.TSdoc import *
from modules.threesys import *
from modules.responses import *
from flask import Flask, render_template, request

load_dotenv()
app = Flask(__name__)


@app.route("/")
def main():
    return default_route()


@app.route("/generate", methods=["POST"])
def generate():
    # check request file and initialize fitz document object into memory from request if passed
    result = initialize_request(request)

    # check if document is PDF
    if not result:
        return input_fail(0)

    # deconstruct result tuple
    (document, document_name) = result

    dimensions_passed = check_document_dimensions(document)

    # check if document is big enough for 1 inch margins
    if not dimensions_passed:
        return input_fail(1)

    # check to see if the dm location parameter is set. If not then default to bottom right
    dm_steg_location = (
        request.form["location"] if "location" in request.form else "bottom-right"
    )

    # initialize TSdoc, dm steg location is optional as it will default to bottom right.
    # also, if the user fails to specify either top-left, top-right, bottom-left, bottom-right
    # due to a typo, the api will default back to bottom-right
    ts_doc = TSdoc("generate", document_name, document, dm_steg_location)

    # return str(ts_doc.__dict__)
    return generate_if_hell(ts_doc)


@app.route("/verify", methods=["POST"])
def verify():
    # check request file and initialize fitz document object into memory from request if passed
    document = initialize_request(request)

    # check if document is PDF
    if not document:
        return input_fail(0)

    # initialize TSdoc
    ts_doc = TSdoc("verify", document)

    # return str(ts_doc.__dict__)
    return verify_if_hell(ts_doc)


if __name__ == "__main__":
    app.run()
