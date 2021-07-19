# import sqlite3

# conn = sqlite3.connect('../guarro_goodreads.db')

# curr = conn.cursor()

# curr.execute("""
#             SELECT proj_gutenberg_id, author
#             FROM books
#             WHERE title = 'The King James Version of the Bible'
#         """)

# row = curr.fetchone()

# id = row[0]
# author = row[1]

# print(author == None)

# INSERT INTO 'tablename' ('column1', 'column2') VALUES
#     ('data1', 'data2'),
#     ('data1', 'data2'),
#     ('data1', 'data2'),
#     ('data1', 'data2');
# (proj_gutenberg_id, title, genre, num_votes)

# genres= ['a','b','c','d','e','f','g','h']
# num_votes = [1,2,3,4,5,6,7,8]
# pg_id = 50

# sql = "INSERT INTO books(proj_gutenberg_id, title, genre, num_votes) VALUES "
# ay = "".join("({0},'{1}',{2}),".format(pg_id,x,y) for x,y in zip(genres,num_votes))
# ay = sql + ay[:-1] + ';'
# print(ay)
# for i in range(len(num_votes)):
#     ','.join()

# task = (1,2,3,4,5)

# str = "Book update failure with these parameters GOODREADS_RATING: {}, NUM_RATINGS = {}, GOODREADS_BLURB = {}, NUM_PAGES = {}, PROJ_GUTENBERG_ID = {}".format(*task)
# print(str)

# import re

# ystr = '71 pages'
# ay = re.search(r'\d+', ystr).group(0)
# print(int(ay))

# author = 'Various'

# l_name = author.split(',')[0]

# print(l_name)

from SQLiteHelper import SQLiteHelper

sqlite_helper = SQLiteHelper()

genre_names = ['History', 'Nonfiction', 'Politics', 'Business', 'Amazon', 'Politics']
num_votes = [11,4,3,3,3,3]
pg_id = 3
(3,'History',11),(3,'Nonfiction',4),(3,'Politics',3),(3,'Business',3),(3,'Amazon',3),(3,'Politics',3);

sqlite_helper.genre_multi_insert(pg_id, genre_names, num_votes)

# rec = sqlite_helper.getNext()

# book_id = rec[0]
# author_lname = rec[1].split(',')[0]
# book_title = rec[2]
# print("1:", book_title)
# book_title = book_title.replace('\r\n', '\n').replace('\n', '\r').replace('\r', ' ')
# print('\n')
# print(book_title)
# task = (3.63,19,'',71,1)
# sqlite_helper.updateBook(task)