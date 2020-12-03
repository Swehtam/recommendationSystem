#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
from Model import Model
from SimilarityModel import SimilarityModel
from CartRecom import CartRecom
from DMean import DMean
import pandas as pd
import numpy as np
import pickle

model = Model()
similarityModel = SimilarityModel()
cartRecom = CartRecom()
dMean = DMean()

class Recommendation:
    
    matrix_u_c = []
    db_cart = pd.DataFrame()
    db_purchase = pd.DataFrame()
    df_matrix = []
    classif_dict = {}
    
    def __init__(self):
        self.db_cart = pd.read_csv('dados_vendas.csv', sep = ';')
        self.db_cart.CLASSIFICACAO = self.db_cart.CLASSIFICACAO.apply(lambda x : x.strip())
        self.matrix_u_c = cartRecom.create_matrix_u_c(self.db_cart)
        self.db_purchase = pd.read_csv('data_armz.csv', sep = ';')
        self.db_purchase.QUANTIDADE = self.db_purchase.QUANTIDADE.astype('int16')
        self.df_matrix = self.create_user_classif_matrix(self.db_cart)
        self.classif_dict = pickle.load(open("classif_dict.pickle", "rb"))
        
    def create_user_classif_matrix(self, df_compras):
        db_copy = df_compras.copy()
        db_copy['DUMMY'] = 1

        df_matrix = pd.pivot_table(db_copy, 
                                   values = 'DUMMY', 
                                   index = 'COD_CLIENTE', 
                                   columns = 'CLASSIFICACAO', 
                                   fill_value=0)
        df_matrix = df_matrix.T

        return df_matrix

    def retrain_model(self, bicluster_recom):
        db = self.db_purchase
        # - Retrain Bicluster
        print("\nTreinando recomendações do bicluster...") 
        print("\nCriando tabela de adjacencia...")
        bicluster_recom.create_adjacency_list(self.db_cart)
        print("\nTreinando o Bicluster...")
        bicluster_recom.execute_terminal_command()
        print("\nTreinamento finalizado...")
        
        # - Retrain Add To Cart:
        '''print("\nTreinando recomendações do carrinho...")   
        print("\nCalculando D-Mean...")
        print()
        dMean.create_class_cliente_df(self.db_cart)
        self.classif_dict = dMean.get_classif_dict()   
        print("\nCalculando matriz de similaridades...")
        self.matrix_u_c = cartRecom.create_matrix_u_c(self.db_cart)
        similarityModel.create_cosine_similarity_matrix(self.matrix_u_c, self.classif_dict)
        
        # - Retrain Purchased Based:
        # variables to define field names:
        # CHANGE TO READ THE PROVIDED DATA        
        user_id = 'COD_CLIENTE'
        item_id = 'COD_PRODUTO'
        item_name = 'NOME_PRODUTO'
        users_to_recommend = list(db[user_id])
        n_rec = 10 # itens to recommend

        print("\nTreinando purchased...")
        df_matrix_norm = model.matrix_normalization(db)
        data_norm = model.data_input_creation(df_matrix_norm)
        print("\nRealizando split nos dados...")
        train_data, test_data = model.split_data(data_norm)
        print("\nTreinando recomendações de compras...")
        recom = model.recom_model(train_data, user_id, item_id, users_to_recommend, n_rec)
        print("\nAtualizando informações de recomendações...")
        df_output = model.create_output(recom, user_id, item_id, users_to_recommend, n_rec, print_csv=True)'''
        return ("Recomendações atualizadas.")
