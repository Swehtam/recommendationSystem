#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import pickle
import numpy as np

class SimilarityModel():
    sim_results = None
    
    def __init__(self):
        self.sim_results = pickle.load( open( "cosine_sim_matrix.pickle", "rb" ) )
        
        
    def save_matrix(self, cosine_sim_matrix):
        pickle.dump(cosine_sim_matrix, open("cosine_sim_matrix.pickle", "wb"))

    #Lembrar de pensar na melhor forma de passar esse 'classif_dict', por exemplo,
    #Pensar aonde vai criar o objeto da classe DMean para passar o 'classif_dict' como parametro
    #Teoricamente se criar mais de 1 objeto vai ter q ler os arquivos .pickle para cada objeto
    #Caso tenha como criar uma variavel static em python, então nao tem oq se precoupar com mais 1 objeto
    def create_cosine_similarity_matrix(self, matrix_u_c, classif_dict):
        '''
            Calcula a matriz de similaridades entre classificações

            Input: matrix_u_c - matriz transposta de usuario por classe de produto
            Output: results - dicionário de classes de itens
                            (key: classe, value: [classe, similaridade])
        '''
        matrix_u_c_compressed = csr_matrix(matrix_u_c, dtype=np.int8)
        cos_similarity = cosine_similarity(matrix_u_c_compressed)

        matrix_u_c_index = matrix_u_c.copy().reset_index()
        results = {} 
        for index,rows in matrix_u_c_index.iterrows():
            #Se for True então deixa a classificacao pra ser recomendada
            if (classif_dict[rows['CLASSIFICACAO']]): 
                similar_indexes = cos_similarity[index].argsort()[::-1]
                #Se for False tira o proprio nome da Classificacao da recomendação
            else: 
                similar_indexes = cos_similarity[index].argsort()[:-1]
                similar_indexes = similar_indexes[::-1]

            similar_items = [(cos_similarity[index][i], matrix_u_c_index['CLASSIFICACAO'][i]) for i in similar_indexes]
            results[rows['CLASSIFICACAO']] = similar_items
        
        self.save_matrix(results)

    def get_product_name(self, code, df_compras):
        name = df_compras.loc[df_compras['COD_PRODUTO'] == code]['NOME_PRODUTO'].values[0]
        return name.strip()

    def get_product_classif(self, code, df_compras):
        classif = df_compras.loc[df_compras['COD_PRODUTO'] == code]['CLASSIFICACAO'].values[0]
        return classif

    def recommendation(self, code, max_recom, df_compras):
        classification = self.get_product_classif(code, df_compras)
        name = self.get_product_name(code, df_compras)
        
        recoms = self.sim_results[classification][:max_recom]
        return recoms

    def get_products_recom_array(self, code, max_recom, df_compras):
        recoms = self.recommendation(code, max_recom, df_compras)
        
        df_products_recoms = pd.DataFrame(columns = ['COD_PRODUTO'])

        for rec in recoms:
            df_aux = df_compras.loc[df_compras['CLASSIFICACAO'] == rec[1]]['COD_PRODUTO']
            df_products_recoms = pd.concat([df_products_recoms, df_aux])
            
        df_products_recoms.drop_duplicates()

        return df_products_recoms.to_numpy()