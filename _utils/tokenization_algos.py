# -*- coding: utf-8 -*-
import re
alphabets= "([A-Za-z])"
digits = "([0-9])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
prefixes = "(Mr|St|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|Mt)[.]" 
websites = "[.](com|net|org|io|gov|me|edu)"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

import sys
def tokenize_book_and_make_labels(book, cut_off, success, tokenizer, chunk_limit = sys.maxsize, use_spacy = False):
  dictOfTokenizedChunks = split_book_into_nice_chunks(book, cut_off, tokenizer, chunk_limit, use_spacy)
  labels = [int(success)] * len(dictOfTokenizedChunks['input_ids'])
  return dictOfTokenizedChunks, labels

def seal_off_chunk(dictOfTokenizedChunks, currListOfInputIDs, cut_off):
  currListOfInputIDs.extend([102])
  attend_up_to = len(currListOfInputIDs)
  currListOfInputIDs.extend([0] * (cut_off - attend_up_to))
  
  dictOfTokenizedChunks['input_ids'].append(currListOfInputIDs)
  dictOfTokenizedChunks['token_type_ids'].append([0] * cut_off)
  dictOfTokenizedChunks['attention_mask'].append([1] * attend_up_to + [0] * (cut_off - attend_up_to))

# by default, we do not set a limit on the number of chunks.
def tokenize_complete_sentences(example, tokenizer, cut_off = 512, chunk_limit = sys.maxsize):
  if goodreads_guarro:
    dictOfTokenizedChunks = {'input_ids': [], 'token_type_ids': [], 'attention_mask': []}
  else:
    dictOfTokenizedChunks = {'input_ids': [], 'token_type_ids': [], 'attention_mask': [], 'success_label': None, 'genre': None, 'book_title': None}
    
  currListOfInputIDs = [101]
  split_book = split_into_sentences(example['text'])
  num_chunks = 0;
  needs_final_seal = False
  for sent in split_book:
    next_tokenized_sent = tokenizer(sent, add_special_tokens = False)['input_ids']
    if (len(currListOfInputIDs) + len(next_tokenized_sent) < cut_off - 1):
      currListOfInputIDs.extend(next_tokenized_sent)
      needs_final_seal = True
    else:
      seal_off_chunk(dictOfTokenizedChunks, currListOfInputIDs, cut_off)
      num_chunks += 1
      if num_chunks == chunk_limit:
        return dictOfTokenizedChunks
      currListOfInputIDs = [101]  
      needs_final_seal = False
  if (needs_final_seal):
    seal_off_chunk(dictOfTokenizedChunks, currListOfInputIDs, cut_off)

  if not goodreads_guarro:
    dictOfTokenizedChunks['success_label'] = [example['success_label']] * len(dictOfTokenizedChunks['input_ids'])
    dictOfTokenizedChunks['genre'] = [example['genre']] * len(dictOfTokenizedChunks['input_ids'])
    dictOfTokenizedChunks['book_title'] = [example['book_title']] * len(dictOfTokenizedChunks['input_ids'])
    # print(len(dictOfTokenizedChunks['input_ids']))
  return dictOfTokenizedChunks

def tokenize_w_overlap(example, tokenizer):
  data_tokenize = tokenizer(example['text'], 
                  max_length = 512,
                  stride=50,
                  add_special_tokens=True,
                  return_attention_mask=True,
                  return_token_type_ids=True,
                  return_overflowing_tokens = True)
  num_chunks = len(data_tokenize['input_ids'])
  return {
      'input_ids': data_tokenize['input_ids'][:num_chunks-1], 
      'token_type_ids': data_tokenize['token_type_ids'][:num_chunks-1], 
      'attention_mask': data_tokenize['attention_mask'][:num_chunks-1], 
      'success_label': [example['success_label']] * (num_chunks-1), 
      'genre': [example['genre']] * (num_chunks-1), 
      'book_title': [example['book_title']] * (num_chunks-1)
  }

# When batched = True, we take in multiple examples
def chunk_and_encode_examples_w_complete_sentences(examples, tokenizer):
  mega_dict = None
  if goodreads_guarro:
    mega_dict = {'attention_mask': [], 'input_ids': [], 'token_type_ids': []}
  else:
    mega_dict = {'attention_mask': [], 'genre': [], 'input_ids': [], 'success_label': [], 'token_type_ids': [], 'book_title': []}
  for i in range(len(examples['text'])):
    book_sample = None
    if goodreads_guarro:
      book_sample = {'text': examples['text'][i]}
    else:
      book_sample = {'text': examples['text'][i], 'genre': examples['genre'][i], 'success_label': examples['success_label'][i], 'book_title':examples['book_title'][i]}
    dictOfTokenizedChunks = tokenize_complete_sentences(book_sample, tokenizer)
    for key, value in dictOfTokenizedChunks.items():
      mega_dict[key].extend(value)
  return mega_dict

# When batched = True, we take in multiple examples
def chunk_and_encode_examples_w_overlap(examples, tokenizer):
  mega_dict = {'attention_mask': [], 'genre': [], 'input_ids': [], 'success_label': [], 'token_type_ids': [], 'book_title': []}
  for i in range(len(examples['text'])):
    book_sample = {'text': examples['text'][i], 'genre': examples['genre'][i], 'success_label': examples['success_label'][i], 'book_title':examples['book_title'][i]}
    dictOfTokenizedChunks = tokenize_w_overlap(book_sample, tokenizer)
    for key, value in dictOfTokenizedChunks.items():
      mega_dict[key].extend(value)
  return mega_dict