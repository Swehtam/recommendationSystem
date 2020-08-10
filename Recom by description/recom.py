#!/usr/bin/env python3.5.7
# -*- coding: utf-8 -*- 

import pandas as pd 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel 
import nltk
# language = portuguese
from spacy.lang.pt.stop_words import STOP_WORDS

# Reading data
#data = pd.read_csv("sample.csv")
data = pd.read_csv('data_description.csv', sep=';')
data = data[data['DESCRIPTION'] != '[]']
data.reset_index(drop = True, inplace=True)

# --- IMPORTANT --- #
''' The rarer the term in DESCRIPTION, the higher de TF-IDF score is. Where TF is Term Frequency and IDF is Inverse Document Frequency. 
TF(term) = (n of term appareances) / (n of total terms)
IDF(term) = log_e(n of documents / n of docs with term)'''

# TF-IDF
#stopwords = nltk.corpus.stopwords.words(’portuguese’)
TF = TfidfVectorizer(analyzer='word', ngram_range=(1,3), min_df=0, stop_words=STOP_WORDS)
TFIDF_matrix = TF.fit_transform(data['DESCRIPTION'])
#print(TFIDF_matrix)

# Calculating cosine similarity
cos_similarity = linear_kernel(TFIDF_matrix, TFIDF_matrix)
results = {} 
for index,rows in data.iterrows():
    similar_indexes = cos_similarity[index].argsort()[:-100:-1]
    similar_items = [(cos_similarity[index][i], data['id'][i]) for i in similar_indexes]
    results[rows['id']] = similar_items[1:]

def item(id):
    return data.loc[data['id'] == id]['NOME_PRODUTO'].tolist()[0]
    #data.loc[data['id'] == id]['DESCRIPTION'].tolist()[0].split(' - ')[0]

# Recommendation Model
def model(item_id, max_recom):
    print("Recommending " + str(max_recom) + " products similar to " + item(item_id) + "...")
    print("#################")
    recoms = results[item_id][:max_recom]
    for rec in recoms:
        print("Recommended: " + item(rec[1]) + " with score = " + str(rec[0]))

model(1, 10)