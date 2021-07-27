from MultimodalGoodreadsDataset import MultimodalGoodreadsDataset

dataset_base_dir = r'G:\My Drive\Thesis\BookSuccessPredictor\datasets\goodreads_maharjan_super\raw_preprocessed\goodreads_maharjan_trimmed'
cached_features_dir = r'G:\My Drive\Thesis\BookSuccessPredictor\datasets\goodreads_maharjan_super\MultiModal\dataset_loader\cached_features'
a = MultimodalGoodreadsDataset(dataset_base_dir, cached_features_dir)