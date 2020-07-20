#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
from Model import Model
import pandas as pd
import numpy as np

model = Model()

class Recommendation:

    def retrain_model(self):
        # variables to define field names:
        # CHANGE TO READ THE PROVIDED DATA
        db = pd.read_csv('data_armz.csv', sep = ';')
        user_id = 'COD_CLIENTE'
        item_id = 'COD_PRODUTO'
        item_name = 'NOME_PRODUTO'
        users_to_recommend = list(db[user_id])
        n_rec = 10 # itens to recommend

        print("abriu o treinamento")
        df_matrix_norm = model.matrix_normalization(db)
        data_norm = model.data_input_creation(df_matrix_norm)
        train_data, test_data = model.split_data(data_norm)
        recom = model.recom_model(train_data, user_id, item_id, users_to_recommend, n_rec)
        df_output = model.create_output(recom, user_id, item_id, users_to_recommend, n_rec, print_csv=True)
        return ("Recomendações atualizadas.")
