import pandas as pd 
from requests import get
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

class Scrapper():

    def add_prod_description(self, entry):
        # Reading csv 
        descriptions_df = pd.read_csv('data_final.csv', sep=';')
        descriptions_df = descriptions_df[['COD_PRODUTO', 'NOME_PRODUTO']].copy()
        descriptions_df = descriptions_df.drop_duplicates()
        # Dealing with json response 
        new_products = pd.DataFrame(entry)
        data_final = descriptions_df.append(new_products, ignore_index = True)
        # Adding a '0' character before each product code
        codes = []
        for code in tqdm(new_products.COD_PRODUTO):
            code = '0' + str(code)
            codes.append(code)

        data = data_final[['NOME_PRODUTO']].copy()
        data['CODE'] = codes
        # Extracting description from api 
        descriptions = []
        for product in tqdm(data.CODE):
            url = 'https://www.armazempb.com.br/ccstoreui/v1/products/' + str(product) + '?fields=longDescription'
            text = get(url).text.encode('utf-8') 
            match = re.findall(">(.*?)</", text)
            descriptions.append(match)     
        
        data['DESCRIPTION'] = descriptions   
        data.to_csv(r'data_description.csv', sep=';')
        print("Tudo pronto!")
        return "DB com descrições atualizada!"