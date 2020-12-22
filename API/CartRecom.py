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
        
    def get_products_to_recommend(self, code):
        index = self.convert_produto[code]
        
        return self.cart_output[index]
        
    def calculate_recommendations_similarity(self, code, df_compras, df_products, sim_results, max_recom=2):
        #Criar o stopwords para serem usados na recomendação baseado na similaridade de descrições
        stopwords = nltk.corpus.stopwords.words('portuguese')
        stopwords.extend(["nao", "...", "[", ']'])
        stopwords.extend(["pois"])
        stopwords.extend(["qualquer"])
        stopwords.extend(["descrição"])
        stopwords.extend(["produto"])
        
        products = similarityModel.get_products_recom_array(code, max_recom, df_compras, sim_results)
        products_codes = self.get_products_list(code, products)
        purchase_similarity = self.purchase_similarity_recom(products_codes, code, df_compras)
        description_similarity = self.description_similarity_recom(products_codes, code, df_products, stopwords)

        #Calcular a média das tuplas de cada uma das recomendações
        all_tuples_similarity = description_similarity + purchase_similarity
        similarity_dict = {}
        #Cria um dicionario e o preenche com os valores de cada uma das recomendações 
        [similarity_dict [t [1]].append(t [0]) if t [1] in list(similarity_dict.keys()) else similarity_dict.update({t [1]: [t [0]]}) for t in all_tuples_similarity]
        for key in similarity_dict:
          similarity_dict[key] = sum(similarity_dict[key])/2

        recommended_products = sorted(similarity_dict.items(), key=lambda x: x[1], reverse = True)
        recommended_products = [str(lis[0]) for lis in recommended_products] 
        return recommended_products[:10]
    
    def get_products_list(self, code, products):
        # - pega os codigos dos produtos que devem ser recomendados
        products_codes = [product for product in products]
        products_codes.append(code)
        # Caso o próprio codigo do produto ja esteja nessa lista irá tirar sua duplicata
        products_codes = list(dict.fromkeys(products_codes))
        return products_codes
    
    #Modelo de recomendação por similaridade por compras
    def purchase_similarity_recom(self, products_codes, code, df_compras):
        df_modelo = df_compras[df_compras.COD_PRODUTO.isin(products_codes)]

        #Mais rapido do q o pivot table
        df_matrix_purchase = df_modelo.groupby(["COD_PRODUTO", "COD_CLIENTE"]).agg({"QUANTIDADE": 'sum'}).unstack(level="COD_PRODUTO").fillna(0)
        df_matrix_purchase.columns = df_matrix_purchase.columns.droplevel(0)
        df_matrix_purchase = df_matrix_purchase.T
        
        df_matrix_purchase_compressed = csr_matrix(df_matrix_purchase)
        cos_sim_purchase = cosine_similarity(df_matrix_purchase_compressed)
        
        df_matrix_purchase = df_matrix_purchase.reset_index()
        index = 0
        for p_code in df_matrix_purchase['COD_PRODUTO']:
            if (p_code == code):
                similar_indexes = cos_sim_purchase[index].argsort()[:-100:-1]
                similar_items = [(cos_sim_purchase[index][i], df_matrix_purchase['COD_PRODUTO'][i]) for i in similar_indexes]
                return similar_items[1:]
                
            index += 1
        
    #Modelo de recomendação por similaridade de descrição dos produtos
    def description_similarity_recom(self, products_codes, code, df_products, stopwords):
        df_modelo = df_products[df_products.COD_PRODUTO.isin(products_codes)]
        df_modelo = df_modelo.copy()
        df_modelo.DESCRIPTION = df_modelo.DESCRIPTION.astype('str')

        df_modelo.DESCRIPTION = df_modelo.DESCRIPTION.apply(lambda x : x.lower())
        # - remove números e caracteres especiais 
        df_modelo.DESCRIPTION = df_modelo.DESCRIPTION.apply(lambda x : re.sub('[||\.|/|$|\(|\)|-|\+|:|•]', ' ', x))
        # - remove acentos 
        df_modelo.DESCRIPTION = df_modelo.DESCRIPTION.apply(lambda x: unidecode(x))

        # - reduz as palavras a seus radicais 
        stemmer = nltk.stem.RSLPStemmer()
        df_modelo.DESCRIPTION = df_modelo.DESCRIPTION.apply(lambda x: stemmer.stem(x))
        
        # - reseta indices
        df_modelo.reset_index(inplace = True)
        
        TF = TfidfVectorizer(analyzer='word', ngram_range=(1,3), min_df=0, stop_words=stopwords)
        TFIDF_matrix = TF.fit_transform(df_modelo['DESCRIPTION'])
                
        # Calculating cosine similarity
        TFIDF_matrix_sparse = csr_matrix(TFIDF_matrix)
        cos_similarity = linear_kernel(TFIDF_matrix_sparse, TFIDF_matrix_sparse)
                
        index = 0
        for p_code in df_modelo['COD_PRODUTO']:
            if (p_code == code):
                similar_indexes = cos_similarity[index].argsort()[:-100:-1]
                similar_items = [(cos_similarity[index][i], df_modelo['COD_PRODUTO'][i]) for i in similar_indexes]
                return similar_items[1:]
                
            index += 1
                
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
                
    def create_cart_recommendation_output(self, df_compras, df_products):
        print("\nCalculando D-Mean...")
        classif_dict = dMean.get_classif_dict(df_compras)   
        print("\nCalculando matriz de similaridades...")
        matrix_u_c = self.create_matrix_u_c(df_compras)
        sim_results = similarityModel.create_cosine_similarity_matrix(matrix_u_c, classif_dict)
        
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
        
        cart_output = []
        print("\nCriando o output para cada produto...")
        with tqdm(total=len(self.convert_produto)) as pbar:
            for key in self.convert_produto:
                results = self.calculate_recommendations_similarity(key, df_compras, df_products, sim_results)
                cart_output.append(results)
                pbar.update(1)

        self.cart_output = cart_output
        pickle.dump(self.cart_output, open("pickle/cart_output.pickle", "wb"))