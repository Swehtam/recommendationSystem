#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*-
from SimilarityModel import SimilarityModel
from DMean import DMean
from BdManagement import BdManagement
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
import regex as re
from unidecode import unidecode
import nltk
nltk.download('stopwords')
nltk.download('rslp')

similarityModel = SimilarityModel()
dMean = DMean()
bd_manager = BdManagement()

class CartRecom():
    df_compras = None
    df_products = None
    #df_matrix_u_c = None #Acho que nao precisa
    stopwords = None 
    convert_produto = None
    cart_output = None
    
    def __init__(self, df_compras): 
        self.df_compras = df_compras
        self.df_products = bd_manager.getProductsTable()#self.df_products = pd.read_csv('df_product.csv', sep = ';')
        self.df_products = self.df_products.fillna('')
        self.convert_produto = pickle.load( open( "Bicluster/pickle/cart_convert_produto.pickle", "rb" ) )
        self.cart_output = pickle.load( open( "pickle/cart_output.pickle", "rb" ) )
        
        stopwords = nltk.corpus.stopwords.words('portuguese')
        stopwords.extend(["nao", "...", "[", ']'])
        stopwords.extend(["pois"])
        stopwords.extend(["qualquer"])
        stopwords.extend(["descrição"])
        stopwords.extend(["produto"])
        
    #Metodo para pegar a instancia de D_MEAN
    def get_d_mean(self):
        return dMean
        
    #Metodo para pegar a instancia de SimilarityModel
    def get_similarityModel(self):
        return similarityModel
    
    #Chamar na API quando for retreinar
    def create_matrix_u_c(self, df_compras):
        db_copy = df_compras.copy()
        db_copy['DUMMY'] = 1
        df_matrix_u_c = pd.pivot_table(db_copy, 
                                            values = 'DUMMY', 
                                            index = 'COD_CLIENTE', 
                                            columns = 'CLASSIFICACAO', 
                                            fill_value=0)
        df_matrix_u_c = df_matrix_u_c.T
        #matrix_u_c = self.df_matrix_u_c.copy()
        return df_matrix_u_c
        
    def get_products_to_recommend(self, code):
        index = self.convert_produto[code]
        
        return self.cart_output[index]
        
    def calculate_recommendations_similarity(self, code, max_recom=3):
        products = similarityModel.get_products_recom_array(code, max_recom, self.df_compras)
        products_codes = self.get_products_list(code, products)
        purchase_similarity = self.purchase_similarity_recom(products_codes, code)
        description_similarity = self.description_similarity_recom(products_codes, code)

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
        products_codes = [product[0] for product in products]
        products_codes.append(product_input)
        return products_codes
    
    #Modelo de recomendação por similaridade por compras
    def purchase_similarity_recom(self, products_codes, code):
        df_modelo = self.df_compras[self.df_compras.COD_PRODUTO.isin(products_codes)]
        
        df_matrix_purchase = pd.pivot_table(df_modelo, values = 'QUANTIDADE', index = 'COD_CLIENTE', columns = 'COD_PRODUTO', aggfunc=np.sum, fill_value=0)
        df_matrix_purchase = df_matrix_purchase.T
        cos_sim_purchase = cosine_similarity(df_matrix_purchase)
        
        df_matrix_index = df_matrix_purchase.copy().reset_index()
        for index,rows in df_matrix_index.iterrows():
            if (rows['COD_PRODUTO'] == code):
                similar_indexes = cos_sim_purchase[index].argsort()[:-100:-1]
                similar_items = [(cos_sim_purchase[index][i], df_matrix_index['COD_PRODUTO'][i]) for i in similar_indexes]
                return similar_items[1:]
        
    #Modelo de recomendação por similaridade de descrição dos produtos
    def description_similarity_recom(self, products_codes, code):
        df_modelo = self.df_products[self.df_products.COD_PRODUTO.isin(products_codes)]
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
        
        TF = TfidfVectorizer(analyzer='word', ngram_range=(1,3), min_df=0, stop_words=self.stopwords)
        TFIDF_matrix = TF.fit_transform(df_modelo['DESCRIPTION'])
                
        # Calculating cosine similarity
        cos_similarity = linear_kernel(TFIDF_matrix, TFIDF_matrix)
         
        for index,rows in df_modelo.iterrows():
            if (rows['COD_PRODUTO'] == code):
                similar_indexes = cos_similarity[index].argsort()[:-100:-1]
                #Lembrar de mudar o nome da coluna "COD_PRODUTO" para o nome correspondete na tabela de produtos
                similar_items = [(cos_similarity[index][i], df_modelo['COD_PRODUTO'][i]) for i in similar_indexes]
                return similar_items[1:]
                
    def create_cart_recommendation_output(self):
        df = self.df_compras[['COD_PRODUTO']]
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
        for key in convert_produto:
            results = self.calculate_recommendations_similarity(key)
            cart_output.append(results)

        self.cart_output = cart_output
        pickle.dump(self.cart_output, open("pickle/cart_output.pickle", "wb"))
    
    def update_df_products(self):
        self.df_products = bd_manager.getProductsTable()

    def update_df_compras(self, df_compras):
        self.df_compras = df_compras