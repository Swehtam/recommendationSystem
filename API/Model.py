#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-

import pandas as pd
import turicreate as tc
import numpy as np

class Model:
    
    # Returns train and test datasets as scalable dataframes
    def split_data(self,data):
        data_sframe = tc.SFrame(data)
        return data_sframe

    def recom_model(self,train_data, user_id, item_id, users_to_recommend, n_rec):
        model = tc.item_similarity_recommender.create(tc.SFrame(train_data),
                                                       user_id = user_id,
                                                       item_id = item_id,
                                                       target = 'FREQ_COMPRAS',
                                                       similarity_type='cosine')
        recom = model.recommend(users=users_to_recommend, k=n_rec)
        return recom

    def create_output(self,model,user_id, item_id, users_to_recommend, n_rec):
        recomendation = model
        df_rec = recomendation.to_dataframe()
        df_rec['recommendedProducts'] = df_rec.groupby([user_id])[item_id].transform(lambda x: '|'.join(x.astype(str)))
        df_output = df_rec[['COD_CLIENTE','recommendedProducts']].drop_duplicates().sort_values('COD_CLIENTE')#.set_index('COD_CLIENTE')

        return df_output