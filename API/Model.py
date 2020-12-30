#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-

import pandas as pd
import turicreate as tc
import numpy as np
from sklearn.model_selection import train_test_split
import dask.dataframe as dd

class Model:
    
    def dask_pivot_melt(classif, vendas):  
        vendas_classif = vendas.loc[vendas['CLASSIFICACAO'] == classif].copy()
        dask_vendas = dd.from_pandas(vendas_classif, npartitions=2)
        dask_vendas = dask_vendas.categorize(columns=['COD_PRODUTO'])
        #Faz a matriz esparsa de cliente por produto em cada categoria
        dask_vendas_pivot = dask_vendas.pivot_table(values='QUANTIDADE', index='COD_CLIENTE', columns='COD_PRODUTO', aggfunc='sum').fillna(0).astype('float16')
        #Ordena as categorias de COD PRODUTO para funcionar o min e o max
        dask_vendas_pivot.columns = dask_vendas_pivot.columns.as_ordered()
        #Faz a normalização da matriz esparsa
        dask_vendas_pivot = (dask_vendas_pivot-dask_vendas_pivot.min())/(dask_vendas_pivot.max()-dask_vendas_pivot.min())

        #Coloca em str para funcionar o reset index
        dask_vendas_pivot.columns = dask_vendas_pivot.columns.astype('str')
        dask_vendas_input = dask_vendas_pivot.reset_index()
        dask_vendas_input.index.names = ['FREQ_COMPRAS']
        #Faz o melt da matriz esparsa
        dask_data_norm = dd.melt(dask_vendas_input, id_vars=['COD_CLIENTE'], value_name='FREQ_COMPRAS')

        #Remove linhas desnecessárias
        dask_data_norm = dask_data_norm.loc[dask_data_norm['FREQ_COMPRAS'] > 0]

        #Transforma para pandas
        return dask_data_norm.compute()
    
    def matrix_normalization(self,db):
        #db.QUANTIDADE = db.QUANTIDADE.astype('int32')
        df_matrix = pd.pivot_table(db, 
                                   values = 'QUANTIDADE', 
                                   index = 'COD_CLIENTE', 
                                   columns = 'COD_PRODUTO', 
                                   aggfunc = np.sum,
                                   fill_value=0)
        columns = list(df_matrix.columns)
        df_matrix[columns] = df_matrix[columns].astype('float16')
        df_matrix_norm = (df_matrix-df_matrix.min())/(df_matrix.max()-df_matrix.min())
        columns = list(df_matrix_norm.columns)
        df_matrix_norm[columns] = df_matrix_norm[columns].astype('float16')
        del df_matrix
        del columns
        return df_matrix_norm

    def data_input_creation(self,df_matrix_norm):
        # create a table for input to the modeling
        columns = list(df_matrix_norm.columns)
        df_matrix_norm[columns] = df_matrix_norm[columns].astype('float16')
        data_input = df_matrix_norm.reset_index()
        del columns
        del df_matrix_norm
        data_input.index.names = ['FREQ_COMPRAS']
        data_norm = pd.melt(data_input, id_vars=['COD_CLIENTE'],
                            value_name='FREQ_COMPRAS')
        data_norm = data_norm.dropna()
        return data_norm

    # Returns train and test datasets as scalable dataframes
    def split_data(self,data):
        #train, test = train_test_split(data, test_size = .2)
        #train_data = tc.SFrame(train)
        #test_data = tc.SFrame(test)
        
        #return train_data, test_data
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
        df_output = df_rec[['COD_CLIENTE','recommendedProducts']].drop_duplicates().sort_values('COD_CLIENTE').set_index('COD_CLIENTE')

        #if print_csv:
        #    df_output.to_csv(r'output.csv', sep=';')
        #    print("An output file can be found with name 'output.csv'")

        return df_output

