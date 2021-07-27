from sklearn.pipeline import FeatureUnion
from features import create_feature
import os
import joblib
from scipy import sparse
import numpy as np


def re_order(order_lst, X, Y):
    X_reordered, Y_reordered = [], []

    def create_dic(X, Y):
        data = {}
        for x, y in zip(X, Y):
            data[x.book_id] = (x, y)
        return data

    mapping = create_dic(X,Y)

    for ele in order_lst:
        X_reordered.append(mapping.get(ele)[0])
        Y_reordered.append(mapping.get(ele)[1])
    return X_reordered, np.array(Y_reordered)

def fetch_features_vectorized(data_dir, features, corpus):
    # The ordering of all features will be based on these array of book_id's
    train_books = [corpus.X_train[i].book_id for i in range(len(corpus.X_train))]
    val_books = [corpus.X_val[i].book_id for i in range(len(corpus.X_val))]
    test_books = [corpus.X_test[i].book_id for i in range(len(corpus.X_test))]
    def extract_feature(feature, train_books, val_books, test_books):
        print("extracting feature:", feature)
        target_file = os.path.join(data_dir, feature, feature + '.pkl')
        target_index_file = os.path.join(data_dir, feature, feature + '_index.pkl')
        target_labels_file = os.path.join(data_dir, feature, feature + '_labels.pkl')
        target_model_file = os.path.join(data_dir, feature, feature + '_model.pkl')
        if os.path.exists(target_file):
            X_train, X_val, X_test = joblib.load(target_file)
            f_train_books, f_val_books, f_test_books = joblib.load(target_index_file)

            # Now these all should pass since we just re_ordered them to be the same
            for x, x1 in zip(f_train_books, train_books):
                if x != x1:
                    print("Book ids", x, x1)

                    raise AssertionError("Train book order differ")

            for x, x1 in zip(f_val_books, val_books):
                if x != x1:
                    print("Book ids", x, x1)

                    raise AssertionError("Val book order differ")

            for x, x1 in zip(f_test_books, test_books):
                if x != x1:
                    raise AssertionError("Test book order differ")

            #X_train, X_test=corpus.X_train, corpus.X_test
            Y_train, Y_val, Y_test = corpus.Y_train, corpus.Y_val, corpus.Y_test

        else:
            print(feature)
            feature_name, vectorizer = create_feature(feature) # , train_books, val_books, test_books

            X_train, Y_train, X_val, Y_val, X_test, Y_test = extract_features_and_labels_by_split(feature, vectorizer, corpus, {'train_books': train_books, 'val_books': val_books, 'test_books': test_books})

            joblib.dump((X_train, X_val, X_test), target_file)
            joblib.dump((Y_train, Y_val, Y_test), target_labels_file)
            joblib.dump(([book.book_id for book in corpus.X_train], [book.book_id for book in corpus.X_val], [book.book_id for book in corpus.X_test]),
                        target_index_file)
            joblib.dump(vectorizer, target_model_file)
            # Y_train, Y_val, Y_test = corpus.Y_train, corpus.Y_val, corpus.Y_test
        return X_train, Y_train, X_val, Y_val, X_test, Y_test

    if isinstance(features, list):
        results = [extract_feature(feature, train_books, val_books, test_books) for feature in features]
        # open the results
        X_trains, Y_trains, X_vals, Y_vals, X_tests, Y_tests = zip(*results)

        if any(sparse.issparse(f) for f in X_trains):
            X_trains = sparse.hstack(X_trains).tocsr()
            X_vals = sparse.hstack(X_vals).tocsr()
            X_tests = sparse.hstack(X_tests).tocsr()

        else:
            X_trains = np.hstack(X_trains)
            X_vals = np.hstack(X_vals)
            X_tests = np.hstack(X_tests)

        for i, y in enumerate(Y_trains):
            if i != 0:
                for j, k in zip(y, Y_trains[i - 1]):
                    if j != k:
                        print("j,k",j,k)
                        raise AssertionError("Y's differ")
                # assert np.allclose(np.array(y), np.array()), "Y's differ"

                for j, k in zip(Y_vals[i], Y_vals[i - 1]):
                    if j != k:
                        raise AssertionError("Y val's differ")

                for j, k in zip(Y_tests[i], Y_tests[i - 1]):
                    if j != k:
                        raise AssertionError("Y test's differ")
                        # assert np.allclose(np.array(Y_tests[i]), np.array(Y_tests[i - 1])), "Y test's differ"

        return X_trains, Y_trains[0], X_vals, Y_vals[0], X_tests, Y_tests[0]
    else:
        return extract_feature(features)


def extract_features_and_labels_by_split(feature, vectorizer, corpus, book_ids_order):

    if feature == 'bert_features':
        X_train, Y_train, X_val, Y_val, X_test, Y_test = vectorizer.get_features_and_labels(book_ids_order)
    else:
        X_train = vectorizer.fit_transform(corpus.X_train)
        X_val = vectorizer.transform(corpus.X_val)
        X_test = vectorizer.transform(corpus.X_test)

        Y_train, Y_val, Y_test = corpus.Y_train, corpus.Y_val, corpus.Y_test

    return X_train, Y_train, X_val, Y_val, X_test, Y_test

    # if(feature == "BertFeatures"):
    #     from datasets import DatasetDict, Dataset
    #     import pickle

    #     # r"G:\My Drive\Thesis\UsefulRelatedProjects\curr_sota\genre_aware_attention\code\cached_features\avg_pld_outs_hf_ds.pkl"
    #     with open("../cached_features/avg_pld_outs_hf_ds.pkl", "rb") as input_file:
    #         avg_pld_outs_hf_ds = pickle.load(input_file)

    #     X_train, X_val, X_test = avg_pld_outs_hf_ds['train']['meaned_pooled_output'], avg_pld_outs_hf_ds['validation']['meaned_pooled_output'], avg_pld_outs_hf_ds['test']['meaned_pooled_output']
    #     Y_train, Y_val, Y_test = avg_pld_outs_hf_ds['train']['success_label'], avg_pld_outs_hf_ds['validation']['success_label'], avg_pld_outs_hf_ds['test']['success_label']

    #     def get_permutations(ref_order, cur_order):
    #         ref_order_mapping = {}
    #         for i in range(len(ref_order)):
    #             ref_order_mapping[ref_order[i]] = i

    #         permutations = []
    #         for i in range(len(cur_order)):
    #             permutations.append(ref_order_mapping[cur_order[i]])
            
    #         return permutations

    #     def reorder_list(curlist, permutations):
    #         new_list = [0] * len(curlist)
    #         for i in range(len(curlist)):
    #             new_list[permutations[i]] = curlist[i]
    #         return new_list

    #     train_perms = get_permutations(train_books, avg_pld_outs_hf_ds['train']['book_title'])
    #     val_perms = get_permutations(val_books, avg_pld_outs_hf_ds['validation']['book_title'])
    #     test_perms = get_permutations(test_books, avg_pld_outs_hf_ds['test']['book_title'])

    #     X_train, Y_train = reorder_list(X_train, train_perms), reorder_list(Y_train, train_perms)
    #     X_val, Y_val = reorder_list(X_val, val_perms), reorder_list(Y_val, val_perms)
    #     X_test, Y_test = reorder_list(X_test, test_perms), reorder_list(Y_test, test_perms)

    #     joblib.dump((X_train, X_val, X_test), target_file)
    #     joblib.dump((Y_train, Y_val, Y_test), target_labels_file)
    #     joblib.dump((train_books, val_books, test_books), target_index_file)
    # else:




# def test_fetch_features_vectorizer(data_dir, features=['writing_density', 'readability']):
#     X_train, Y_train, _, _ = fetch_features_vectorized(data_dir, features, '')
#     X_train_w, Y_train_w, _, _ = fetch_features_vectorized(data_dir, 'writing_density', None)
#     X_train_r, Y_train_r, _, _ = fetch_features_vectorized(data_dir, 'readability', None)
#     assert np.allclose(Y_train, Y_train_r), 'Y does not match'
#     assert np.allclose(Y_train, Y_train_w), 'Y does not match'
#     assert np.allclose(np.hstack((X_train_w, X_train_r)), X_train), 'Xs does not match'

# def johns_features():
#     data = np.load('book_datav4_multitask_15_feats.npy')
#     data = data.tolist()

#     fnames, features, target = data['fnames'], data['features'], data['targets']
#     X_train_rnn = []
#     X_test_rnn = []
#     X_train, X_test = joblib.load('/home/sjmaharjan/Books/booksuccess/vectors/unigram_index.pkl')

#     for fname in X_train:
#         X_train_rnn.append(features[fnames.index(fname)].tolist())
#     for fname in X_test:
#         X_test_rnn.append(features[fnames.index(fname)].tolist())

#     joblib.dump((np.array([target[fnames.index(fname)] for fname in X_train]),
#                  np.array([target[fnames.index(fname)] for fname in X_test])), 'rnn_labels.pk')
