import datetime
import fitz
import io
from PIL import Image
import zxing
import treepoem
from pylibdmtx.pylibdmtx import decode as pylibdmtx_decode
from pyzbar.pyzbar import decode as pyzbar_decode

allowance = 3

# class definition that allows the api to define the five document traits of
# margin, images, dm images, dm stegs, and modified


class TSdoc:
    def __init__(self, document):
        self.document = document
        # self.margin = self.check_document_margins(self.document)
        # self.images = self.check_document_images(self.document) = None
        # self.dm_images = self.check_document_images_if_dm(self.images) = None
        # self.dm_steg = self.check_document_dms_if_steg(self.dm_images) = None
        # self.modified = self.check_db_if_already_exists(self.document)
