import fitz
from pylibdmtx.pylibdmtx import decode as pylibdmtx_decode
import os
import psycopg2
from psycopg2 import Error
import json
import treepoem
import datetime
import io
import math
import hashlib


ALLOWED_EXTENSIONS = {"pdf"}
url = os.getenv("DATABASE_URL")
allowance = 3


# checks the request file if it is a pdf. If it is, then it is read into
# memory for api manipulation
def initialize_request(req):
    print("initialize_request")
    file = req.files["file"]
    if (
        "file" not in req.files
        or req.files["file"] == ""
        or not allowed_file(file.filename)
    ):
        return False
    file_stream = file.read()
    document = fitz.open(stream=file_stream, filetype="pdf")
    return (document, file.filename)


# utility function for initialize_request_file which breaks down the name of a file
# to derive its file type and returns if whether or not the file is a file type contained
# within ALLOWED_EXTENSIONS
def allowed_file(filename):
    print("allowed_file")
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# # function that ensures that the metadata of the document isn't empty. This must be done
# # because the API makes use of metadata to check validity
# def check_document_metadata(document):
#     print("check_document_metadata")
#     metadata = document.metadata
#     author = metadata["author"]
#     creation_date = metadata["creationDate"]
#     mod_date = metadata["modDate"]
#     if not author or not creation_date or not mod_date:
#         return False
#     return True


# checks if document has enough space for 1 inch defined margins. The limit variable
# is defined by 2 times an inch (1 inch = 72 pixels for 72 ppi document which is the
# standard)
def check_document_dimensions(document):
    print("check_document_dimensions")
    limit = 72 * 2
    for page in document:
        page_width = math.floor(page.rect.width)
        page_height = math.floor(page.rect.height)
        if page_width <= limit or page_height <= limit:
            return False
    return True


# reads the regular payload of the dm
def read_dm_pylibdmtx(image):
    print("read_dm_pylibdmtx")
    image_width, image_height = image.size
    if image_width > 350 and image_height > 350:
        return ""
    result = pylibdmtx_decode(image)
    if not result:
        return ""
    (decoded, rect) = result[0]
    return decoded.decode("utf-8")


# novel algorithm which reads 3.Sys steganography
def read_steganography(image):
    print("read_steganography")
    chunk_size = 2
    width, height = image.size
    image_map = image.load()
    msg = []
    byte = ""
    for i in range(width):
        for j in range(height):
            (r, g, b) = image_map[i, j]
            bin_r = format(r, "08b")
            chunk = bin_r[-chunk_size:]
            byte += chunk
            if len(byte) == 8:
                msg.append(chr(int(byte, 2)))
                byte = ""
    dirty_msg = "".join(msg)
    marker_i = dirty_msg.find("//3.sys//")
    if marker_i != -1:
        return dirty_msg[:marker_i]
    return False


# saves the document to the origpdfs table in 3.Sys db and returns the
# id of that generated row
def save_orig_doc_to_db(document, document_hash):
    print("save_orig_doc_to_db")
    orig_pdf_data = document.tobytes()
    QUERY = "INSERT INTO origpdfs (orig_pdf_data, orig_pdf_hash) VALUES (%s, %s) RETURNING orig_id;"
    try:
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(QUERY, (orig_pdf_data, document_hash))
                return cursor.fetchone()[0]
    except (Exception, Error) as error:
        return f"Error while connecting to PostgreSQL, {error}"
    finally:
        if connection:
            cursor.close()
            connection.close()


# saves the modified document to the threesyspdf table in 3.Sys db
def save_modified_doc_to_db(new_pdf_data, steg_id):
    print("save_modified_doc_to_db")
    modified_document_hash = hashlib.sha256(new_pdf_data).hexdigest()
    QUERY = "INSERT INTO threesyspdfs (pdf_hash, pdf_data, origpdfs_id) VALUES (%s,%s, %s) RETURNING *;"
    try:
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    QUERY, (modified_document_hash, new_pdf_data, steg_id))
    except (Exception, Error) as error:
        return f"Error while connecting to PostgreSQL, {error}"
    finally:
        if connection:
            cursor.close()
            connection.close()


# generate a dm with the treepoem module
def generate_dm(pdf_file):
    print("generate_dm")
    metadata = pdf_file.metadata
    message = generate_message(metadata)
    return treepoem.generate_barcode(
        barcode_type="datamatrix",
        data=message,
        options={
            "textxalign": "center",
            "textsize": 3,
            "padding": 2,
            "backgroundcolor": "ffffff",
        },
    )


# utility function for generate_dm that generates a secret message
# based on the given metadata to be steganographized
def generate_message(metadata):
    print("generate_message")
    now = datetime.datetime.now()
    author = metadata["author"] if metadata["author"] else "anonymous"
    date_signed = f'{now.strftime("%B")} {now.day}, {now.year}'
    return f"This document was signed using 3.Sys API on {date_signed} and is owned by {author}"


# novel steganography function that uses LSB to hide the secret message in the last bits
# (defined by chunk_size) of every pixel, red channel
def steganography(image, secret):
    print("steganography")
    chunk_size = 2
    # initialize necessary image components
    width, height = image.size
    image_map = image.load()

    # convert secret to workable binary stream
    secret_ascii = msg_to_binary_stream(secret)
    secret_chunks = chunkify(secret_ascii, chunk_size)

    # loop that replaces the least significat n values of each R byte
    # in each pixel with its corresponding secret message chunk of n bits
    for i in range(width):
        for j in range(height):
            secret_chunks_index = i * height + j
            if secret_chunks_index < len(secret_chunks):
                secret_portion = secret_chunks[secret_chunks_index]
                (r, g, b) = image_map[i, j]
                bin_r = format(r, "08b")
                new_bin_r = bin_r[:-chunk_size] + secret_portion
                new_r = int(new_bin_r, 2)
                image.putpixel((i, j), (new_r, g, b))
    return image


# utility function for steganography that converts a string into a binary stream
def msg_to_binary_stream(str):
    print("msg_to_binary_stream")
    formatted_str = str + "//3.sys//"
    ascii_str = "".join(format(ord(i), "08b") for i in formatted_str)
    return ascii_str


# utility function for steganography that splits the given binary_stream into chunk_size
# define chunks
def chunkify(binary_stream, chunk_size):
    print("chunkify")
    return [
        binary_stream[i: i + chunk_size]
        for i in range(0, len(binary_stream), chunk_size)
    ]


# attaches generated steg dms to the specified location on the document
def put_steg_dm_in_pdf(pdf_file, steg_dm, dm_steg_location):
    print("put_steg_dm_in_pdf")
    dm_width = (72 - (2 * allowance)) / 2  # for a half inch sized dm
    first_page = pdf_file[0]
    (_x, _y, page_width, page_height) = first_page.rect

    match dm_steg_location:
        case "top-left":
            x1 = allowance
            y1 = allowance
            x2 = dm_width + allowance
            y2 = dm_width + allowance
        case "top-right":
            x1 = page_width - dm_width - allowance
            y1 = allowance
            x2 = page_width - allowance
            y2 = allowance + dm_width
        case "bottom-left":
            x1 = allowance
            y1 = page_height - dm_width - allowance
            x2 = allowance + dm_width
            y2 = page_height - allowance
        case "bottom-right":
            x1 = page_width - dm_width - allowance
            y1 = page_height - dm_width - allowance
            x2 = page_width - allowance
            y2 = page_height - allowance

    rect = (x1, y1, x2, y2)
    byteIO = io.BytesIO()
    steg_dm.save(byteIO, format="PNG")
    img_bytes = byteIO.getvalue()
    first_page.insert_image(rect, stream=img_bytes)
    return pdf_file


# checks if whether or not the input (unsigned) document has already been previously
# signed by a 3.Sys signature.
def check_if_doc_is_already_prev_signed(document_hash):
    print("check_if_doc_is_already_prev_signed")
    QUERY = "SELECT * FROM origpdfs WHERE orig_pdf_hash = (%s);"
    try:
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(QUERY, (document_hash,))
                if cursor.rowcount > 0:
                    (
                        origpdf_id,
                        origpdf_hash,
                        origpdf_data,
                    ) = cursor.fetchall()[0]
                    print("Db hash:", origpdf_hash)
        print("Curr hash:", document_hash)
        print("Sign status:", cursor.rowcount > 0)
        return cursor.rowcount > 0
    except (Exception, Error) as error:
        return f"Error while connecting to PostgreSQL, {error}"
    finally:
        if connection:
            cursor.close()
            connection.close()


# defines if whether or not the document has been modifed
def check_if_document_is_modified(document_hash, dm_stegs):
    print("check☺_if_document_is_modified")
    if len(dm_stegs) != 1:
        return True
    dm_steg = dm_stegs[0]
    steg_msg = read_steganography(dm_steg)
    QUERY = "SELECT * FROM threesyspdfs WHERE origpdfs_id = (%s);"
    try:
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(QUERY, (steg_msg,))
                if cursor.rowcount > 0:
                    (
                        rpdf_id,
                        rpdf_hash,
                        rpdf_data,
                        rorigpdfs_id,
                    ) = cursor.fetchall()[0]
                    return not document_hash == rpdf_hash
                else:
                    return True
    except (Exception, Error) as error:
        return f"Error while connecting to PostgreSQL, {error}"
    finally:
        if connection:
            cursor.close()
            connection.close()


def get_hash_of_document(document):
    print("get_hash_of_document")
    document_bytes = document.tobytes(no_new_id=True)
    docu_hash = hashlib.sha256(document_bytes).hexdigest()
    return docu_hash
