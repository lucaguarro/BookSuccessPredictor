import os

dir_name = r"C:\Users\lucag\Documents\Thesis\datasets\book_preprocessing\goodreads_maharjan_preprocessed"
test = os.listdir(dir_name)

for item in test:
    if item.endswith(".txt"):
        os.remove(os.path.join(dir_name, item))