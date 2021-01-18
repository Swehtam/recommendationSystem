#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-

import pandas as pd
import turicreate as tc
import numpy as np
import dask.dataframe as dd

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

    class ClientProductMap: 
        def __init__(self):
            self.client_map = {}
            self.product_map = {}
            self.client_rmap = []
            self.product_rmap = []


            self.num_cli = -1
            self.num_prod = -1

            self.adj_list = []

            self.max = []
          
        def __del__(self):
            del self.client_map
            del self.product_map
            del self.client_rmap
            del self.product_rmap
            del self.adj_list
            del self.max
          
          
          
        def add(self, cod_cli, cod_prod, freq):
            #Pega o id do cliente a partir de cod_cli no seu mapa
            try:
                id_cli = self.client_map[cod_cli]
            except KeyError:
                #Se não houver este cliente no mapa criá-lo como um novo clinte
                self.num_cli += 1
                self.client_map[cod_cli] = self.num_cli
                self.client_rmap.append(cod_cli)
                id_cli = self.num_cli
                self.adj_list.append([])
              

            #Pega o id do produto a partir de cod_prod no seu mapa
            try:
                id_prod = self.product_map[cod_prod]
            except KeyError:
                #Se não houver este produto no mapa criá-lo como um novo produto
                self.num_prod += 1
                self.product_map[cod_prod] = self.num_prod
                self.product_rmap.append(cod_prod)
                id_prod = self.num_prod
                self.max.append(freq)
              
            #Procurando o produto na lista de adjacencia
            l_cli = self.adj_list[id_cli]
            new_prod = True
            for i in range(len(l_cli)):
                if(l_cli[i][0] == id_prod):
                    l_cli[i] = (l_cli[i][0], l_cli[i][1] + freq)
                    if(self.max[id_prod] < l_cli[i][1]):
                        self.max[id_prod] = l_cli[i][1]
                    new_prod = False
                    break
            #Se o produto não esta na lista, adicione
            if(new_prod == True):
                l_cli.append((id_prod, freq))
                if(self.max[id_prod] < freq):
                    self.max[id_prod] = freq
                  
          
        def getNormalizedFreq(self):
            M = []
            for id_cli in range(len(self.adj_list)):
                l_cli = self.adj_list[id_cli]
                for prod in l_cli:
                    id_prod = prod[0]
                    freq = prod[1]
                    norm = 0
                    if (self.max[id_prod] != 1):
                        norm = float((freq - 1) / (self.max[id_prod] - 1))
                    M.append((self.client_rmap[id_cli], self.product_rmap[id_prod], norm))
                  
            return M

