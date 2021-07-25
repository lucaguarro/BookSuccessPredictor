import os
import yaml
import pandas as pd
from pathlib import Path
import shutil
import math
import re
import numpy as np

dataset_base = Path(r"C:\Users\lucag\Documents\Thesis\datasets\goodreads_maharjan")
data_yaml = dataset_base / "train_test_split_goodreads.yaml"

def get_next_book():
    with open(data_yaml) as file:
        documents = yaml.full_load(file)

        for train_test, doc in documents.items():
            for d in doc:
                for path in dataset_base.rglob(d):
                    with open(path, 'r', encoding = 'utf-8') as file:
                        yield file.read(), path

book_gen = get_next_book()

def find_newline_cutoff(book, percentage):
#     with open (book_path, "r") as myfile:
#         book = myfile.read()
    data = book[:math.floor(len(book)*percentage)]
    newline_positions = [match.start() for match in re.finditer("\n", data)]
    newline_position_diff = [newline_positions[n]-newline_positions[n-1] for n in range(1,len(newline_positions))]
    newline_position_diff = [float(i) for i in newline_position_diff]
    newline_position_diff -= np.average(newline_position_diff)
    cumsum = np.cumsum(newline_position_diff)
    min_index = np.argmin(cumsum)
    return newline_positions[min_index]

base_input_dir = Path(r'C:\Users\lucag\Documents\Thesis\datasets\goodreads_maharjan')
base_output_dir = Path(r'C:\Users\lucag\Documents\Thesis\datasets\book_preprocessing\goodreads_maharjan_preprocessed')
for book, path in book_gen:
    file_name = os.path.basename(path)
    save_to = os.path.join(base_output_dir, path.relative_to(base_input_dir))
    # print(str(path.relative_to(base_input_dir)))
    # print(ay)
    newline_cutoff = find_newline_cutoff(book, 0.10)
    preprocessed_book = book[newline_cutoff:]
    txt_file = open(save_to, "w", encoding="utf-8")
    txt_file.write(preprocessed_book)
    txt_file.close()
