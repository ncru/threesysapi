import os
import psycopg2
from psycopg2.extras import RealDictCursor
import fitz

# author
# creationDate
# modDate

# QUERY = "SELECT * FROM origpdfs WHERE orig_id='1';"

# QUERY = "SELECT * FROM origpdfs WHERE orig_pdf_metadata -> 'author' = %s AND orig_pdf_metadata -> 'creationDate' = %s AND orig_pdf_metadata -> 'modDate' = %s"

QUERY = "SELECT orig_pdf_metadata -> 'author' AS author, orig_pdf_metadata -> 'creationDate' AS creationdate, orig_pdf_metadata -> 'modDate' AS moddate FROM origpdfs WHERE orig_pdf_metadata ->> 'author' = %s AND orig_pdf_metadata ->> 'creationDate' = %s AND orig_pdf_metadata ->> 'modDate' = %s"


# SELECT = "SELECT orig_pdf_metadata FROM origpdfs"


url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)
document = fitz.open('./clean docu.pdf')

metadata = document.metadata
author = metadata['author']
creation_date = metadata['creationDate']
mod_date = metadata['modDate']

with connection:
    with connection.cursor() as cursor:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(QUERY, (author, creation_date, mod_date))
        metadata_from_db = cursor.fetchone()
        db_author = metadata_from_db['author']
        db_creation_date = metadata_from_db['creationdate']
        db_mod_date = metadata_from_db['moddate']
        if author == db_author and creation_date == db_creation_date and mod_date == db_mod_date:
            print("DOCU BLAH BLAH")
