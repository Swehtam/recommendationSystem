#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
from SimilarityModel import SimilarityModel
from DMean import DMean
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
import regex as re
from unidecode import unidecode
import pickle
from tqdm import tqdm
import nltk
from scipy.sparse import csr_matrix
nltk.download('stopwords')
nltk.download('rslp')

similarityModel = SimilarityModel()
dMean = DMean()

class CartRecom():
    convert_produto = None
    cart_output = None
    
    def __init__(self):
        self.convert_produto = pickle.load( open( "pickle/cart_convert_produto.pickle", "rb" ) )
        self.cart_output = pickle.load( open( "pickle/cart_output.pickle", "rb" ) )
        
    def get_products_to_recommend(self, product_codes):
        multiple_recom = []
        n_prod = len(product_codes)
        for prod in product_codes:
            if (prod in self.convert_produto.keys()):
                index = self.convert_produto[prod]
                single_recom = self.cart_output[index]
                multiple_recom += single_recom
            else:
                n_prod -= 1
                if(n_prod == 0):
                    return None
                
        similarity_dict = {}
        [similarity_dict [t [0]].append(t [1]) if t [0] in list(similarity_dict.keys()) else similarity_dict.update({t [0]: [t [1]]}) for t in multiple_recom]
        for key in similarity_dict:
            similarity_dict[key] = sum(similarity_dict[key])/n_prod            
            
        recommended_products = sorted(similarity_dict.items(), key=lambda x: x[1], reverse = True)
        recommended_products = [str(lis[0]) for lis in recommended_products]
        return recommended_products[:10]
        
    def calculate_recommendations_similarity(self, code, classif, classif_results, prod_similarity, df_products, cos_similarity):
        products = classif_results[classif]

        products_codes = self.get_products_dict(code, products)

        #Pega os 100 produtos mais similares que fazem parte das categorias similares
        purchase_similarity = prod_similarity[code]
        purchase_similarity_filtered = []
        count = 0
        for i in purchase_similarity:
            if count < 100:
                if i[0] in products_codes:
                    purchase_similarity_filtered.append([i[0], i[1]])
                    count += 1
            else:
                break

        '''description_similarity = self.description_similarity_recom(products_codes, code, df_products, cos_similarity)
        
        #Calcular a média das tuplas de cada uma das recomendações
        all_tuples_similarity = description_similarity + purchase_similarity_filtered
        similarity_dict = {}
        #Cria um dicionario e o preenche com os valores de cada uma das recomendações 
        [similarity_dict [t [0]].append(t [1]) if t [0] in list(similarity_dict.keys()) else similarity_dict.update({t [0]: [t [1]]}) for t in all_tuples_similarity]
        for key in similarity_dict:
            similarity_dict[key] = sum(similarity_dict[key])/2

        recommended_products = sorted(similarity_dict.items(), key=lambda x: x[1], reverse = True)
        recommended_products = [lis for lis in recommended_products]'''
        recommended_products = sorted(purchase_similarity_filtered, key=lambda x: x[1], reverse = True)
        return recommended_products[:10]
    
    def get_products_dict(self, code, products):
        # - pega os codigos dos produtos que devem ser recomendados
        products.append(code)
        # Caso o próprio codigo do produto ja esteja nessa lista irá tirar sua duplicata
        products_codes = dict.fromkeys(products)
        return products_codes
        
    #Modelo de recomendação por similaridade de descrição dos produtos
    def description_similarity_recom(self, products_codes, code, df_products, cos_similarity):
        index = df_products.index[df_products['COD_PRODUTO'] == code].tolist()[0]
        cos_similarity = cos_similarity[index]
        
        similar_indexes = cos_similarity.argsort()[::-1]
        similar_items = [(df_products['COD_PRODUTO'][i], cos_similarity[i]) for i in similar_indexes if df_products['COD_PRODUTO'][i] in products_codes]
        return similar_items[1:101]
                
    #Cria uma matrix esparsa de classificacao por produto
    def create_matrix_u_c(self, df_compras):
        db_copy = df_compras.copy()
        db_copy['DUMMY'] = 1
        #É mais eficiente fazer cliente por classificacao
        df_matrix_u_c = pd.pivot_table(db_copy, 
                                            values = 'DUMMY', 
                                            index = 'COD_CLIENTE', 
                                            columns = 'CLASSIFICACAO', 
                                            fill_value=0)
        #E depois faz sua transposta para ter o resultado desejado nesse metodo
        df_matrix_u_c = df_matrix_u_c.T
        return df_matrix_u_c
                
    def create_cart_recommendation_output(self, df_compras, df_products, client_product_map):
        print("\nCalculando D-Mean...")
        classif_dict = dMean.get_classif_dict(df_compras)   
        print("\nCalculando matriz de similaridades...")
        matrix_u_c = self.create_matrix_u_c(df_compras)
        classif_results = similarityModel.create_cosine_similarity_matrix(matrix_u_c, classif_dict, df_compras)
        
        df = df_compras[['COD_PRODUTO']]
        df = df.copy()
        df = df.drop_duplicates()

        #Mapeamento produtos
        convert_produto={}
        c=0
        for code in df['COD_PRODUTO'].unique():
            convert_produto[code]=c
            c+=1
        
        self.convert_produto = convert_produto
        pickle.dump(self.convert_produto, open("pickle/cart_convert_produto.pickle", "wb"))
        
        #Criar o stopwords para serem usados na recomendação baseado na similaridade de descrições
        stopwords = nltk.corpus.stopwords.words('portuguese')
        stopwords.extend(["nao", "...", "[", ']'])
        stopwords.extend(["pois"])
        stopwords.extend(["qualquer"])
        stopwords.extend(["descrição"])
        stopwords.extend(["produto"])
        
        #Nessa parte é realizada uma unica vez o calculo da similaridade entre os produtos
        TF = TfidfVectorizer(analyzer='word', ngram_range=(1,1), min_df=0, stop_words=stopwords) #Deixando assim sera realizado os scores em cima de cada palavra e nao, além disso, mais a combinação das mesmas
        TFIDF_matrix = TF.fit_transform(df_products['DESCRIPTION'])
        TFIDF_matrix_sparse = csr_matrix(TFIDF_matrix)
        cos_similarity = linear_kernel(TFIDF_matrix_sparse, TFIDF_matrix_sparse)
        
        cart_output = []
        print("\nCalculando Similaridade entre os produtos...")
        prod_similarity = client_product_map.compute_cosine_similarity()
        print("\nCriando o output para cada produto...")
        with tqdm(total=len(self.convert_produto)) as pbar:
            for key in self.convert_produto:
                #Pega a classificação do produto
                classif = df_compras.loc[df_compras['COD_PRODUTO'] == key]['CLASSIFICACAO'].values[0]
                results = self.calculate_recommendations_similarity(key, classif, classif_results, prod_similarity, df_products, cos_similarity)
                cart_output.append(results)
                pbar.update(1)

        self.cart_output = cart_output
        pickle.dump(self.cart_output, open("pickle/cart_output.pickle", "wb"))