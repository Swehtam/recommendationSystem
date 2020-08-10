#!/usr/bin/env python3.5.7
# -*- coding: utf-8 -*- 

import pandas as pd 
from requests import get
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

# Reading csv 
db = pd.read_csv('data_final.csv', sep=';')
db = db[['COD_PRODUTO', 'NOME_PRODUTO']].copy()
db = db.drop_duplicates()

# Adding a '0' character before each product code
codes = []
for code in tqdm(db.COD_PRODUTO):
    code = '0' + str(code)
    codes.append(code)

data = db[['NOME_PRODUTO']].copy()
data['CODE'] = codes

print("Caractere zero adicionado!")
print("Iniciando extração das descrições...")

# Extracting description from api 
descriptions = []
for product in tqdm(data.CODE):
    url = 'https://www.armazempb.com.br/ccstoreui/v1/products/' + str(product) + '?fields=longDescription'
    text = get(url).text.encode('utf-8') 
    match = re.findall(">(.*?)</", text)
    descriptions.append(match)     
    
data['DESCRIPTION'] = descriptions   
data.to_csv('data_description.csv', sep=';')

print("Tudo pronto!")