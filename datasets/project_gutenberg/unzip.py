import sqlite3
import os
from pathlib import Path
import zipfile

conn = sqlite3.connect('./guarro_goodreads.db')

dataCur = conn.cursor()

dataCur.execute("Select file_path from books where use_for_adaptive_ft = 2")

record = dataCur.fetchone()

counter = 0
while(record):
    # print(record)
    file_path = Path(record[0])
    file_dir = file_path.parents[0]

    # for loop acts as an if statement just to make sure that the txt file wasnt already unzipped
    for fname in os.listdir(file_dir):
        if fname.endswith('.txt'):
            break
    else:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(file_dir)

    record = dataCur.fetchone()
    counter += 1
    if (counter % 200 == 0):
        print(counter)

conn.close()