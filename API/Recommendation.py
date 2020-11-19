#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
from Model import Model
from SimilarityModel import SimilarityModel
import pandas as pd
import numpy as np

model = Model()
similarityModel = SimilarityModel()

class Recommendation:
    def create_user_classif_matrix(self, df_compras):
        db_copy = df_compras.copy()
        db_copy['DUMMY'] = 1

        df_matrix = pd.pivot_table(db_copy, values = 'DUMMY', index = 'COD_CLIENTE', columns = 'CLASSIFICACAO', fill_value=0)
        df_matrix = df_matrix.T

        return df_matrix

    def retrain_model(self):
        db = pd.read_csv('data_armz.csv', sep = ';')
        
        # - Retrain Add To Cart:
        print("Treinando add-to-cart")
        similarityModel.create_cosine_similarity_matrix(db)
        
        # - Retrain Purchased Based:
        # variables to define field names:
        # CHANGE TO READ THE PROVIDED DATA        
        user_id = 'COD_CLIENTE'
        item_id = 'COD_PRODUTO'
        item_name = 'NOME_PRODUTO'
        users_to_recommend = list(db[user_id])
        n_rec = 10 # itens to recommend

        print("Treinando purchased")
        df_matrix_norm = model.matrix_normalization(db)
        data_norm = model.data_input_creation(df_matrix_norm)
        train_data, test_data = model.split_data(data_norm)
        recom = model.recom_model(train_data, user_id, item_id, users_to_recommend, n_rec)
        df_output = model.create_output(recom, user_id, item_id, users_to_recommend, n_rec, print_csv=True)
        return ("Recomendações atualizadas.")
