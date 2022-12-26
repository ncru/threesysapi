import datetime
import fitz
import io
from PIL import Image
import zxing
import treepoem
from pylibdmtx.pylibdmtx import decode as pylibdmtx_decode
from pyzbar.pyzbar import decode as pyzbar_decode


def initialize_request_file(req):
    file = req.files["file"]
    with open(file.name, "rb") as iamge_file:
        file_stream = iamge_file.read()
    document = fitz.open(stream=file_stream, filetype="pdf")
    return document


def generate_if_hell():
