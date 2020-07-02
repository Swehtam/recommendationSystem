import pandas as pd
from Recommendation import Recommendation

class Purchase:

    def add(self, entry):
        new_rec = Recommendation()
        df = pd.read_csv('data_armz.csv', sep = ';')
        new_values = pd.DataFrame(entry)

        if(int(new_values['QUANTIDADE']) > 5):
            return ('Fornecedores não são permitidos.',
                    'Insira quantidades inferiores a 5.')
        else:
            new_df = df.append(new_values, ignore_index = True)
            new_df.to_csv(r'data_armz.csv', sep = ';', index = False)
            status = new_rec.retrain_model()
            print(status)
        return ("BD atualizada!")
