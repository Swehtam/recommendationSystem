#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
import numpy as np
from tqdm import tqdm

class ClientProductMap:
    
    def __init__(self):
        self.client_map = {}
        self.product_map = {}
        self.client_rmap = []
        self.product_rmap = []
        
        
        self.num_cli = 0
        self.num_prod = 0
        
        self.adj_list_cli = []
        self.adj_list_prod = []

        ##Lista de produtos similares (similaridade de cosseno)
        self.l_sim_prod = []
        
        self.max = []
        
    def __del__(self):
        del self.client_map
        del self.product_map
        del self.client_rmap
        del self.product_rmap
        del self.adj_list_cli
        del self.adj_list_prod
        del self.l_sim_prod
        del self.max
        
        
        
    def add(self, cod_cli, cod_prod, freq):
        #Pega o id do cliente a partir de cod_cli no seu mapa
        try:
            id_cli = self.client_map[cod_cli]
        except KeyError:
            #Se não houver este cliente no mapa criá-lo como um novo clinte
            self.client_map[cod_cli] = self.num_cli
            self.client_rmap.append(cod_cli)
            id_cli = self.num_cli
            self.adj_list_cli.append([])
            self.num_cli += 1
            
        
        #Pega o id do produto a partir de cod_prod no seu mapa
        try:
            id_prod = self.product_map[cod_prod]
        except KeyError:
            #Se não houver este produto no mapa criá-lo como um novo produto
            self.product_map[cod_prod] = self.num_prod
            self.product_rmap.append(cod_prod)
            id_prod = self.num_prod
            self.max.append(freq)
            self.adj_list_prod.append([])
            self.l_sim_prod.append([])
            self.num_prod += 1
        
            
        #Adicionando o produto e o cliente em suas listas de Adjacencia
        l_cli = self.adj_list_cli[id_cli]
        l_prod = self.adj_list_prod[id_prod]
        new_prod = True
        for i in range(len(l_cli)):
            if(l_cli[i][0] == id_prod):
                l_cli[i] = (l_cli[i][0], l_cli[i][1] + freq)
                if(self.max[id_prod] < l_cli[i][1]):
                    self.max[id_prod] = l_cli[i][1]

                for i in range(len(l_prod)):
                    if (l_prod[i][0] == id_cli):
                        l_prod[i] = (l_prod[i][0], l_prod[i][1] + freq)
                
                new_prod = False
                break
        #Se o produto não esta na lista de clientes, adicione
        if(new_prod == True):
            l_cli.append((id_prod, freq))
            l_prod.append((id_cli, freq))
            if(self.max[id_prod] < freq):
                    self.max[id_prod] = freq

           
    def compute_cosine_similarity(self):
        freq_p1 = [0]*self.num_cli
        add_prod_N = [True]*self.num_prod

        with tqdm(total=len(self.adj_list_prod)) as pbar:
            for p1 in range(len(self.adj_list_prod)):
                l_p1 = self.adj_list_prod[p1]
                sum1 = 0

                for cli_p1 in l_p1:
                    f_p1 = cli_p1[1]
                    sum1 += f_p1 * f_p1
                    freq_p1[cli_p1[0]] = f_p1

                #Encontrando o N2 de p1   
                N_p1 = []
                add_prod_N[p1] = False
                for cli in l_p1:
                    l_prod = self.adj_list_cli[cli[0]]
                    for prod in l_prod:
                        if add_prod_N[prod[0]] == True:
                            N_p1.append(prod[0])
                            add_prod_N[prod[0]] = False

                for p2 in N_p1:
                    add_prod_N[p2] = True
                    l_p2 = self.adj_list_prod[p2]
                    sum1_2 = 0
                    sum2 = 0

                    for cli_p2 in l_p2:
                        f_p2 = cli_p2[1]
                        sum2 += f_p2 * f_p2
                        if freq_p1[cli_p2[0]] > 0:
                          sum1_2 += freq_p1[cli_p2[0]] * f_p2


                    if (sum1 != 0) and (sum2 != 0):
                        sim_cos = sum1_2/(np.sqrt(sum1) * np.sqrt(sum2))
                        if(sim_cos > 0):
                            self.l_sim_prod[p1].append((p2, sim_cos))

                #Zerando controles do p1
                add_prod_N[p1] = True
                for cli in l_p1:
                    freq_p1[cli[0]] = 0

                pbar.update(1)

        #ordenando os produtos pela similaridade
        for p in range(len(self.l_sim_prod)):
            self.l_sim_prod[p].sort(reverse=True, key=lambda prod: prod[1])

        return self.get_similar_products_list()
            
    def get_similar_products_list(self):
        list_sim_prod = {}
        for cod_prod in self.product_map:
            list_sim_prod[cod_prod] = self.get_similar_products(cod_prod)
        return list_sim_prod
    
    def get_similar_products(self, cod_prod):
        l_cod_prod = []
        id_prod = self.product_map[cod_prod]
        l_prod = self.l_sim_prod[id_prod]
        for prod in l_prod:
            l_cod_prod.append((self.product_rmap[prod[0]], prod[1]))

        return  l_cod_prod;   
        
    def getNormalizedFreq(self):
        M = []
        for id_cli in range(len(self.adj_list_cli)):
            l_cli = self.adj_list_cli[id_cli]
            for prod in l_cli:
                id_prod = prod[0]
                freq = prod[1]
                norm = float((freq - 1) / (self.max[id_prod] - 1))
                M.append((self.client_rmap[id_cli], self.product_rmap[id_prod], norm))
                
        return M