import pandas as pd
from Recommendation import Recommendation

class Purchase:

    def add(self, entry):
        new_rec = Recommendation()
        df = pd.read_csv('data_armz.csv', sep = ';')
        new_values = pd.DataFrame(entry)        
        new_values.head() 
        #Deleting possible providers - they cause the BD to be biased
        new_values.drop(new_values[new_values.QUANTIDADE.astype(int) > 5].index, inplace=True)
        new_df = df.append(new_values, ignore_index = True)
        new_df.to_csv(r'data_armz.csv', sep = ';', index = False)
        status = new_rec.retrain_model()
        print(status)
        return ("BD atualizada! Compras de quantidade superior a 5 foram desconsideradas.")
