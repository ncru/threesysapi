import hashlib
import unittest
import fitz
from modules.TSdoc import TSdoc

#   Stores the three document inputs for use in testing.
class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):  # runs at the start before all tests, once.
        # variable assignments for use
        cls.mode1 = "generate"
        cls.mode2 = "verify"

        # region Clean document
        cls.doc = fitz.open(
            "testing/Clean_tester.pdf"
        )  # using clean wImg doc as a tester
        cls.doc_name = cls.doc.name
        cls.doc_dmloc = "top-left"
        cls.doc_bytes = cls.doc.tobytes(garbage=4, no_new_id=True)
        cls.doc_hash = hashlib.sha256(cls.doc_bytes).hexdigest()
        cls.doc_dict = {
            "margins": True,
            "images": False,
            "dm_images": False,
            "dm_steg": False,
            "modified": False,
        }  # expected dict values to compare, based on file
        # endregion

        # region Clean wImg document2
        cls.doc2 = fitz.open(
            "testing/Clean_wImg_tester.pdf"
        )  # using clean wImg doc as a tester
        cls.doc2_name = cls.doc2.name
        cls.doc2_dmloc = ""
        cls.doc2_bytes = cls.doc2.tobytes(garbage=4, no_new_id=True)
        cls.doc2_hash = hashlib.sha256(cls.doc2_bytes).hexdigest()

        cls.doc2_dict = {
            "margins": True,
            "images": True,
            "dm_images": False,
            "dm_steg": False,
            "modified": False,
        }  # expected dict values to compare, based on file
        # endregion

        # region Dirty wDMSteg document3
        cls.doc3 = fitz.open(
            "testing/Dirty_wDMSteg_tester.pdf"
        )  # using clean wImg doc as a tester
        cls.doc3_name = cls.doc3.name
        cls.doc3_dmloc = ""
        cls.doc3_bytes = cls.doc3.tobytes(garbage=4, no_new_id=True)
        cls.doc3_hash = hashlib.sha256(cls.doc3_bytes).hexdigest()

        cls.doc3_dict = {
            "margins": False,
            "images": True,
            "dm_images": True,
            "dm_steg": True,
            "modified": True,
        }  # expected dict values to compare, based on file
        # endregion

        cls.document = TSdoc(cls.mode1, cls.doc_name, cls.doc, cls.doc_dmloc)
        cls.document2 = TSdoc(cls.mode2, cls.doc2_name, cls.doc2, cls.doc2_dmloc)
        cls.document3 = TSdoc(cls.mode1, cls.doc3_name, cls.doc3, cls.doc3_dmloc)
        print("=====START OF TEST=====")

        if cls is not BaseTestCase and cls.setUp is not BaseTestCase.setUp:
            orig_setUp = cls.setUp

            def setUpOverride(self, *args, **kwargs):
                BaseTestCase.setUp(self)
                return orig_setUp(self, *args, **kwargs)

            cls.setUp = setUpOverride

    @classmethod
    def tearDownClass(cls):  # runs at the end before all tests, once.
        print("=====END OF TEST=====")


# @unittest.skip("bypassed for now")
# Checks if __init__ reads the fitz object, along with the
# outputs of the class methods (which fills in the __init__ variables)
class Test_TSdoc_A_init(BaseTestCase):
    # @classmethod
    # def setUpClass(cls):  # runs at the start before all tests, once.
    #     pass

    # def setUp(self):
    #     print("test start")

    # def tearDown(self):
    #     print("test end")

    def test_A_mode(self):
        print("TSdoc - mode returns string")
        assert (
            type(self.document.mode)
            and type(self.document2.mode)
            and type(self.document3.mode) is str
        )
        print("TSdoc - mode accepts either generate or verify")
        assert self.document.mode, self.document3.mode == "generate"
        assert self.document2.mode == "verify"

    def test_B_document_name(self):
        assert (
            type(self.document.document_name)
            and type(self.document2.document_name)
            and type(self.document3.document_name) is str
        )
        assert self.document.document_name == self.doc_name
        assert self.document2.document_name == self.doc2_name
        assert self.document3.document_name == self.doc3_name

    def test_C_dm_steg_loc(self):
        assert (
            type(self.document.dm_steg_location)
            and type(self.document2.dm_steg_location)
            and type(self.document3.dm_steg_location) is str
        )
        assert self.document.dm_steg_location == "top-left"  # given position argument
        assert (
            self.document2.dm_steg_location
            and self.document3.dm_steg_location == "bottom-right"
        )  # given none

    def test_D_document(self):
        assert (
            type(self.document.document)
            and type(self.document2.document)
            and type(self.document3.document) is fitz.fitz.Document
        )
        assert self.document.document == self.doc
        assert self.document2.document == self.doc2
        assert self.document3.document == self.doc3

    def test_E_bytehash(self):
        assert type(self.document.bytes), type(self.document.hash) is str
        assert type(self.document2.bytes), type(self.document2.hash) is str
        assert type(self.document3.bytes), type(self.document3.hash) is str
        assert self.document.bytes == self.doc_bytes
        assert self.document2.bytes == self.doc2_bytes
        assert self.document3.bytes == self.doc3_bytes
        assert self.document.hash == self.doc_hash
        assert self.document2.hash == self.doc2_hash
        assert self.document3.hash == self.doc3_hash

    def test_F_signed(self):
        assert (
            type(self.document.already_signed)
            and type(self.document2.already_signed)
            and type(self.document3.already_signed) is bool
        )
        assert self.document.already_signed == True
        assert self.document2.already_signed == False
        assert self.document3.already_signed == False

    def test_G_images(self):
        assert (
            type(self.document.images)
            and type(self.document2.images)
            and type(self.document3.images) is list
        )
        assert (
            self.document.images == []
        )  # document 1 contains no images, should return none
        assert (
            str(type(self.document2.images[0]))
            == "<class 'PIL.PngImagePlugin.PngImageFile'>"
        )
        assert (
            str(type(self.document3.images[0]))
            == "<class 'PIL.PngImagePlugin.PngImageFile'>"
        )

    def test_H_dmimages(self):
        assert (
            type(self.document.dm_images)
            and type(self.document.dm_images)
            and type(self.document3.dm_images) is list
        )
        assert self.document.dm_images == []
        assert self.document2.dm_images == []
        self.assertTrue(self.document3.dm_images)  # checks if the list is not empty

    def test_I_dmstegs(self):
        assert (
            type(self.document.dm_stegs)
            and type(self.document2.dm_stegs)
            and type(self.document3.dm_stegs) is list
        )
        assert self.document.dm_stegs == []
        assert self.document2.dm_stegs == []
        self.assertTrue(self.document3.dm_stegs)  # checks if the list is not empty

    def test_J_traits(self):
        assert (
            type(self.document.traits)
            and type(self.document2.traits)
            and type(self.document3.traits) is dict
        )
        # check if list output corresponds to manually identified list
        assert self.document.traits == self.doc_dict
        assert self.document2.traits == self.doc2_dict
        assert self.document3.traits == self.doc3_dict


@unittest.skip("bypassed for now")
class Test_TSdoc_B_check_set_dmloc(BaseTestCase):

    # def setUp(self):
    #     print("test start")

    # def tearDown(self):
    #     print("test end")

    def test_A_checksetdm_returntype(self):
        assert (
            type(self.document.check_set_dm_steg_location(self.doc_dmloc))
            and type(self.document2.check_set_dm_steg_location(self.doc2_dmloc))
            and type(self.document3.check_set_dm_steg_location(self.doc3_dmloc)) is str
        )

    def test_B_checksetdm_location(
        self,
    ):  # Only tests 1 document object since all 3 are same objects.
        # what differs here is the 'location' that is being fed to the method/function
        assert (
            self.document.check_set_dm_steg_location(None) == "bottom-right"
        )  #   no input should return bottom-right as default

        assert (
            self.document.check_set_dm_steg_location("guatemala") == "bottom-right"
        )  #   wrong input should return bottom-right as default

        assert (
            self.document.check_set_dm_steg_location("top-left") == "top-left"
        )  # right input should return bottom-right as default


@unittest.skip("bypassed for now")
class Test_TSdoc_C_document_margins_passed(BaseTestCase):

    # def setUp(self):
    #     print("test start")

    # def tearDown(self):
    #     print("test end")

    def test_A_documentmarginpass_returntype(self):
        # function only returns if the corner is unicolor
        # match-case works based on dm steg location attribute from document object
        # .is_unicolor is a PyMuPDF function variable, which should return a boolean
        assert (
            type(self.document.document_margins_passed())
            and type(self.document2.document_margins_passed())
            and type(self.document3.document_margins_passed()) is bool
        )

    def test_B_if_area_is_unicolor(self):
        assert self.document.document_margins_passed() == True
        assert (
            self.document3.document_margins_passed() == False
        )  # this is the dirty document


@unittest.skip("bypassed for now")
class Test_TSdoc_D_grab_all_first_page_images(BaseTestCase):
    # check for images list
    def test_A_grabfirstpageimg_returntype(self):
        assert (
            type(self.document.grab_all_first_page_images())
            and type(self.document2.grab_all_first_page_images())
            and type(self.document3.grab_all_first_page_images()) is list
        )

    def test_B_first_page_img_list(self):
        assert self.document.grab_all_first_page_images() == []
        self.assertTrue(self.document2.grab_all_first_page_images())
        self.assertTrue(self.document3.grab_all_first_page_images())


@unittest.skip("bypassed for now")
class Test_TSdoc_E_grab_all_dms_from_images(BaseTestCase):
    def test_A_grabdmsfromimg_returntype(self):
        assert (
            type(self.document.grab_all_dms_from_images())
            and type(self.document2.grab_all_dms_from_images())
            and type(self.document3.grab_all_dms_from_images()) is list
        )

    def test_B_dms_images(self):
        assert self.document.grab_all_dms_from_images() == []
        self.assertTrue(self.document2.grab_all_dms_from_images())
        self.assertTrue(self.document3.grab_all_dms_from_images())


@unittest.skip("bypassed for now")
class Test_TSdoc_F_grab_all_dms_from_images(BaseTestCase):
    def test_A_grabdmstedfromimg_returntype(self):
        assert (
            type(self.document.grab_all_dm_steg_from_dms())
            and type(self.document2.grab_all_dm_steg_from_dms())
            and type(self.document3.grab_all_dm_steg_from_dms()) is list
        )

    def test_B_dm_steg_images(self):
        assert self.document.grab_all_dm_steg_from_dms() == []
        self.assertTrue(self.document2.grab_all_dm_steg_from_dms())
        self.assertTrue(self.document3.grab_all_dm_steg_from_dms())


# class Test_TSdoc_G_generate_dm_and_add_to_pdf(BaseTestCase):
#     def test_A_saveorigdoctodb(self):
#         print(self.document.generate_dm_and_add_to_pdf.)


if __name__ == "__main__":
    unittest.main(argv=[""], verbosity=2, exit=False)
