#!/usr/bin/env  python3.6.9
# -*- coding: utf-8 -*- 

import sys
sys.path.append(".")
from flask import Flask, jsonify, request
import json
import pandas as pd
from Purchase import Purchase
from Recommendation import Recommendation
from Description import Description
from Scrapper import Scrapper
from CartRecom import CartRecom
from Bicluster.BiclusterRecom import BiclusterRecom

app = Flask(__name__)
add_product = Purchase()
retrain_recom = Recommendation()
description = Description()
scrap_desc = Scrapper()
cart_recom = CartRecom()
bicluster_recom = BiclusterRecom(retrain_recom.db_cart)

# ************************************************************* #
# *********************** MÉTODOS GET ************************* #
# ************************************************************* #

@app.route('/')
def home():
    return "Você se conectou."

# - Lista todas as recomendações
@app.route('/recommendations', methods=['GET'])
def recommendations():
    output = pd.read_csv('output.csv', sep = ";")
    output.set_index(['COD_CLIENTE'], inplace=False)
    return output.to_json(), 200

# - Lista recomendações para um dado cliente
@app.route('/get_recommendations/', methods=['GET'])
def recom_per_user():    
    user_id = request.args.get('user_id', None)
    product_id = request.args.get('product_id', None)
    recommendations = {'CLIENT' : '', 'PRODUCT' : ''}
    if(user_id != None):
        output = pd.read_csv('output.csv', sep = ";")
        index = output[output['COD_CLIENTE']==user_id].index.values
        client_recom = output[output.index == index[0]].recommendedProducts.values[0].split('|')   
        recommendations['CLIENT'] = client_recom
        if(product_id == None):                                  
            return json.dumps(recommendations), 200
        else:
            product_id = int(product_id)
            product_recom = cart_recom.get_products_to_recommend(product_id)        
            recommendations['PRODUCT'] = product_recom
            return json.dumps(recommendations), 200
    elif(user_id == None and product_id != None):
        product_id = int(product_id)
        product_recom = cart_recom.get_products_to_recommend(product_id)
        recommendations['PRODUCT'] = product_recom
        return json.dumps(recommendations), 200        
    else:
        return jsonify({'error':'Não há como gerar recomendações sem um produto ou cliente.'}), 406


# - Lista produtos semelhantes aos recomendados para o cliente
@app.route('/recommendations/desc/<string:user_id>', methods=['GET'])
def recom_desc_user(user_id):
    output = pd.read_csv('output.csv', sep = ";")
    index = output[output['COD_CLIENTE']==user_id].index.values
    if (len(index) == 0):
        return jsonify({'error':'not found'}), 404
    else:
        recoms = description.list_recom(output, user_id)
        return recoms.to_json(), 200
    
# - Lista recomendações em que o produto aparece
@app.route('/recommendations/product/<string:product_id>', methods=['GET'])
def product_recom_summary(product_id):
    if(len(product_id) < 5):
        return jsonify({'error':'Não é um código de produto válido.'}), 404
    output = pd.read_csv('output.csv', sep = ";")
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
    output = pd.read_csv('output.csv', sep = ";")
    contain_values = output[output['recommendedProducts'].str.contains(product_id)]
    count = ("Número de recomendações desse produto:", len(contain_values.index))
    if(len(contain_values) == 0):
        return jsonify({'error':'Não há recomendações com esse produto.'}), 404
    else:
        return jsonify(count), 200
        
# - Bicluster        
@app.route('/recommendations/bicluster/<string:user_id>', methods=['GET'])
def recom_bicluster_user(user_id):
    recoms = bicluster_recom.recomenda_cliente(user_id)
    return json.dumps(recoms)
        
# - Retreina o modelo
@app.route('/retrain', methods=['GET'])
def retrain():
    status = retrain_recom.retrain_model()
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
    app.run()
