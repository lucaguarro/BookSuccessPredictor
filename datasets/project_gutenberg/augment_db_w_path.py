import sqlite3
import os
from pathlib import Path

conn = sqlite3.connect('./guarro_goodreads.db')

dataCur = conn.cursor()
modCur = conn.cursor()

def updateBook(task):
    sql = ""
    try:
        sql = """
            UPDATE books
            SET file_path = ?
            WHERE proj_gutenberg_id = ?
        """
        modCur.execute(sql, task)
        conn.commit()
    except Exception as e:
        print(e)


dataCur.execute("Select proj_gutenberg_id from books where use_for_adaptive_ft = 2")

record = dataCur.fetchone()

root_dir = Path('./All65kBooks')
counter = 0
while record:
    pg_id = record[0]
    split_digits = [int(i) for i in str(pg_id)]
    num_digits = len(split_digits)
    bookpath = root_dir
    exists = None
    if num_digits == 1:
        bookpath = bookpath / '0' / str(split_digits[0])
        exists = os.path.isdir(bookpath)
        for fname in os.listdir(bookpath):
            if fname.endswith('.zip'):
                bookpath = bookpath / fname
    else:
        for i in range(num_digits):
            if i == num_digits - 1:
                bookpath = bookpath / str(pg_id)
            else:
                bookpath = bookpath / str(split_digits[i])
        exists = os.path.isdir(bookpath)
        if exists:
            for fname in os.listdir(bookpath):
                if fname.endswith('.zip'):
                    bookpath = bookpath / fname
                    break
    if (exists):
        bookpath = str(bookpath)
    else:
        bookpath = "BOOK_NOT_FOUND"
    task = (bookpath, pg_id)
    updateBook(task)
    # print('Split Digits: {}\nBookpath: {} \n'.format(split_digits, bookpath))

    record = dataCur.fetchone()
    counter += 1
    if counter % 200 == 0:
        print(counter)

conn.close()