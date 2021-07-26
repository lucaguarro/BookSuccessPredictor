import os
import pickle

__all__ = ['BertFeatures']


class BertFeatures():
    def __init__(self):
        resource_dir = os.path.join(os.path.dirname(__file__), 'resources/bertFeatures')
        data_dir = os.path.join(resource_dir, 'avg_pld_outs_hf_ds.pkl')
        with open(data_dir, "rb") as input_file:
            self.avg_pld_outs_hf_ds = pickle.load(input_file)

    def get_features_and_labels(self, book_id_ordering):
        def get_permutations(ref_order, cur_order):
            ref_order_mapping = {}
            for i in range(len(ref_order)):
                ref_order_mapping[ref_order[i]] = i

            permutations = []
            for i in range(len(cur_order)):
                permutations.append(ref_order_mapping[cur_order[i]])
            
            return permutations

        def reorder_list(curlist, permutations):
            new_list = [0] * len(curlist)
            for i in range(len(curlist)):
                new_list[permutations[i]] = curlist[i]
            return new_list

        X_train, X_val, X_test = self.avg_pld_outs_hf_ds['train']['meaned_pooled_output'], self.avg_pld_outs_hf_ds['validation']['meaned_pooled_output'], self.avg_pld_outs_hf_ds['test']['meaned_pooled_output']
        Y_train, Y_val, Y_test = self.avg_pld_outs_hf_ds['train']['success_label'], self.avg_pld_outs_hf_ds['validation']['success_label'], self.avg_pld_outs_hf_ds['test']['success_label']

        train_perms = get_permutations(book_id_ordering['train_books'], self.avg_pld_outs_hf_ds['train']['book_title'])
        val_perms = get_permutations(book_id_ordering['val_books'], self.avg_pld_outs_hf_ds['validation']['book_title'])
        test_perms = get_permutations(book_id_ordering['test_books'], self.avg_pld_outs_hf_ds['test']['book_title'])

        X_train, Y_train = reorder_list(X_train, train_perms), reorder_list(Y_train, train_perms)
        X_val, Y_val = reorder_list(X_val, val_perms), reorder_list(Y_val, val_perms)
        X_test, Y_test = reorder_list(X_test, test_perms), reorder_list(Y_test, test_perms)

        return X_train, Y_train, X_val, Y_val, X_test, Y_test