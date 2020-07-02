'''import pandas as pd
import turicreate as tc
import numpy as np
from sklearn.model_selection import train_test_split
'''
class Model:
    print("ABRIU MODEL.PY")
'''    
    def matrix_normalization(self,db):
        df_matrix = pd.pivot_table(db, values = 'QUANTIDADE', index = 'COD_CLIENTE', columns = 'COD_PRODUTO')
        df_matrix_norm = (df_matrix-df_matrix.min())/(df_matrix.max()-df_matrix.min())
        return df_matrix_norm

    def data_input_creation(self,df_matrix_norm):
        # create a table for input to the modeling
        data_input = df_matrix_norm.reset_index()
        data_input.index.names = ['FREQ_COMPRAS']
        data_norm = pd.melt(data_input, id_vars=['COD_CLIENTE'],
                            value_name='FREQ_COMPRAS')
        data_norm = data_norm.dropna()
        return data_norm

    # Returns train and test datasets as scalable dataframes
    def split_data(self,data):
        train, test = train_test_split(data, test_size = .2)
        train_data = tc.SFrame(train)
        test_data = tc.SFrame(test)
        return train_data, test_data

    def recom_model(self,train_data, user_id, item_id, users_to_recommend, n_rec):
        model = tc.item_similarity_recommender.create(tc.SFrame(train_data),
                                                       user_id = user_id,
                                                       item_id = item_id,
                                                       target = 'FREQ_COMPRAS',
                                                       similarity_type='cosine')
        recom = model.recommend(users=users_to_recommend, k=n_rec)
        return recom

    def create_output(self,model, users_to_recommend, n_rec, print_csv=True):
        recomendation = model
        df_rec = recomendation.to_dataframe()
        df_rec['recommendedProducts'] = df_rec.groupby([user_id])[item_id].transform(lambda x: '|'.join(x.astype(str)))
        df_output = df_rec[['COD_CLIENTE', 'recommendedProducts']].drop_duplicates().sort_values('COD_CLIENTE').set_index('COD_CLIENTE')

        if print_csv:
            df_output.to_csv(r'output.csv', sep=';')
            print("An output file can be found with name 'output.csv'")

        return df_output
'''
