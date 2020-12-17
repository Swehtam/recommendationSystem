#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
import pandas as pd
import pickle
from tqdm import tqdm

class DMean():
    
    def get_classif_dict(self, df_compras):
        classif_dict = self.create_classif_dict(df_compras)
        return classif_dict
        
    def get_media_sum_cliente(self, df_media_cliente):
        media_sum = 0
        for index, rows in df_media_cliente.iterrows():
            qtde = rows['QUANTIDADE_TOTAL']
            n_buys = rows['#_COMPRAS']
            media = float(qtde/n_buys)
            media_sum += media
        return media_sum

    def get_d_mean_classif(self, classif, df_compras):        
        # - Cria df para a media de compras dos clientes nessa classificacao
        df_media_cliente = pd.DataFrame(columns = ['COD_CLIENTE', 'QUANTIDADE_TOTAL', '#_COMPRAS'])
        # - Filtra o banco de compras pra pegar as compras da classificacao
        df_classificacao = df_compras.loc[df_compras['CLASSIFICACAO'] == classif]
        # - Pega o codigo de todos os clientes que ja compraram nessa classificacao
        clientes = df_classificacao['COD_CLIENTE'].unique()
        df_media_cliente['COD_CLIENTE'] = clientes
        df_media_cliente = df_media_cliente.fillna({'QUANTIDADE_TOTAL': 0, '#_COMPRAS': 0})

        # - Itera a tabela de compras da classificacao 
        # - Somando a quantitade total de produtos e a quantidade de compras por cliente
        for index,rows in df_classificacao.iterrows():
            # - Pega o cliente da compra
            clien = rows['COD_CLIENTE']
            # - Pega a quantidade total de produtos já salvo
            old_qtde = df_media_cliente.loc[df_media_cliente['COD_CLIENTE'] == clien]['QUANTIDADE_TOTAL']
            # - Soma com a quantidade de produtos da compra e soma com a antiga
            new_qtde = rows['QUANTIDADE'] + old_qtde

            # - Pega a quantidade antiga de compras
            old_n_buys = df_media_cliente.loc[df_media_cliente['COD_CLIENTE'] == clien]['#_COMPRAS']

            # - Salva a nova quantidade de produtos
            df_media_cliente.loc[df_media_cliente['COD_CLIENTE'] == clien, 'QUANTIDADE_TOTAL'] = new_qtde
            # - Soma +1 na quantidade antiga de compras na nova quantidade de compras
            df_media_cliente.loc[df_media_cliente['COD_CLIENTE'] == clien, '#_COMPRAS'] = old_n_buys + 1

        #Pega a soma da media de cada cliente
        media_sum = self.get_media_sum_cliente(df_media_cliente)
        n_clientes = df_classificacao['COD_CLIENTE'].unique().size
        d_mean = float(media_sum/n_clientes)

        return d_mean

    def create_class_cliente_df(self, df_compras):
        df_class_cliente = pd.DataFrame(columns = ['CLASSIFICACAO', 'D_MEDIA'])
        df_class_cliente['CLASSIFICACAO'] = df_compras['CLASSIFICACAO'].unique()
        df_class_cliente = df_class_cliente.fillna({'D_MEDIA': 0})

        for index,rows in tqdm(df_class_cliente.iterrows()):
            classif = rows['CLASSIFICACAO']
            #print("classificacao: " + classif)
            d_mean = self.get_d_mean_classif(classif, df_compras)
            df_class_cliente.loc[[index], 'D_MEDIA'] = d_mean
        
        #Retorna para a fun??o de criar o dicionario de classificacao
        return df_class_cliente
        
    def create_classif_dict(self, df_compras):
        df_class_cliente = self.create_class_cliente_df(df_compras)
        std = df_class_cliente.D_MEDIA.std()
        mean = df_class_cliente.D_MEDIA.mean()

        d_mean_threshold = mean + std

        classif_dict = {}
        for index,rows in df_class_cliente.iterrows():
            if (rows['D_MEDIA'] >= d_mean_threshold):
                classif_dict[rows['CLASSIFICACAO']] = True
            else:
                classif_dict[rows['CLASSIFICACAO']] = False

        return classif_dict