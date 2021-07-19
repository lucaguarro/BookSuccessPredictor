import sqlite3

import pathlib
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

db_log_path = pathlib.Path().absolute() / "Log" / "db.log"
file_handler = logging.FileHandler(db_log_path, 'w', 'utf-8')
# file_handler = logging.FileHandler(r'C:\Users\lguarro\Documents\Work\SearchEngine_Pure\Log\db.log', 'w', 'utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class SQLiteHelper():
    def __init__(self):
        self.conn = sqlite3.connect('../guarro_goodreads.db')
        self.dataCur = self.conn.cursor()
        self.modCur = self.conn.cursor()
        self.initializeCursor()
        logger.info('connected to db and initialized cursors')

    def __del__(self):
        # print("yikess")
        self.conn.close()

    def initializeCursor(self):
        self.dataCur.execute("""
            SELECT proj_gutenberg_id, author, title
            FROM books WHERE goodreads_rating is NULL and no_gr_found is NULL
        """)
        self.nextVal = self.dataCur.fetchone()

    def getNext(self):
        returnVal = self.nextVal
        self.nextVal = self.dataCur.fetchone()
        return returnVal

    def mark_no_gr_found(self, pg_id):
        try:
            sql = """
                UPDATE books
                SET no_gr_found = 1
                WHERE proj_gutenberg_id = ? 
            """
            self.modCur.execute(sql, (pg_id,))
            self.conn.commit()
            logger.info('Marked no_gr_found for book with id ' + str(pg_id))
        except Exception as e:
            print(e)
            logger.error('Marked no_gr_found failure for book with id ' + str(pg_id))

    def updateBook(self, task):
        sql = ""
        try:
            sql = """
                UPDATE books
                SET goodreads_rating = ? ,
                    num_ratings = ? ,
                    goodreads_blurb = ? ,
                    num_pages = ? ,
                    published_info = ? ,
                    title_gr = ? ,
                    author_gr = ?
                WHERE proj_gutenberg_id = ?
            """
            self.modCur.execute(sql, task)
            self.conn.commit()
            logger.info('Updated metadata for book with id ' + str(task[7]))
        except Exception as e:
            print(e)
            logger.error("Book update failure with these parameters GOODREADS_RATING: {}, NUM_RATINGS = {}, GOODREADS_BLURB = {}, NUM_PAGES = {}, PROJ_GUTENBERG_ID = {}".format(*task))

    def genre_multi_insert(self, pg_id, genres, votes):
        sql = ""
        try:
            sql = "INSERT INTO goodreads_genre(proj_gutenberg_id, genre, num_votes) VALUES "
            ay = "".join("({0},'{1}',{2}),".format(str(pg_id),x,str(y)) for x,y in zip(genres,votes))
            sql = sql + ay[:-1] + ';'
            self.modCur.execute(sql)
            self.conn.commit()
            logger.info('Inserted genres for book with id ' + str(pg_id))
        except Exception as e:
            print(type(e))
            logger.error('Genre Update FAILURE, Query was: ' + sql)
            logger.error(e)

    # def addGenres(self, task):
    #     sql = "INSERT INTO genres(proj_gutenberg_id, genre, num_votes) VALUES (?, ?, ?)"
    #     self.dataCur.execute(sql, task)


