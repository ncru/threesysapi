import fitz
import io
from PIL import Image
from modules.threesys import *


# class definition that allows the api to define the five document traits of
# margin, images, dm images, dm stegs, and modified
class TSdoc:
    # initialize GenereateTSdoc the 5 notable traits and the desired location for
    # the dm-steg to be located (default is bottom right)
    def __init__(self, document, dm_steg_location=None):
        # string of the location where the user may or may not have defined where to put the steg dm
        self.dm_steg_location = self.check_set_dm_steg_location(
            dm_steg_location)
        # this is a fitz document object
        self.document = document
        # A boolean of if the document has already been previously signed by 3.Sys
        self.already_signed = check_if_doc_is_already_prev_signed(
            self.document)
        # a list of all the document images (may be empty)
        self.images = self.grab_all_first_page_images()
        # a list of all dms derived from self.images (may be empty)
        self.dm_images = self.grab_all_dms_from_images()
        # a list of all dm stegs from self.dm_images (may be empty)
        self.dm_stegs = self.grab_all_dm_steg_from_dms()

        # All 5 binary traits
        self.traits = {
            # True means margins are clean and can hold the dm steg as specified by  self.dm_steg_location, False otherwise
            "margins": self.document_margins_passed() if self.dm_steg_location else True,
            "images": True if self.images else False,
            "dm_images": True if self.dm_images else False,
            "dm_steg": True if self.dm_stegs else False,
            # this is set to default False as it will only be determined by the /verify endpoint
            "modified": check_if_document_is_modified(self.document, self.dm_stegs)
            if self.dm_stegs
            else False,
        }

        if not self.traits["modified"] and self.dm_stegs:
            self.regular_dm_payload = read_dm_pylibdmtx(self.dm_stegs[0])

    def check_set_dm_steg_location(location):
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
        page_width = page.rect.width
        page_height = page.rect.height

        rect_header = fitz.Rect(0, 0, page_width, inch)
        rect_footer = fitz.Rect(0, page_height - inch, page_width, page_height)

        header = page.get_pixmap(clip=rect_header)
        footer = page.get_pixmap(clip=rect_footer)

        match self.dm_steg_location:
            case "top-left" | "top-right":
                return self.check_margin(header)
            case "bottom-left" | "bottom-right":
                return self.check_margin(footer)

    # utility function for check_document_margins which defines the specific
    # thresholds necessary for checking of whether or not there is enough
    # white pixel space int he desired location for the dm steg
    def check_margin(self, pix_map):
        print("check_margin")
        dm_width = 72 - (2 * allowance)
        pix_width = pix_map.width
        pix_height = pix_map.height
        padded_dm = dm_width + (2 * allowance)
        match self.dm_steg_location:
            case "top-left":
                x_threshold = padded_dm
                y_threshold = padded_dm
            case "top-right":
                x_threshold = pix_width - padded_dm
                y_threshold = padded_dm
            case "bottom-left":
                x_threshold = padded_dm
                y_threshold = pix_height - padded_dm
            case "bottom-right":
                x_threshold = pix_width - padded_dm
                y_threshold = pix_height - padded_dm
        return self.check_designated_margin_area(pix_map, x_threshold, y_threshold)

    # utility function for check_document_margins which checks the defined pixel spaces
    # ,according to threshold (defined by margin_is_empty). This function ultimately
    # determines if the margin of the document qualifies for a dm steg to be placed on it
    def check_designated_margin_area(self, pix_map, x_threshold, y_threshold):
        print("check_designated_margin_area")
        coords = []
        pix_width = pix_map.width
        pix_height = pix_map.height
        for x in range(pix_width):
            for y in range(pix_height):
                pixel = pix_map.pixel(x, y)
                if pixel != (255, 255, 255):
                    match self.dm_steg_location:
                        case "top-left":
                            if x <= x_threshold and y <= y_threshold:
                                coords.append((x, y))
                        case "top-right":
                            if x >= x_threshold and y <= y_threshold:
                                coords.append((x, y))
                        case "bottom-left":
                            if x <= x_threshold and y >= y_threshold:
                                coords.append((x, y))
                        case "bottom-right":
                            if x >= x_threshold and y >= y_threshold:
                                coords.append((x, y))
        return True if len(coords) == 0 else False

    # indiscirminantly grabs all the images from the first page of the document
    def grab_all_first_page_images(self):
        print("grab_all_first_page_images")
        page = self.document[0]
        image_list = page.get_images()
        images = []
        for j, img in enumerate(image_list, start=1):
            xref = img[0]
            pix = fitz.Pixmap(self.document, xref)
            image_bytes = pix.tobytes()
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)
        return images

    # filters out the dms from the collected document images
    def grab_all_dms_from_images(self):
        print("grab_all_dms_from_images")
        if not self.images:
            return []
        return list(
            filter(lambda img: True if read_dm_pylibdmtx(
                img) else False, self.images)
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
                lambda img: True if read_steganography(
                    img) else False, self.dm_images
            )
        )

    # generate a dm, steganographize it and add it to the document at the specified location

    def generate_dm_and_add_to_pdf(self):
        print("generate_dm_and_add_to_pdf")
        steg_id = save_orig_doc_to_db(self.document)
        ord_dm = generate_dm(self.document)
        steg_dm = steganography(ord_dm, str(steg_id))
        modified_document = put_steg_dm_in_pdf(
            self.document, steg_dm, self.dm_steg_location
        )
        metadata = json.dumps(modified_document.metadata)
        new_pdf_data = bytes(modified_document.tobytes())
        save_modified_doc_to_db(metadata, new_pdf_data, steg_id)
        base_name = os.path.basename(self.document.name)
        new_name = f'{base_name[: base_name.find(".pdf")]}-signed.pdf'
        return (new_pdf_data, new_name)
