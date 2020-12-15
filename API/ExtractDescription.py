#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*- 

import pandas as pd 
from requests import get
from tqdm import tqdm
import re
import html
from BdManagement import BdManagement

bd_manager = BdManagement()

class ExtractDescription():

    # HTML Dictionary to delete some "unnecessary" entities
    htmlEntities = {
        '\xa0': ' ',
        '\\\\n': '',
        '&bull;': '',
        '&trade;': '',
        '&reg;': '',
        '&sup1;': '',
        '&sup2;': '',
        '&sup3;': ''
    }
    
    #OBS.: Recebe db de vendas
    def create_df_product(self, db_cart):
        db_cart = db_cart[['COD_PRODUTO', 'NOME_PRODUTO']].copy()
        data = db_cart.drop_duplicates(ignore_index=True).copy()

        print("Iniciando extração das descrições...")
        # Extracting description from api 
        descriptions = []
        for product in tqdm(data.COD_PRODUTO):
            # Create url string to get products long Description
            url = 'https://www.armazempb.com.br/ccstoreui/v1/products/0' + str(product) + '?fields=longDescription'
            # Get text from the url
            text = get(url).text.encode('utf-8')
            # Set it to string, 'cause sometime it comes as "bytes" object
            text = str(text)
            # Get only the text that's between '>' and '<'
            match = re.findall(">(.*?)<", text)
            # Concatenate all string into one
            result = ""
            for string in match:
                result = result + string
                
            # Translate HTML Entities to string
            unescape_result = html.unescape(result)
            #For each entities on the dictonary replace the patterns with "" for each product
            for entities in self.htmlEntities:
                unescape_result = unescape_result.replace(entities, self.htmlEntities[entities])
                
            # Append the result on the descriptions list
            data.loc[data['COD_PRODUTO'] == product, 'DESCRIPTION'] = str(unescape_result)
            #descriptions.append(unescape_result)     

        # Add descriptions into the descriptions columns
        data.DESCRIPTION = data.DESCRIPTION.astype('str')
        # COLOCAR ESSE DATAFRAME NO BD
        bd_manager.updateProductTable(data)

        print("Tudo pronto!")