#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
import pandas as pd
import pickle
from tqdm import tqdm

class DMean():
    
    def get_classif_dict(self, df_compras):
        classif_dict = self.create_classif_dict(df_compras)
        return classif_dict

    def get_d_mean_classif(self, classif, df_compras_grouped):
        class_grouped = df_compras_grouped.loc[df_compras_grouped['CLASSIFICACAO'] == classif]

        media_sum = 0
        for index, rows in class_grouped.iterrows():
            qtde = rows['QUANTIDADE_TOTAL']
            n_buys = rows['#_COMPRAS']
            media = float(qtde/n_buys)
            media_sum += media

        d_mean = media_sum/len(class_grouped)
        return d_mean

    def create_class_cliente_df(self, df_compras):
        #Resumo: Pega todas as todos os clientes de cada uma das classificacoes e faz um somatorio da quantidade de itens comprado e numero de compras
        df_compras = df_compras.copy()
        df_compras['COMPRA_DUMMY'] = 1
        df_compras_grouped = df_compras.groupby(['CLASSIFICACAO', 'COD_CLIENTE']).agg({'QUANTIDADE': ['sum'], 'COMPRA_DUMMY': ['sum']})
        df_compras_grouped.columns = ['QUANTIDADE_TOTAL', '#_COMPRAS']
        df_compras_grouped = df_compras_grouped.reset_index()

        df_class_cliente = pd.DataFrame(columns = ['CLASSIFICACAO', 'D_MEDIA'])
        df_class_cliente['CLASSIFICACAO'] = df_compras['CLASSIFICACAO'].unique()
        df_class_cliente = df_class_cliente.fillna({'D_MEDIA': 0})

        with tqdm(total=len(df_class_cliente)) as pbar:
            for index,rows in df_class_cliente.iterrows():
                classif = rows['CLASSIFICACAO']
                d_mean = self.get_d_mean_classif(classif, df_compras_grouped)
                df_class_cliente.loc[[index], 'D_MEDIA'] = d_mean
                pbar.update(1)

        #Retorna para a funcao de criar o dicionario de classificacao
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