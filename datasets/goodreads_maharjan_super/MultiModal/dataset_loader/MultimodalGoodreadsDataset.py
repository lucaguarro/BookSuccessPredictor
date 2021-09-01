from torch.utils.data import Dataset, DataLoader
from readers.goodreads import GoodreadsReader
from readers.corpus import Corpus
from features.utils import fetch_features_vectorized
import numpy as np
import os

def label_extractor(book_data):
    return book_data.success

class MultimodalGoodreadsDataset():

    def one_hot(self, arr):
        unique, inverse = np.unique(arr, return_inverse=True)
        onehot = np.eye(unique.shape[0])[inverse]
        return onehot

    def get_genre_info(self, corpus):
        train_genres = self.one_hot([corpus.X_train[i].genre for i in range(len(corpus.X_train))])
        val_genres = self.one_hot([corpus.X_val[i].genre for i in range(len(corpus.X_val))])
        test_genres = self.one_hot([corpus.X_test[i].genre for i in range(len(corpus.X_test))])
        return train_genres, val_genres, test_genres

    def __init__(self, dataset_base_dir, cached_features_dir, features=["char_5_gram", "bert_features", ]):
        # G:\My Drive\Thesis\BookSuccessPredictor\datasets\goodreads_maharjan_super\raw_preprocessed\goodreads_maharjan_trimmed
        # r'G:\My Drive\Thesis\UsefulRelatedProjects\curr_sota\data\raw_text'
        reader = GoodreadsReader(dataset_base_dir)
        
        # r'G:\My Drive\Thesis\BookSuccessPredictor\datasets\goodreads_maharjan_super\raw_text\train_test_val_split_goodreads.yaml'
        print("Path to yaml:", os.path.join(dataset_base_dir, r'train_test_val_80_20_split_goodreads.yaml'))
        corpus = Corpus.from_splitfile(reader, os.path.join(dataset_base_dir, r'train_test_val_80_20_split_goodreads.yaml'), label_extractor)

        train_genres, val_genres, test_genres = self.get_genre_info(corpus)
        X_train, Y_train, X_val, Y_val, X_test, Y_test, f_lengths = fetch_features_vectorized(cached_features_dir, features, corpus)

        assert X_train.shape[0] == len(Y_train) == len(train_genres)
        assert X_val.shape[0] == len(Y_val) == len(val_genres)
        assert X_test.shape[0] == len(Y_test) == len(test_genres)

        self.train = MultimodalGoodreadsDatasetSplit(X_train, train_genres, Y_train)
        self.val = MultimodalGoodreadsDatasetSplit(X_val, val_genres, Y_val)
        self.test = MultimodalGoodreadsDatasetSplit(X_test, test_genres, Y_test)
        self.f_lengths = f_lengths


class MultimodalGoodreadsDatasetSplit(Dataset):

    def __init__(self, X, genres, Y):
        self.X = X
        self.genres = genres
        self.Y = Y

    def __len__(self):
        return len(self.Y)

    def __getitem__(self, idx):
        return {'text_features': self.X[idx], 'genre': self.genres[idx], 'label': self.Y[idx]}