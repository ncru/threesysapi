import fitz
import io
from PIL import Image
from modules.threesys import *


# class definition that allows the api to define the five document traits of
# margin, images, dm images, dm stegs, and modified
class TSdoc:
    # initialize GenereateTSdoc the 5 notable traits and the desired location for
    # the dm-steg to be located (default is bottom right)
    def __init__(self, mode, document_name, document, dm_steg_location=None):
        self.mode = mode
        self.document_name = document_name
        # string of the location where the user may or may not have defined where to put the steg dm
        self.dm_steg_location = self.check_set_dm_steg_location(dm_steg_location)
        # this is a fitz document object
        self.document = document
        # get hash and bytes of the document
        (self.hash, self.bytes) = get_hash_and_bytes_of_document(self.document)
        # A boolean of if the document has already been previously signed by 3.Sys
        self.already_signed = check_if_doc_is_already_prev_signed(self.hash)
        # a list of all the document images (may be empty)
        self.images = self.grab_all_first_page_images()
        # a list of all dms derived from self.images (may be empty)
        self.dm_images = self.grab_all_dms_from_images()
        # a list of all dm stegs from self.dm_images (may be empty)
        self.dm_stegs = self.grab_all_dm_steg_from_dms()

        # All 5 binary traits
        self.traits = {
            # True means margins are clean and can hold the dm steg as specified by  self.dm_steg_location, False otherwise
            "margins": self.document_margins_passed()
            if self.mode == "generate"
            else True,
            "images": True if self.images else False,
            "dm_images": True if self.dm_images else False,
            "dm_steg": True if self.dm_stegs else False,
            # this is set to default False as it will only be determined by the /verify endpoint
            "modified": check_if_document_is_modified(self.hash, self.dm_stegs)
            if self.dm_stegs
            else False,
        }

        if not self.traits["modified"] and self.dm_stegs:
            self.regular_dm_payload = read_dm_pylibdmtx(self.dm_stegs[0])

    def check_set_dm_steg_location(self, location):
        match location:
            case "top-left" | "top-right" | "bottom-left" | "bottom-right":
                return location
            case _:
                return "bottom-right"

    # mother function for checking if the margins of the document have enough
    # white pixel space for the dm-steg to be placed in.
    def document_margins_passed(self):
        print("document_margins_passed")
        inch = 72
        page = self.document[0]

        dm_width = 72 - (2 * allowance)
        padded_dm = dm_width + (2 * allowance)

        page_width = page.rect.width
        page_height = page.rect.height
        match self.dm_steg_location:
            case "top-left":
                corner = fitz.Rect(
                    page_width - padded_dm,
                    page_height - padded_dm,
                    page_width,
                    page_height,
                )
            case "top-right":
                corner = fitz.Rect(page_width - padded_dm, 0, page_width, padded_dm)
            case "bottom-left":
                corner = fitz.Rect(0, page_height - padded_dm, padded_dm, page_height)
            case "bottom-right":
                corner = fitz.Rect(0, 0, padded_dm, padded_dm)

        dm_area = page.get_pixmap(clip=corner)
        return dm_area.is_unicolor

    # indiscirminantly grabs all the images from the first page of the document
    def grab_all_first_page_images(self):
        print("grab_all_first_page_images")
        page = self.document[0]
        image_list = page.get_images()
        images = []
        for j, img in enumerate(image_list, start=1):
            xref = img[0]
            pix = fitz.Pixmap(self.document, xref)

            if pix.colorspace.name == "DeviceCMYK":
                continue

            image_bytes = pix.tobytes()
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert("RGB")
            images.append(image)
        return images

    # filters out the dms from the collected document images
    def grab_all_dms_from_images(self):
        print("grab_all_dms_from_images")
        if not self.images:
            return []
        return list(
            filter(lambda img: True if read_dm_pylibdmtx(img) else False, self.images)
        )

    # reads every collected dm from the document (if there are any) and checks to see
    # if there are any with valid 3.Sys This function will return false if there are multiple
    # steg valid dms because this is an indicator of a falsified document

    def grab_all_dm_steg_from_dms(self):
        print("grab_all_dm_steg_from_dms")
        if not self.dm_images:
            return []
        return list(
            filter(
                lambda img: True if read_steganography(img) else False, self.dm_images
            )
        )

    # generate a dm, steganographize it and add it to the document at the specified location

    def generate_dm_and_add_to_pdf(self):
        print("generate_dm_and_add_to_pdf")
        steg_id = save_orig_doc_to_db(self.hash, self.bytes)
        ord_dm = generate_dm(self.document)
        steg_dm = steganography(ord_dm, str(steg_id))
        modified_document = put_steg_dm_in_pdf(
            self.document, steg_dm, self.dm_steg_location
        )
        (new_pdf_hash, new_pdf_bytes) = get_hash_and_bytes_of_document(
            modified_document
        )
        save_modified_doc_to_db(new_pdf_hash, new_pdf_bytes, steg_id)
        new_name = f'{self.document_name [:self.document_name.find(".pdf")]}-signed.pdf'
        return (new_pdf_bytes, new_name)
