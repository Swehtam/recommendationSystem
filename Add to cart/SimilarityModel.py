import pandas 
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

class SimilarityModel():
    def save_matrix(self, cosine_sim_matrix):
        pickle.dump(cosine_sim_matrix, open("/pickle/cosine_sim_matrix.pickle"))

    def create_cosine_similarity_matrix(self, matrix_u_i):
        '''
            Calcula a matriz de similaridades entre classificações

            Input: matrix_u_i - matriz transposta de usuario por classe de produto
            Output: results - dicionário de classes de itens
                            (key: classe, value: [classe, similaridade])
        '''
        matrix_u_i_compressed = csr_matrix(matrix_u_i, dtype=np.int8)
        cos_similarity = cosine_similarity(matrix_u_i_compressed)

        matrix_u_i_index = matrix_u_i.copy().reset_index()
        results = {} 
        for index,rows in matrix_u_i_index.iterrows():
            #Se for True então deixa a classificacao pra ser recomendada
            if (classif_dict[rows['CLASSIFICACAO']]): 
                similar_indexes = cos_similarity[index].argsort()[::-1]
                #Se for False tira o proprio nome da Classificacao da recomendação
            else: 
                similar_indexes = cos_similarity[index].argsort()[:-1]
                similar_indexes = similar_indexes[::-1]

            similar_items = [(cos_similarity[index][i], matrix_u_i_index['CLASSIFICACAO'][i]) for i in similar_indexes]
            results[rows['CLASSIFICACAO']] = similar_items
            self.save_matrix(results)
        #return results

    def get_product_name(self, code, df_compras):
        name = df_compras.loc[df_compras['COD_PRODUTO'] == code]['NOME_PRODUTO'].values[0]
        return name.strip()

    def get_product_classif(self, code, df_compras):
        classif = df_compras.loc[df_compras['COD_PRODUTO'] == code]['CLASSIFICACAO'].values[0]
        return classif

    def recommendation(self, code, max_recom):
        classification = get_product_classif(code)
        name = self.get_product_name(code)
        recoms = results[classification][:max_recom]
        return recoms

    def get_products_recom_array(self, recoms, df_compras):
        df_products_recoms = pd.DataFrame(columns = ['NOME_PRODUTO', 'COD_PRODUTO'])

        for rec in recoms:
            df_aux = df_compras.loc[df_compras['CLASSIFICACAO'] == rec[1]][['NOME_PRODUTO', 'COD_PRODUTO']]
            df_products_recoms = pd.concat([df_products_recoms, df_aux]).drop_duplicates()

        return df_products_recoms.to_numpy()