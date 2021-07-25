augment_db_w_path.py:
Uses the proj_gutenberg_id to find the path where the zip file containing the book is located. And stores the path to the zip file in the file_name column. I will mention that some books contain multiple zip files (I assume to account for different editions of the same book). In this case I just made the file_path point to the last one.

unzip.py:
Unzips the zip files being pointed at by the file_path column.
After executing this file I ran this SQL query
"""
update books
set file_path = SUBSTR(file_path, 1, LENGTH(file_path) - 4) || ".txt" where file_path is not null
"""
to actually point at the txt file which will be used for data processing.