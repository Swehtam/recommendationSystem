from Model import Model
import pandas as pd
import numpy as np

class Recommendation:

    model = Model()

    # variables to define field names:
    db = pd.read_csv('data_final.csv', sep = ';')
    user_id = 'COD_CLIENTE'
    item_id = 'COD_PRODUTO'
    item_name = 'NOME_PRODUTO'
    #users_to_recommend = list(db[user_id])
    n_recommendation = 10 # itens to recommend

    def retrain_model(self):
        print("abriu o treinamento")
        return ("Recomendações atualizadas.")


    '''

    df_matrix_norm = model.matrix_normalization(db)
    data_norm = model.data_input_creation(df_matrix_norm)
    train_data, test_data = model.train_test_split(data_norm)
    recom = model.recom_model(train_data, user_id, item_id, users_to_recommend, n_rec)
    df_output = model.create_output(recom, users_to_recommend, n_rec, print_csv=True)
    '''
