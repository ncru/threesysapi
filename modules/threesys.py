import datetime
import fitz
import io
from PIL import Image
import zxing
import treepoem
from pylibdmtx.pylibdmtx import decode as pylibdmtx_decode
from pyzbar.pyzbar import decode as pyzbar_decode


def put_steg_dm_in_pdf(pdf_file, steg_dm):
    w = 20
    allowance = 3
    first_page = pdf_file[0]
    (_x, _y, width, height) = first_page.rect
    rect = (
        width - (w + allowance),
        height - (w + allowance),
        width - allowance,
        height - allowance,
    )
    byteIO = io.BytesIO()
    steg_dm.save(byteIO, format="PNG")
    img_bytes = byteIO.getvalue()
    first_page.insert_image(rect, stream=img_bytes)
    return pdf_file


def check_dms_for_steganography(dm_paths):
    threesys_dms = []
    for path in dm_paths:
        _image = Image.open(path)
        read_result = read_steganography(_image)
        if read_result != False:
            threesys_dms.append(path)
    if len(threesys_dms) == 1:
        return threesys_dms[0]
    return False


def generate_message(metadata):
    now = datetime.datetime.now()
    author = metadata["author"]
    date_signed = f'{now.strftime("%B")} {now.day}, {now.year}'
    return f"This document was signed using 3-sys API on {date_signed} and is owned by {author}"


def generate_dm(pdf_file):
    metadata = pdf_file.metadata
    message = generate_message(metadata)

    # generate a dm with treepoem
    return treepoem.generate_barcode(
        barcode_type="datamatrix",
        data=message,
        options={
            # 'alttext': alttext,
            # 'scale': 5,
            # 'includetext': True if len(alttext) > 0 else False,
            "textxalign": "center",
            "textsize": 3,
            "padding": 2,
            "backgroundcolor": "ffffff",
        },
    )


def steganography(image, secret):
    chunk_size = 2
    # initialize necessary image components
    width, height = image.size
    image_map = image.load()

    # convert secret to workable binary stream
    secret_ascii = msg_to_ascii(secret)
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
    # save metadata to database
    return image


def read_steganography(image):
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


def grab_all_dms_from_images(paths):
    dms = []
    for path in paths:
        if is_dm(path):
            dms.append(path)
    return dms


def is_dm(path):
    result = read_dm_zxing(path)
    return True if result else False


def read_dm_zxing(path):
    reader = zxing.BarCodeReader()
    result = reader.decode(path)
    return result.raw


def read_dm_pylibdmtx(image):
    (decoded, rect) = pylibdmtx_decode(image)[0]
    return decoded.decode("utf-8")


def read_dm_zbar(image):
    (data, rect, polygon, orientation, quality) = pyzbar_decode(image)[0]
    return data.decode("utf-8")


def msg_to_ascii(str):
    formatted_str = str + "//3.sys//"
    ascii_str = "".join(format(ord(i), "08b") for i in formatted_str)
    return ascii_str


def chunkify(msg_ascii, chunk_size):
    return [msg_ascii[i: i + chunk_size] for i in range(0, len(msg_ascii), chunk_size)]


def margin_is_empty(pix_map):
    coords = []
    for x in range(pix_map.width):
        for y in range(pix_map.height):
            pixel = pix_map.pixel(x, y)
            if pixel != (255, 255, 255):
                coords.append((x, y))
    return True if len(coords) == 0 else False


def margins_passed(pdf_file):
    inch = 72

    for page in pdf_file:
        p_width = page.rect.width
        p_height = page.rect.height

        r_header = fitz.Rect(0, 0, p_width, inch)
        r_footer = fitz.Rect(0, p_height - inch, p_width, p_height)
        r_left = fitz.Rect(0, 0, inch, p_height)
        r_right = fitz.Rect(p_width - inch, 0, p_width, p_height)

        header = page.get_pixmap(clip=r_header)
        footer = page.get_pixmap(clip=r_footer)
        left = page.get_pixmap(clip=r_left)
        right = page.get_pixmap(clip=r_right)

        margins = [header, footer, left, right]

        for margin in margins:
            if not margin_is_empty(margin):
                return False
    return True


def grab_first_page_images(pdf_file):
    page = pdf_file[0]
    image_list = page.get_images()
    images = []
    for j, img in enumerate(image_list, start=1):
        xref = img[0]
        p = fitz.Pixmap(pdf_file, xref)
        image_bytes = p.tobytes()
        image = Image.open(io.BytesIO(image_bytes))
        images.append(image)
    return images
