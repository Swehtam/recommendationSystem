#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import numpy as np

class SimilarityModel():

    def create_cosine_similarity_matrix(self, matrix_u_c, classif_dict, df_compras, max_recom = 3):
        '''
            Cria dicionario contendo os possíveis produtos a serem recomendados,
            baseado na classificação do produto adicionado no carrinho

            Input: matrix_u_c - matriz transposta de usuario por classe de produto
            Output: sim_results - dicionário de classes de itens
                                 (key: classe, value: [classe, similaridade])
        '''
        #Cria o dicionário de classificação por produto
        print("\nCriando dicionário de classificacao por produto...")
        classif_product_dict = self.create_classif_product_dict(df_compras)

        matrix_u_c_compressed = csr_matrix(matrix_u_c, dtype=np.int8)
        cos_similarity = cosine_similarity(matrix_u_c_compressed)

        matrix_u_c_index = matrix_u_c.copy().reset_index()
        
        #Dicionario com os posíveis produtos a serem recomendados,
        #Baseado na classificação do produto adicionado no carrinho
        print("\nCriando dicionário de classificacao com possíveis produtos a serem recomendados...")
        classif_results = {} 
        for index,rows in matrix_u_c_index.iterrows():
            #Se for True então deixa a classificacao pra ser recomendada
            if (classif_dict[rows['CLASSIFICACAO']]): 
                similar_indexes = cos_similarity[index].argsort()[::-1]
                similar_indexes = similar_indexes[:max_recom]
            
            #Se for False tira o proprio nome da Classificacao da recomendação
            else: 
                similar_indexes = cos_similarity[index].argsort()[:-1]
                similar_indexes = similar_indexes[::-1]
                similar_indexes = similar_indexes[:max_recom]

            products_list = []
            for i in similar_indexes:
                classif = matrix_u_c_index['CLASSIFICACAO'][i]
                list_aux = classif_product_dict[classif]
                products_list = products_list + list_aux

            classif_results[rows['CLASSIFICACAO']] = products_list
        
        return classif_results

    #Metodo para criar um dicionario onde a chave é o nome da classificação
    #E os valores são os codigos dos produtos dessa classificação
    #Esse dicionário é criado para melhorar o acesso ao códigos dos produtos
    def create_classif_product_dict(self, df_compras):
        classif_product_dict = {}
        for classif in df_compras.CLASSIFICACAO.unique():
            classif_product_dict[classif] = df_compras.loc[df_compras['CLASSIFICACAO'] == classif]['COD_PRODUTO'].unique().tolist()
        
        return classif_product_dict