#!/usr/bin/env python3.6.9
# -*- coding: utf-8 -*- 

import pandas as pd 
from requests import get
from tqdm import tqdm
import re
import html
import regex as re
from unidecode import unidecode
import nltk
from nltk.tokenize import word_tokenize
from BdManagement import BdManagement
nltk.download('rslp')
nltk.download('punkt')

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
        db_cart = db_cart[['COD_PRODUTO', 'NOME_PRODUTO']]
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
        data.DESCRIPTION = data.DESCRIPTION.fillna('')
        data.DESCRIPTION = data.DESCRIPTION.astype('str')
        
        data.DESCRIPTION = data.DESCRIPTION.apply(lambda x : x.lower())
        # - remove números e caracteres especiais 
        data.DESCRIPTION = data.DESCRIPTION.apply(lambda x : re.sub('[||\.|/|$|\(|\)|-|\+|:|•]', ' ', x))
        # - remove acentos 
        data.DESCRIPTION = data.DESCRIPTION.apply(lambda x: unidecode(x))

        # - reduz as palavras a seus radicais
        stemmer = nltk.stem.RSLPStemmer()
        data.DESCRIPTION = data.DESCRIPTION.apply(lambda x: self.stemSentence(x))
        # COLOCAR ESSE DATAFRAME NO BD
        #bd_manager.updateProductTable(data)

        print("Tudo pronto!")
        
    def stemSentence(sentence):
        token_words=word_tokenize(sentence)
        stem_sentence=[]
        for word in token_words:
            stem_sentence.append(stemmer.stem(word))
            stem_sentence.append(" ")
        return "".join(stem_sentence)