from PIL import Image
import treepoem
from pylibdmtx.pylibdmtx import decode as pylibdmtx_decode
from pyzbar.pyzbar import decode as pyzbar_decode


def msg_to_ascii(str):
    formatted_str = str + "//3.sys//"
    ascii_str = "".join(format(ord(i), "08b") for i in formatted_str)
    return ascii_str


def chunkify(msg_ascii, chunk_size):
    return [msg_ascii[i: i + chunk_size] for i in range(0, len(msg_ascii), chunk_size)]


def generate_dm():
    message = 'Hello world!'

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


def steganography(image):
    secret = 'This is a very big secret and I have no more things to say! This is a very big secret and I have no more things to say! This is a very big secret and I have no more things to say! This is a very big secret and I have no more things to say! This is a very big secret and I have no more things to say! This is a very big secret and I have no more things to say! This is a very big secret and I have no more things to say! This is a very big secret and I have no more things to say! '
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


img = generate_dm()
steg = steganography(img)
print(steg)
steg.save('test.png')
