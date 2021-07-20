import matplotlib

class ModelScorer:
  def __init__(self, trainer, segmented_dataset, for_multitask = False):
    # self.segmented_dataset = segmented_dataset
    print("Getting predictions on validation set")
    val_dataset = segmented_dataset['validation']
    self.devset_predictions = trainer.predict(segmented_dataset['validation']).predictions
    self.val_book_changes_idx = self.get_book_changes_idx(val_dataset['book_title'])
    self.y_val_true = val_dataset['labels']

    print("Getting predictions on test set")
    test_dataset = segmented_dataset['test']
    self.testset_predictions = trainer.predict(segmented_dataset['test']).predictions
    self.test_book_changes_idx = self.get_book_changes_idx(test_dataset['book_title'])
    self.y_test_true = test_dataset['labels']

    if for_multitask:
      self.devset_predictions = self.devset_predictions[:,0:2]
      self.y_val_true = [item[0] for item in self.y_val_true]
      self.testset_predictions = self.testset_predictions[:,0:2]
      self.y_test_true = [item[0] for item in self.y_test_true]

#   def __init__(self, devset_predictions, testset_predictions, segmented_dataset, for_multitask = False):
#     self.devset_predictions = devset_predictions
#     self.testset_predictions = testset_predictions
    
#     val_dataset = segmented_dataset['validation']
#     self.val_book_changes_idx = self.get_book_changes_idx(val_dataset['book_title'])
#     self.y_val_true = val_dataset['labels']
#     # self.y_val_true = list( val_dataset['labels'][i] for i in book_changes_idx )

#     test_dataset = segmented_dataset['test']
#     self.test_book_changes_idx = self.get_book_changes_idx(test_dataset['book_title'])
#     self.y_test_true = test_dataset['labels']
#     # self.y_test_true = list( test_dataset['labels'][i] for i in self.test_book_changes_idx )

#     if for_multitask:
#       self.devset_predictions = self.devset_predictions[:,0:2]
#       self.y_val_true = [item[0] for item in self.y_val_true]
#       self.testset_predictions = self.testset_predictions[:,0:2]
#       self.y_test_true = [item[0] for item in self.y_test_true]

  def get_book_changes_idx(self, book_titles):
    book_changes_idx = np.where(np.array(book_titles[:-1]) != np.array(book_titles[1:]))[0]
    book_changes_idx += 1
    book_changes_idx = np.insert(book_changes_idx, 0, 0)
    return book_changes_idx

  def get_segmented_f1_scores(self, for_val = True):
    print("*******************************************************************")
    print("********************** SEGMENTED F1 SCORE *************************")
    print("*******************************************************************")
    # if for_val:
    y_score = softmax(self.devset_predictions, axis = 1)[:, 1].tolist()
    f1_scores_and_thresholds = self.get_f1_for_validation(y_score)
    self.plot_f1_scores(f1_scores_and_thresholds)
    plt.pause(0.1)
    
    best_thres = f1_scores_and_thresholds['thresholds'][f1_scores_and_thresholds['max_f1_index']]
    test_f1 = self.output_f1_for_test(best_thres, for_whole_book = False)
    print("*****SCORE ON TEST SET*****")
    print("The weighted f1 score is {} using the validated threshold of {} \n".format(test_f1, best_thres))

  def get_f1_for_validation(self, y_score, l_th = 0.4, u_th = 0.8, for_whole_book = False):
    y_true = self.y_val_true
    if for_whole_book:
      y_true = list( self.y_val_true[i] for i in self.val_book_changes_idx )

    thresholds = np.arange(l_th, u_th, 0.01)
    f1_scores = []
    for th in thresholds:
      y_pred = [math.floor(input) if input < th else math.ceil(input) for input in y_score]
      f1_res = f1_score(y_true, y_pred, average = 'weighted')
      f1_scores.append(f1_res)
    max_f1 = max(f1_scores)
    max_f1_index = f1_scores.index(max_f1)
    self.validated_threshold = thresholds[max_f1_index]
    f1_scores_and_thresholds = {'thresholds': thresholds, 'f1_scores': f1_scores, 'max_f1_index': max_f1_index}
    return f1_scores_and_thresholds

  def get_book_f1_scores(self):
    print("*******************************************************************")
    print("************************ BOOK F1 SCORE ****************************")
    print("*******************************************************************")
    # DEV
    avg_book_scores = self.get_average_book_scores(self.devset_predictions, self.val_book_changes_idx)
    probabilities_per_book = softmax(avg_book_scores, axis = 1)
    y_score = probabilities_per_book[:,1].tolist()

    f1_scores_and_thresholds = self.get_f1_for_validation(y_score, 0.40, 0.80, for_whole_book = True)
    best_thres = f1_scores_and_thresholds['thresholds'][f1_scores_and_thresholds['max_f1_index']]

    self.plot_f1_scores(f1_scores_and_thresholds)
    plt.pause(0.1)

    # TEST
    middle_f1 = self.output_f1_for_test(0.5, for_whole_book = True)
    validated_thres_f1 = self.output_f1_for_test(best_thres, for_whole_book = True)
    print("*****SCORE ON TEST SET*****")
    print("The weighted f1 score is {} using a threshold of {} \n".format(middle_f1, 0.5))
    print("The weighted f1 score is {} using the validated threshold of {} \n".format(validated_thres_f1, best_thres))

  def output_f1_for_test(self, th, for_whole_book = False):
    y_true = None
    y_score = None
    if for_whole_book:
      y_true = list( self.y_test_true[i] for i in self.test_book_changes_idx )
      avg_book_scores = self.get_average_book_scores(self.testset_predictions, self.test_book_changes_idx)
      y_score = softmax(avg_book_scores, axis = 1)[:,1].tolist()
    else:
      y_true = self.y_test_true
      y_score = softmax(self.testset_predictions, axis = 1)[:, 1].tolist()
    y_pred = [math.floor(input) if input < th else math.ceil(input) for input in y_score]
    return f1_score(y_true, y_pred, average = 'weighted')

  def get_average_book_scores(self, predictions, book_changes_idx):
    total_book_scores = np.add.reduceat(predictions, book_changes_idx)
    interval_lengths = np.diff(np.r_[book_changes_idx, predictions.shape[0]])
    interval_lengths = interval_lengths.reshape(len(interval_lengths), 1)
    return total_book_scores / interval_lengths

  def plot_f1_scores(self, f1_scores_and_thresholds):
    matplotlib.pyplot.plot(f1_scores_and_thresholds['thresholds'], f1_scores_and_thresholds['f1_scores'])
    max_f1_index = f1_scores_and_thresholds['max_f1_index']
    print("*****SCORE ON VALIDATION SET*****")
    print("The max weighted f1 score is {} with a threshold of {} \n".format(f1_scores_and_thresholds['f1_scores'][max_f1_index], f1_scores_and_thresholds['thresholds'][max_f1_index]))

  def get_counts_of_classes(self, model_predictions):
    successful_prob = softmax(model_predictions.predictions, axis=1)[:,1]
    successful = np.around(successful_prob)
    (unique, counts) = np.unique(successful, return_counts=True)
    return counts

  # def get_cumulative_probs_per_book(self, ref_df, chunk_predictions):
  #   book_changes_idx = get_indices_of_books(ref_df)
  #   avg_book_scores = self.get_average_book_scores(chunk_predictions, book_changes_idx)
  #   probabilities_per_book = softmax(avg_book_scores, axis = 1)
  #   y_score = probabilities_per_book[:,1].tolist()
  #   return y_score

def compute_metrics_single(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def compute_metrics_multi(pred):
    preds = pred.predictions
    label_ids = pred.label_ids

    success_labels = label_ids[:, 0]
    genre_labels = label_ids[:, 1]

    success_preds = preds[:, 0:2].argmax(1)
    genre_preds = preds[:, 2:6].argmax(1)

    s_precision, s_recall, s_f1, _ = precision_recall_fscore_support(success_labels, success_preds, average='weighted')
    s_acc = accuracy_score(success_labels, success_preds)

    g_precision, g_recall, g_f1, _ = precision_recall_fscore_support(genre_labels, genre_preds, average='weighted')
    g_acc = accuracy_score(success_labels, success_preds)

    return {
        's_accuracy': s_acc,
        's_f1': s_f1,
        's_precision': s_precision,
        's_recall': s_recall,
        'g_accuracy': g_acc,
        'g_f1': g_f1,
        'g_precision': g_precision,
        'g_recall': g_recall
    }