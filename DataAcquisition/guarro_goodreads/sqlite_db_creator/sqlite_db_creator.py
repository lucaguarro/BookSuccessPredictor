import sqlite3

# Connects to our database. If the database doesn't exist, it will create it.
conn = sqlite3.connect('guarro_goodreads.db') # guarro_goodreads is the name of the db.

# Create a cursor.
c = conn.cursor()

# Create a table
c.executescript("""
    CREATE TABLE books (
        proj_gutenberg_id INTEGER PRIMARY KEY,
        author TEXT,
        title TEXT,
        pg_num_downloads INTEGER,
        num_rdf_Returns INTEGER,
        goodreads_rating REAL,
        num_ratings INTEGER,
        goodreads_blurb TEXT,
        num_pages INTEGER
    );

    CREATE TABLE goodreads_genre (
        proj_gutenberg_id INTEGER,
        genre TEXT,
        FOREIGN KEY(proj_gutenberg_id) REFERENCES books(proj_gutenberg_id)
    );
""")


# Commit our command
conn.commit()

# Close our connection
conn.close()