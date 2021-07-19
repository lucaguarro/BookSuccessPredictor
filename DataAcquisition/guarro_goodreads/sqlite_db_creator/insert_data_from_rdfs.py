from rdflib import Graph, URIRef
from rdflib.namespace import RDFS, SKOS
import os
import pathlib

import sqlite3

def get_query_results(path):
    g = Graph()
    g.parse(str(path))
    qres = g.query(
        """ 
            prefix dcterms: <http://purl.org/dc/terms/> 
            prefix pgterms: <http://www.gutenberg.org/2009/pgterms/>
            select ?title ?num_downloads ?author_name
            where {{
                ?book a pgterms:ebook .
                ?book dcterms:title ?title .
                ?book pgterms:downloads ?num_downloads .
            } OPTIONAL {
                ?agent a pgterms:agent .
                ?agent pgterms:name ?author_name .
            }}
        """)
    for row in qres:
        title = row[0]
        num_downloads = row[1]
        author_name = row[2]
        return title, num_downloads, author_name, len(qres)

# Connects to our database. If the database doesn't exist, it will create it.
conn = sqlite3.connect('guarro_goodreads.db') # guarro_goodreads is the name of the db.

# Create a cursor.
c = conn.cursor()

rootdir = r'C:\Users\lucag\Documents\Thesis\datasets\project_gutenberg\rdf-files\epub'

done = False
count = 0
for subdir, dirs, files in os.walk(rootdir):
    # if(done):
    #     break
    for file in files:
        path = pathlib.PurePath(os.path.join(subdir, file))
        pg_book_id = path.parent.name
        title, num_downloads, author_name, num_returns = get_query_results(path)
        sql = "INSERT INTO books(proj_gutenberg_id, title, pg_num_downloads, author, num_rdf_returns) VALUES (?, ?, ?, ?, ?)"
        book = (pg_book_id, title, num_downloads, author_name, num_returns)
        c.execute(sql, book)
        conn.commit()
        # done = True
    count += 1
    if count % 100 == 0:
        print(count)

print('command executed successfully')
# Close our connection
conn.close()