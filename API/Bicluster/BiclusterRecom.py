#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os.path
from os import path
import shlex
from subprocess import Popen, PIPE
import pickle

class BiclusterRecom():
    convert_cliente = None
    revert_cliente = None
    convert_produto = None
    revert_produto = None
    n_produtos = None
    n_clientes = None
    clientes_cluster = None
    produtos_cluster = None
    biclusters = None
    #Variavel de teste para retreino
    teste = None
    
    def __init__(self):
        #Chamar o metodo para pegar o arquivo adjacency list
        outputname= "Bicluster/Adjacency_list.txt"
        self.get_adjacency_list(outputname)
        
        self.get_biclusters()
        
        self.teste = 1
        
    #Função para atualizar os valores das variaveis quando iniciar essa classe
    def get_adjacency_list(self, txt_file_name):
        if (path.exists(txt_file_name)):
            text_file = open(txt_file_name, mode="r", encoding='utf-8')
            self.n_clientes = int(text_file.readline())
            self.n_produtos = int(text_file.readline())
            self.convert_cliente = pickle.load( open( "Bicluster/pickle/convert_cliente.pickle", "rb" ) )
            self.revert_cliente = pickle.load( open( "Bicluster/pickle/revert_cliente.pickle", "rb" ) )
            self.convert_produto = pickle.load( open( "Bicluster/pickle/convert_produto.pickle", "rb" ) )
            self.revert_produto = pickle.load( open( "Bicluster/pickle/revert_produto.pickle", "rb" ) )
    
    #Função para criar ou pegar um bicluster do banco de dados
    def get_biclusters(self):
        if (path.exists("Bicluster/pickle/biclusters.pickle")):
            self.biclusters = pickle.load( open( "Bicluster/pickle/biclusters.pickle", "rb" ) )
            self.clientes_cluster = pickle.load( open( "Bicluster/pickle/clientes_cluster.pickle", "rb" ) )
            self.produtos_cluster = pickle.load( open( "Bicluster/pickle/produtos_cluster.pickle", "rb" ) )
        
    #Recomenda produtos pro cliente, entrada cod_cliente
    def recomenda_cliente(self, cliente):
        try:
            recomendations = []
            cliente_key = self.convert_cliente[cliente]
            clusters = self.clientes_cluster[cliente_key]
            for a in clusters:
                for j,b in enumerate(self.biclusters[a]):
                    if(j==1):
                        for x in b:
                            produto = self.revert_produto[x]
                            recomendations.append(int(produto))
            return recomendations, 202
        except KeyError:
            return "Cliente não encontrado", 404
        except:
            return "Erro inesperado encontrado, contacte o administrador", -1
           
    #Recomenda clientes baseado na entrada cod_produto
    def recomenda_produto(self, produto):
        try:
            recomendations=[]
            produto_key=self.convert_produto[produto]
            clusters=self.produtos_cluster[produto_key]
            scores=[]
            for a in clusters:
                for j,b in enumerate(self.biclusters[a]):
                    if(j==1):
                        for x in b:
                            if(x not in recomendations and x!= produto_key):
                                recomendations.append(x)
                                scores.append(similarity(produto_key,x,lista_adj_u,b))
            return [recomendations,scores]
        except KeyError:
            return 404 #"Produto não encontrado"
        except:
            return -1 #"Erro inesperado encontrado, contacte o administrador"
    
    #Cria os biclusters
    def create_biclusters(self):
        #Pega a saida em txt e faz a separação
        out = self.execute_terminal_command()
        
        print("\nCriando tabela de Bicluster...")
        f = out.decode("utf-8").split('\n')[-1]
        nonnumbers=['(',')','}',']']
        text=f.split('}')
        clustertext=text[0].split('[')
        solotext=text[1].split('(')
        
        #Faz a criação dos biclusters
        self.biclusters=[]
        self.clientes_cluster=[[] for x in range(self.n_clientes)]
        self.produtos_cluster=[[] for x in range(self.n_produtos)]
        #Clusters
        # i = indice do bicluster; a = valores do bliscuster, tupla [(usuarios), (produtos)]
        for i,a in enumerate(clustertext[1:]):
            #Singular
            bicluster=[]
            for j,b in enumerate(a.split('),')):
                array=[]
                for k,c in enumerate(b.replace('],','').split(',')):
                    txt=c
                    for r in nonnumbers:
                        txt=txt.replace(r, "")
                    if(txt!=''):
                        code=int(txt)
                        array.append(code)
                        if(not j):
                            self.clientes_cluster[code].append(i)
                        else:
                            self.produtos_cluster[code].append(i)
                #Bicluster no singular
                bicluster.append(array)
            #Bicluster no plural
            self.biclusters.append(bicluster)
           
        pickle.dump(self.clientes_cluster, open("Bicluster/pickle/clientes_cluster.pickle", "wb"))
        pickle.dump(self.produtos_cluster, open("Bicluster/pickle/produtos_cluster.pickle", "wb"))
        pickle.dump(self.biclusters, open("Bicluster/pickle/biclusters.pickle", "wb"))
        
        self.teste = 2
    
    #Cria a lista adjacente e criar o arquivo txt
    def create_adjacency_list(self, df_compras):
        #Ler arquivo de vendas
        df = df_compras[['COD_CLIENTE','COD_PRODUTO']] #Selecionando apenas as colunas que vão ser usadas
        df = df.drop_duplicates(keep='first') #Retirando linhas duplicadas, clientes que compraram o mesmo produto mais de uma vez
        self.n_clientes = df['COD_CLIENTE'].nunique() #Verificando o número de clientes
        self.n_produtos = df['COD_PRODUTO'].nunique() #Verificando o número de produtos
        
        #Mapeamento clientes
        self.convert_cliente={} #Array de conversão de ID do cliente para identificador inteiro começando por 0
        self.revert_cliente=['' for x in range(self.n_clientes)]
        c=0
        for x in df['COD_CLIENTE'].unique():
            self.convert_cliente[x]=c
            self.revert_cliente[c]=x
            c+=1
            
        #Salva o converte e reverte cliente em pickle
        pickle.dump(self.convert_cliente, open("Bicluster/pickle/convert_cliente.pickle", "wb"))
        pickle.dump(self.revert_cliente, open("Bicluster/pickle/revert_cliente.pickle", "wb"))
            
        #Mapeamento produtos
        self.convert_produto={}
        self.revert_produto=['' for x in range(self.n_produtos)]
        c=0
        for x in df['COD_PRODUTO'].unique():
            self.convert_produto[x]=c
            self.revert_produto[c]=x
            c+=1
            
        #Salva o converte e reverte produto em pickle
        pickle.dump(self.convert_produto, open("Bicluster/pickle/convert_produto.pickle", "wb"))
        pickle.dump(self.revert_produto, open("Bicluster/pickle/revert_produto.pickle", "wb"))
            
        #Criar lista de adjacencia
        lista_adj=[[] for x in range(self.n_clientes)] #Inicialização da lista de adjacência
        for index,row in df.iterrows():
            lista_adj[self.convert_cliente[row[0]]].append(self.convert_produto[row[1]])
        
        #Escrever lista em arquivo txt
        outputname= "Bicluste/Adjacency_list.txt"
        text_file = open(outputname, "w")
        text_file.write(str(self.n_clientes)+'\n')
        text_file.write(str(self.n_produtos)+'\n')
        for j in lista_adj:
            txt=str(j)[1:-1].replace(',',' ')
            text_file.write(txt+'\n')
        text_file.close()
        
    #Função para o python se comunicar com o terminal
    def get_exitcode_stdout_stderr(self, cmd):
        """
        Execute the external command and get its exitcode, stdout and stderr.
        """
        args = shlex.split(cmd)

        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        exitcode = proc.returncode
        #
        return exitcode, out, err
    
    #Metodo com os comandos para serem executados no terminal
    def execute_terminal_command(self):
        # Primeiro é necessario compilar os arquivos em C++ do professor Gilberto
        print("\nCompilando codigo do Bicluster...")
        cmd = 'g++ -o Bicluster/bc Bicluster/src/*.cpp'   # arbitrary external command, e.g. "python mytest.py"
        exitcode, out, err = self.get_exitcode_stdout_stderr(cmd)
        #Comando para rodar o bicluster
        
        cmd = 'chmod 755 Bicluster/bc'
        exitcode, out, err = self.get_exitcode_stdout_stderr(cmd)
        
        print("\nExecução do codigo em C++ do Bicluster...")
        cmd = 'Bicluster/bc Bicluster/Adjacency_list.txt 1 200 0.25 3 2 30 2'
        exitcode, out, err = self.get_exitcode_stdout_stderr(cmd)
        return out