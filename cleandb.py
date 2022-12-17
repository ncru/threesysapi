import os
import psycopg2

CLEAN_TB1 = "DELETE FROM threesyspdfs"
CLEAN_TB2 = "DELETE FROM origpdfs"


url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

with connection:
    with connection.cursor() as cursor:
        cursor.execute(CLEAN_TB1)
        cursor.execute(CLEAN_TB2)
        print("DB CLEAN")
