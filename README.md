# Master's Thesis Project: A Transformer-based Approach to the Book Success Prediction Problem

## Developers
Gianluca Guarro

## Implementation

These are the core experiments done in exploring the efficacy of a Book Success Predictor. The process can logically be split into three stages:

1. Data preprocessing / Model pretraining
    
    - Auto-book trimming using newline character frequency
    - Feeding books through a transformer model fine-tuned on the named-entity-recognition task to mask character names
    - Pretraining Bert using within-task and in-domain pretraining https://link.springer.com/chapter/10.1007/978-3-030-32381-3_16
    - Explored results using both sentence-tokenizer and overlap-tokenizer

2. Model training with transformer models directly

    - Average pooling of book chunk predictions (BERT, DistilBERT, ELECTRA, Roberta)

3. Using the transformer embeddings from stage 2 to train other models

    - Using averaged chunk embeddings per book, trained a shallow NN
    - Using averaged chunk embeddings per book, trained an SVM
    - Training an LSTM on the chunk embeddings. https://ieeexplore.ieee.org/abstract/document/9003958
    - Trained a Genre-Aware Attention Model using BERT embeddings with other hand-crafted text features. Expanded on the code in this repository: https://github.com/sjmaharjan/genre_aware_attention.