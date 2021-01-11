#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm
from Model import Model
from BdManagement import BdManagement

bd_manager = BdManagement()
model = Model()

class ClientRecom():
    convert_filial = None
    new_client_output = None
    client_output = None
    
    def __init__(self):
        self.convert_filial = pickle.load( open( "pickle/client_convert_filial.pickle", "rb" ) )
        self.new_client_output = pickle.load( open( "pickle/new_client_output.pickle", "rb" ) )
        self.client_output = bd_manager.getOutputRecom()
        
    def get_client_to_recommend(self, user_id):
        recom = None
        try:
            index = self.client_output[self.client_output['COD_CLIENTE']==user_id].index.values
            recom = self.client_output[self.client_output.index == index[0]].recommendedProducts.values[0].split('|')[:10]
            
        except:
            recom = None
        
        return recom
        
    def recommend_to_new_client(self, cod_filial):
        recom = None
        try:
            #Pega o codigo da filial, com ele recebe a posição no array referente ao cod_filial e retorna os codigos dos produtos corretos
            recom = self.new_client_output[self.convert_filial[cod_filial]]
            
        except:
            recom = None
            
        return recom
        
    def recommendations(self):
        output = self.client_output.set_index(['COD_CLIENTE'], inplace=False)
        
        return output
    
    def get_clients_output(self):
        return self.client_output
        
    def train_new_clients(self, db_cart):
        #Realiza o Agrupamento por cod_filial e cod_produto, somando a quantidade de produtos vendidos
        most_sold_products = db_cart.groupby(["COD_FILIAL", "COD_PRODUTO"], as_index = False).agg({"QUANTIDADE": 'sum'})
        
        #Pega o codigo do produto e sua classificação
        products_classif = db_cart[['COD_PRODUTO', 'CLASSIFICACAO']].drop_duplicates()
        
        #Junta as duas tabelas para juntar obter a coluna classificação
        df_products_classif = most_sold_products.merge(products_classif, how='inner', on='COD_PRODUTO')
        #Ordena a tabela do mais vendido para o menos vendido de cada filial
        df_products_classif = df_products_classif.sort_values(by=['COD_FILIAL', 'QUANTIDADE'], ascending=False)
        
        #Conver_filial recebe um codigo de filial e retorna a posição no array new_client_output referente a essa filial
        convert_filial={}
        c=0
        filial_unique = df_products_classif.COD_FILIAL.unique()
        for filial in filial_unique:
            convert_filial[filial]=c
            c+=1
            
        self.convert_filial = convert_filial
        pickle.dump(self.convert_filial, open("pickle/client_convert_filial.pickle", "wb"))

        #Filial output contem em cada elemento uma lista de produtos para cada uma das filiais
        new_client_output = []
        for filial in filial_unique:
            #Remove as duplicatas de acordo com a classificação em cada filial
            #Sendo assim a primeira ocorrencia de uma determinada classificação, em cada filial, é mantida
            filial_products = df_products_classif[df_products_classif.COD_FILIAL == filial].drop_duplicates(subset=['CLASSIFICACAO'])[:10]
            new_client_output.append(filial_products.COD_PRODUTO.to_list())
            
        self.new_client_output = new_client_output
        pickle.dump(self.new_client_output, open("pickle/new_client_output.pickle", "wb"))
        
    def train_cliente_recom(self, db_purchase):
        classif_array = db_purchase.CLASSIFICACAO.unique()
        melt_df_array = []
        for classif in tqdm(classif_array):
          pandas_result = model.dask_pivot_melt(classif, db_purchase)
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
        users_to_recommend = list(db_purchase['COD_CLIENTE'].unique())
        n_rec = 10 # itens to recommend
        recom = model.recom_model(data_sframe, 'COD_CLIENTE', 'COD_PRODUTO', users_to_recommend, n_rec)
        
        print("\nAtualizando informações de recomendações...")
        df_output = model.create_output(recom, 'COD_CLIENTE', 'COD_PRODUTO', users_to_recommend, n_rec)
        self.client_output = df_output
        bd_manager.updateRecomTable(self.client_output)