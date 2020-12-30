#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
from Model import Model
import pandas as pd
import numpy as np
from BdManagement import BdManagement
from ExtractDescription import ExtractDescription
import nltk
nltk.download('rslp')
from subprocess import Popen, PIPE
import shlex
from tqdm import tqdm

model = Model()
bd_manager = BdManagement()
description_extractor = ExtractDescription()

class Recommendation:

    db_cart = pd.DataFrame()
    db_purchase = pd.DataFrame()
    df_products = pd.DataFrame()
    
    ##**************** EU ACHO Q DA PRA TIRAR ISSO DAQUI NA PRODUÇÃO E DEIXAR PARA TESTES DO RETRAIN********************
    #def __init__(self):
        #self.db_cart = bd_manager.getSalesTable()
        #self.db_cart.CLASSIFICACAO = self.db_cart.CLASSIFICACAO.apply(lambda x : x.strip())
        
        #self.db_purchase = bd_manager.getClientRecomTable()
        #self.db_purchase.QUANTIDADE = self.db_purchase.QUANTIDADE.astype('int16')
        
        #self.df_products = bd_manager.getProductsTable()
        #self.df_products.DESCRIPTION = self.df_products.DESCRIPTION.astype('str')
        #self.df_products.DESCRIPTION.fillna('', inplace=True)

    def retrain_model(self, bicluster_recom, cart_recom):
        # - Atualizar tabela de vendas 
        print("\nAtualizando todas tabela encontradas no DB...")
        print("\nAtualizando tabela de vendas...")
        self.db_cart = bd_manager.getSalesTable()
        self.db_cart.CLASSIFICACAO = self.db_cart.CLASSIFICACAO.apply(lambda x : x.strip())
        self.db_cart.QUANTIDADE = self.db_cart.QUANTIDADE.values.astype(np.int16)
        self.db_cart.COD_PRODUTO = self.db_cart.COD_PRODUTO.apply(lambda x : str(x))
        self.db_cart.COD_CLIENTE = self.db_cart.COD_CLIENTE.apply(lambda x : str(x))
        print("\nFinalizado!...")

        # - Atualizar tabela de quantidade de compras por cliente
        print("\nAtualizando tabela para recomendação de cliente...")
        self.db_purchase = bd_manager.getClientRecomTable()
        self.db_purchase.QUANTIDADE = self.db_purchase.QUANTIDADE.astype('int16')
        print("\nFinalizado!...")

        # - Atualizar tabela de produtos
        print("\nAtualizando tabela de produtos no DB...")
        description_extractor.create_df_product(self.db_cart)
        self.df_products = bd_manager.getProductsTable()
        self.df_products.DESCRIPTION = self.df_products.DESCRIPTION.astype('str')
        self.df_products.DESCRIPTION.fillna('', inplace=True)
        print("\nFinalizado!...")
        print("\nAtualizações de tabelas finalizada...")
        
        # - Retrain Bicluster
        print("\nTreinando recomendações do bicluster...") 
        print("\nCriando tabela de adjacencia...")
        bicluster_recom.create_adjacency_list(self.db_cart)
        print("\nTreinando o Bicluster...")
        bicluster_recom.execute_terminal_command()
        print("\nTreinamento finalizado...")
        
        # - Retrain Add To Cart:
        print("\nTreinando recomendações do carrinho...")
        cart_recom.create_cart_recommendation_output(self.db_cart, self.df_products)
        print("\nTreinamento finalizado...")
        
        # - Retrain Purchased Based:
        # variables to define field names:
        # CHANGE TO READ THE PROVIDED DATA
        db = self.db_purchase        
        user_id = 'COD_CLIENTE'
        item_id = 'COD_PRODUTO'
        users_to_recommend = list(db[user_id].unique())
        n_rec = 10 # itens to recommend
        
        print("\nTreinando reomcendação cliente...")
        classif_array = self.db_cart.CLASSIFICACAO.unique()
        melt_df_array = []
        for classif in tqdm(classif_array):
          pandas_result = model.dask_pivot_melt(classif, self.db_cart)
          melt_df_array.append(pandas_result)
          
        print("\nConcatenando dataframes...")
        df_melt_total = pd.DataFrame()
        for df_melt in melt_df_array:
            df_melt_total = pd.concat([df_melt_total, df_melt], ignore_index=True)
          
        #df_matrix_norm = model.matrix_normalization(db)
        #data_norm = model.data_input_creation(df_matrix_norm)
        #print("\nRealizando split nos dados...")
        #train_data, test_data = model.split_data(data_norm)
        data_sframe = model.split_data(df_melt_total)
        print("\nTreinando recomendações de compras...")
        recom = model.recom_model(data_sframe, user_id, item_id, users_to_recommend, n_rec)
        print("\nAtualizando informações de recomendações...")
        df_output = model.create_output(recom, user_id, item_id, users_to_recommend, n_rec, print_csv=True)
        bd_manager.updateRecomTable(df_output)
        return ("Recomendações atualizadas."), df_output