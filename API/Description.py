#!/usr/bin/env python3.5.7
# -*- coding: utf-8 -*- 
#!/usr/bin/env python3.5.7
# -*- coding: utf-8 -*- 
import pandas as pd 
from Recom import Recom
import re
recom = Recom()

class Description:
    def list_recom(self, output, user_id):
        # Reading data
        # Pegar o output de recomendação para um cliente (RECEBER ARRAY)
        index = output[output['COD_CLIENTE']==user_id].index.values
        client = output[output.index == index[0]].recommendedProducts.to_numpy()
        client = str(client[0])
        match = re.findall("[0-9]+", client)    
        products = []
        products.append(match)
        products = products[0]
        recoms = []
        for product in products:
            print('produto de num: ', product)
            recoms.append(recom.model(int(product),3))
            
        return recoms


