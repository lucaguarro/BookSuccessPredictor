proj_gutenberg_id:
Project gutenberg's book identification number. Also corresponds to how the book is stored in './All65kBooks'. For example book with id '4680' would be stored in './All65kBooks/4/6/8/4680'.

author:
True author of the book (provided by project gutenberg).

title:
True title of the book (provided by project gutenberg).

pg_num_downloads:
Number of downloads project gutenberg reports for the book (at time of download of the rdf files).

num_rdf_Returns:
ignore

goodreads_rating:
Rating of the book scraped from goodreads at time of scraping.

num_Ratings:
Number of goodreads rating the book had at time of scraping.

goodreads_blurb:
Short description of the book scraped from goodreads.

num_pages:
Number of pages the book has as scraped from goodreads.

published_info:
Uncleansed information of when the book was published in case it might be useful. (might be noisy due to republishings)

title_gr:
Title of the scraped book from goodreads. Used to compare with the title from project gutenberg.

author_gr:
Author of the scraped book from goodreads. Used to compare with the author from project gutenberg.

no_gr_found:
1 if the scraper did not find any book to scrape from goodreads. Null otherwise.

title_edit_dist:
Edit Distance between the project gutenberg title field and the goodreads title field.

was_successful:
1 if goodreads_rating >= 3.5, otherwise 0. (Null if not 'belongs_to_goodreads_guarro')

belongs_to_goodreads_guarro:
Books that provisionally belong to the new dataset. (Currently 4846 books).

file_path:
Relative path to where the book is stored simply for convenience purposes. (Only generated for books where 'belongs_to_goodreads_guarro' is 1.)

language:
Language of the book. *Note that all books in the /All65kBooks directory are only project gutenberg's english books but the rdf files contained the meta-information of all their books.