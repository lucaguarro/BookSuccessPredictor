import re

book_path = r'C:\Users\lucag\Documents\Thesis\datasets\goodreads_maharjan\Love_stories\success'

with open (book_path + '\\24985_comedies+of+courtship.txt', "r") as myfile:
    data=myfile.read()

print(len(data))
newline_positions = [match.start() for match in re.finditer("\n", data)]

print(newline_positions)