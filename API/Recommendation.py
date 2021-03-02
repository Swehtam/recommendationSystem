#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
from BdManagement import BdManagement
from ExtractDescription import ExtractDescription
from ClientProductMap import ClientProductMap
import pandas as pd
import numpy as np
from tqdm import tqdm

bd_manager = BdManagement()
description_extractor = ExtractDescription()

class Recommendation:

    db_cart = pd.DataFrame()
    db_purchase = pd.DataFrame()
    df_products = pd.DataFrame()
    
    ##**************** VARIAVEIS USADAS PARA TESTES DO RETRAIN********************
    """def __init__(self):
        self.db_cart = bd_manager.getSalesTable()
        self.db_cart.CLASSIFICACAO = self.db_cart.CLASSIFICACAO.apply(lambda x : x.strip())
        self.db_cart.QUANTIDADE = self.db_cart.QUANTIDADE.values.astype(np.int16)
        self.db_cart.COD_CLIENTE = self.db_cart.COD_CLIENTE.apply(lambda x : str(x))
        
        #self.db_purchase = bd_manager.getClientRecomTable()
        #self.db_purchase.QUANTIDADE = self.db_purchase.QUANTIDADE.astype('int16')
        
        self.df_products = bd_manager.getProductsTable()
        self.df_products.DESCRIPTION.fillna('', inplace=True)
        self.df_products.DESCRIPTION = self.df_products.DESCRIPTION.astype('str')"""
        

    def retrain_model(self, bicluster_recom, cart_recom, client_recom):
        # - Atualizar tabela de vendas 
        print("\nAtualizando todas tabela encontradas no DB...")
        print("\nAtualizando tabela de vendas...")
        self.db_cart = bd_manager.getSalesTable()
        self.db_cart.CLASSIFICACAO = self.db_cart.CLASSIFICACAO.apply(lambda x : x.strip())
        self.db_cart.QUANTIDADE = self.db_cart.QUANTIDADE.values.astype(np.int16)
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
        self.df_products.DESCRIPTION.fillna('', inplace=True)
        self.df_products.DESCRIPTION = self.df_products.DESCRIPTION.astype('str')
        print("\nFinalizado!...")
        print("\nAtualizações de tabelas finalizada...")
        
        # - Retrain Bicluster
        print("\nTreinando recomendações do bicluster...") 
        print("\nCriando tabela de adjacencia...")
        bicluster_recom.create_adjacency_list(self.db_cart)
        print("\nTreinando o Bicluster...")
        bicluster_recom.create_biclusters()
        print("\nTreinamento finalizado...")
        
        # - Criando mapa de cliente para produto (mapa usado pelos modelos do ClientRecom e CartRecom)
        print("\nCriando mapa de cliente para produto...")
        client_product_map = self.create_client_product_map()
        print("\nMapeamento finalizado...")
        
        # - Retrain Add To Cart:
        print("\nTreinando recomendações do carrinho...")
        cart_recom.create_cart_recommendation_output(self.db_cart, self.df_products, client_product_map)
        print("\nTreinamento finalizado...")
        
        # - Retrain Purchased Based:
        print("\nTreinando recomendação cliente...")
        client_recom.train_cliente_recom(self.db_purchase, client_product_map)
        print("\nTreinamento finalizado...")
        
        # - Retrain New Clients Purchase:
        #----- AINDA NAO TEM CODIGO DE FILIAL ENTAO N PRECISA TREINAR AINDA -----
        print("\nTreinando recomendação para novos clientes...")
        client_recom.train_new_clients(self.db_cart)
        print("\nTreinamento finalizado...")
        
        #Excluir variaveis para diminuir espaço na memória
        del self.db_cart
        del self.db_purchase
        del self.df_products
        del client_product_map
        return ("Recomendações atualizadas.")
        
    def create_client_product_map(self):
        client_product_map = ClientProductMap()
        #Adicionar no mapa, para cada um dos registros de vendas, o cliente, o produto e a quantidade
        with tqdm(total=len(self.db_cart)) as pbar:
            for index,rows in self.db_cart.iterrows():
                client_product_map.add(rows['COD_CLIENTE'], rows['COD_PRODUTO'], rows['QUANTIDADE'])
                pbar.update(1)
                
        return client_product_map