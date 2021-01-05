#!/usr/bin/env  python3.6.9
# -*- coding: utf-8 -*- 

import sys
sys.path.append(".")
from flask import Flask, jsonify, request, json
import json
import pandas as pd
from Purchase import Purchase
from Recommendation import Recommendation
from Description import Description
from Scrapper import Scrapper
from CartRecom import CartRecom
from Bicluster.BiclusterRecom import BiclusterRecom
from BdManagement import BdManagement

app = Flask(__name__)


add_product = Purchase()
retrain_recom = Recommendation()
description = Description()
scrap_desc = Scrapper()
cart_recom = CartRecom()
bicluster_recom = BiclusterRecom()
bd_manager = BdManagement()
#output = bd_manager.getOutputRecom()


# ************************************************************* #
# *********************** MÉTODOS GET ************************* #
# ************************************************************* #

@app.route('/')
def home():
    return "Você se conectou."

# - Lista todas as recomendações
@app.route('/recommendations', methods=['GET'])
def recommendations():
    #output = bd_manager.getOutputRecom()
    output.set_index(['COD_CLIENTE'], inplace=False)
    return output.to_json(), 200

# - Lista recomendações para um dado cliente
@app.route('/get_recommendations/', methods=['GET'])
def recom_per_user():    
    user_id = request.args.get('user_id', None)
    product_id = request.args.get('product_id', None)
    recommendations = {'CLIENT' : '', 'PRODUCT' : ''}
    if(user_id != None):
        try:            
            #output = bd_manager.getOutputRecom()
            print("Output recebido do BD.")
            # - Checar na recomendação do turicreate
            try:
                index = output[output['COD_CLIENTE']==user_id].index.values
                client_recom = output[output.index == index[0]].recommendedProducts.values[0].split('|')[:10]
                recommendations['CLIENT'] = client_recom
                print("RECOMENDAÇÂO TURICREATE: ", client_recom)
            # - Checar na recomendação do bicluster
            except:
                client_recom, return_code = recom_bicluster_user(user_id)
                recommendations['CLIENT'] = client_recom['BICLUSTER']
                print("RECOMENDAÇÂO BICLUSTER: ", client_recom)
            if(product_id == None):                                  
                return app.response_class(response = json.dumps(recommendations),
                                          status = 200,
                                          mimetype='application/json')
            else:
                product_id = int(product_id)
                product_recom = cart_recom.get_products_to_recommend(product_id)        
                recommendations['PRODUCT'] = product_recom
                return app.response_class(response = json.dumps(recommendations),
                                          status = 200,
                                          mimetype='application/json') 
        except:
            return app.response_class(response = json.dumps("Cliente não treinado, tente outro."),
                                          status = 405,
                                          mimetype='application/json')     
    elif(user_id == None and product_id != None):
        try:
            product_id = int(product_id)
            product_recom = cart_recom.get_products_to_recommend(product_id)
            recommendations['PRODUCT'] = product_recom
            return app.response_class(response = json.dumps(recommendations),
                                          status = 200,
                                          mimetype='application/json')   
        except:
            return app.response_class(response = jsonify({'error':'Produo não treinado, tente outro.'}),
                                          status = 405,
                                          mimetype='application/json') 
        return app.response_class(response = jsonify({'error':'Não há como gerar recomendações sem um produto ou cliente.'}),
                                          status = 406,
                                          mimetype='application/json')


# - Lista produtos semelhantes aos recomendados para o cliente
'''@app.route('/recommendations/desc/<string:user_id>', methods=['GET'])
def recom_desc_user(user_id):
    output = pd.read_csv('output.csv', sep = ";")
    index = output[output['COD_CLIENTE']==user_id].index.values
    if (len(index) == 0):
        return jsonify({'error':'not found'}), 404
    else:
        recoms = description.list_recom(output, user_id)
        return recoms.to_json(), 200
'''

# - Lista recomendações em que o produto aparece
@app.route('/recommendations/product/<string:product_id>', methods=['GET'])
def product_recom_summary(product_id):
    if(len(product_id) < 5):
        return jsonify({'error':'Não é um código de produto válido.'}), 404
    #output = bd_manager.getOutputRecom() #pd.read_csv('output.csv', sep = ";")
    contain_values = output[output['recommendedProducts'].str.contains(product_id)]
    if(len(contain_values) == 0):
        return jsonify({'error':'Não há recomendações com esse produto.'}), 404
    else:
        return contain_values.to_json(), 200

# Conta quantas vezes o produto foi recomendado
@app.route('/recommendations/count/<string:product_id>', methods=['GET'])
def product_recom_count(product_id):
    if(len(product_id) < 5):
        return jsonify({'error':'Não é um código de produto válido.'}), 404
    #output = bd_manager.getOutputRecom()
    contain_values = output[output['recommendedProducts'].str.contains(product_id)]
    count = ("Número de recomendações desse produto:", len(contain_values.index))
    if(len(contain_values) == 0):
        return jsonify({'error':'Não há recomendações com esse produto.'}), 404
    else:
        return jsonify(count), 200
        
# - Bicluster        
@app.route('/recommendations/bicluster/<string:user_id>', methods=['GET'])
def recom_bicluster_user(user_id):
    recoms = {'BICLUSTER' : ''}
    recoms['BICLUSTER'], return_code = bicluster_recom.recomenda_cliente(user_id)
    return json.dumps(recoms), return_code
        
# - Retreina o modelo
@app.route('/retrain', methods=['GET'])
def retrain():
    status, df_output = retrain_recom.retrain_model(bicluster_recom, cart_recom)
    output = df_output
    return status, 200

# ************************************************************** #
# *********************** MÉTODOS POST ************************* #
# ************************************************************** #

# - Adiciona produtos e suas respectivas descrições na base de descrições
@app.route('/update', methods=['POST'])
def add_new_product():
    entry = request.get_json()
    status = scrap_desc.add_prod_description(entry)
    return status, 201

# - Adiciona novas compras na base de treino
@app.route('/purchase/add', methods=['POST'])
def add_purchase():
    entry = request.get_json()
    status = add_product.add(entry)
    return status, 201

if __name__ == '__main__':
    #app.config['DEBUG'] = True
    app.run()
