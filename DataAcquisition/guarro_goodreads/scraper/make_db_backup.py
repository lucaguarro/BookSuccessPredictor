import sqlite3

def progress(status, remaining, total):
    print(f'Copied {total-remaining} of {total} pages...')

con = sqlite3.connect('guarro_goodreads.db')
bck = sqlite3.connect('pre_goodreads_scraping.db')
with bck:
    con.backup(bck, pages=1, progress=progress)
bck.close()
con.close()