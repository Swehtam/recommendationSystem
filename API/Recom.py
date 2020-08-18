#!/usr/bin/env python3.5.7
# -*- coding: utf-8 -*- 

import pandas as pd 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel 
import nltk
# language = portuguese
from spacy.lang.pt.stop_words import STOP_WORDS

class Recom:
    # Reading data
    #data = pd.read_csv("sample.csv")
    def open_file(self):
        data = pd.read_csv('data_description.csv', sep=';')
        data = data[data['DESCRIPTION'] != '[]']
        data.reset_index(drop = True, inplace=True)
        results = self.create_similar(data)
        return results, data


    def create_similar(self, data):
        TF = TfidfVectorizer(analyzer='word', ngram_range=(1,3), min_df=0, stop_words=STOP_WORDS)
        TFIDF_matrix = TF.fit_transform(data['DESCRIPTION'])
        # Calculating cosine similarity
        cos_similarity = linear_kernel(TFIDF_matrix, TFIDF_matrix)
        results = {} 
        for index,rows in data.iterrows():
            similar_indexes = cos_similarity[index].argsort()[:-100:-1]
            similar_items = [(cos_similarity[index][i], data['CODE'][i]) for i in similar_indexes]
            results[rows['CODE']] = similar_items[1:]
        return results

    def item(self, id, data):
        item = data.loc[data['CODE'] == id]['NOME_PRODUTO'].tolist()
        return item[0]

    # Recommendation Model
    def model(self, item_id, max_recom):
        results, data = self.open_file()        
        print("Recommending " + str(max_recom) + " products similar to " + self.item(item_id, data) + "...")
        print("#################")
        recoms = results[item_id][:max_recom]
        for rec in recoms:
            print("Recommended: " + self.item(rec[1], data) + " with score = " + str(rec[0]))
        return recoms


'''
# Pegar o output de recomendação para um cliente
    # Pegar os 10 primeiros produtos 
    # Listar 5 produtos semelhantes por descrição para cada um dos pro
'''
