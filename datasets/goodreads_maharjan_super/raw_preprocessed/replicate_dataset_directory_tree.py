import os
# G:\My Drive\Thesis\Datasets\book_preprocessing\goodreads_maharjan_trimmed_and_nered\csv
inputpath = r'G:/My Drive/Thesis/Datasets/book_preprocessing/goodreads_maharjan_trimmed_and_nered/csv/'
outputpath = r'G:/My Drive/Thesis/Datasets/book_preprocessing/goodreads_maharjan_trimmed_and_nered/txt/'

for dirpath, dirnames, filenames in os.walk(inputpath):
    structure = os.path.join(outputpath, dirpath[len(inputpath):])
    if not os.path.isdir(structure):
        os.mkdir(structure)
    else:
        print("Folder does already exists!")