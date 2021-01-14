#!/usr/bin/env  python3.6.9
# -*- coding: utf-8 -*- 

import sys
sys.path.append(".")
from flask import Flask, jsonify, request, json, Response
import json
import pandas as pd
from Purchase import Purchase
from Recommendation import Recommendation
from Description import Description
from Scrapper import Scrapper
from CartRecom import CartRecom
from Bicluster.BiclusterRecom import BiclusterRecom
from BdManagement import BdManagement
from ClientRecom import ClientRecom

app = Flask(__name__)


add_product = Purchase()
retrain_recom = Recommendation()
description = Description()
scrap_desc = Scrapper()
cart_recom = CartRecom()
bicluster_recom = BiclusterRecom()
bd_manager = BdManagement()
client_recom = ClientRecom()

# ************************************************************* #
# *********************** MÉTODOS GET ************************* #
# ************************************************************* #

@app.route('/')
def home():
    return "Você se conectou."

# - Lista todas as recomendações
@app.route('/recommendations', methods=['GET'])
def recommendations():
    output = client_recom.recommendations()
    return output.to_json(), 200

# - Lista recomendações para um dado cliente
@app.route('/get_recommendations/', methods=['GET'])
def recom_per_user():    
    user_id = request.args.get('user_id', None)
    product_id = request.args.get('product_id', None)
    #filial_id = request.args.get('filial_id', None)
    recommendations = {'CLIENT' : None, 'PRODUCT' : None, 'error': []}
    if(user_id != None):
        print("Output recebido do BD.")
        # - Checar na recomendação do turicreate
        recom = client_recom.get_client_to_recommend(user_id)
        if(recom != None):
            recommendations['CLIENT'] = recom
            
        else: 
            # - Checar na recomendação do bicluster
            recom_bi, return_text, return_code = bicluster_recom.recomenda_cliente(user_id)
            if(recom_bi != None):
                recommendations['CLIENT'] = recom_bi
                
            else:
                #------POR ENQUANTO COMO NÃO TEM COD_FILIAL, ENTAO DEIXA ISSO AQUI COMENTADO------
                #if(filial_id != None):
                    #Fazer chamar a recomendação pra cliente novo
                    #recom_new = client_recom.recommend_to_new_client(cod_filial)
                    #if(recom_new != None):
                        #recommendations['CLIENT'] = recom_new
                        
                    #else:
                        #return app.response_class(response = jsonify({'error':'Erro inesperado encontrado, contacte o administrador.'}),
                                                             #status = 500,
                                                             #mimetype='application/json')
                #else: #------QUALQUER COISA SO TIRAR ESSE ELSE------
                    #return app.response_class(response = jsonify({'error':'Código da filial não foi informado para a requisão de novo cliente.'}),
                                                         #status = 400,
                                                         #mimetype='application/json')               

                #------POR ENQUANTO DEIXA ESSE DAQUI------
                recommendations['error'].append('Código do cliente não consta na base de vendas, tente outro.')
        # - Recomendação do produto não solicitada
        if(product_id == None):
           # - Checa se a recomendação do cliente é vazia ou não
            recommendations['error'], status = is_empty(recommendations)
            return app.response_class(response = json.dumps(recommendations),
                                    status = status,
                                    mimetype='application/json')
        # - Recomendação do produto também foi solicitada
        else:
            try:
                product_id = int(product_id)
            except:
                # - Houve erro semantico no envio no código do produto
                recommendations['error'], status = is_empty(recommendations, 
                                                            error_msg='Código do produto inválido, insira um código válido.',
                                                            code_error=406)
                return app.response_class(response = json.dumps(recommendations),
                                        status = status,
                                        mimetype='application/json')
            # - Sigo com a recomendação de produto
            product_recom = cart_recom.get_products_to_recommend(product_id)        
            if(product_recom != None):
                recommendations['PRODUCT'] = product_recom
                return app.response_class(response = json.dumps(recommendations),
                                        status = 200,
                                        mimetype='application/json')
            else:
                 # - Checa se a recomendação do cliente é vazia ou não
                recommendations['error'], status = is_empty(recommendations, 
                                                            error_msg='Código do produto não consta na base de vendas, tente outro.')
                return  app.response_class(response = json.dumps(recommendations),
                                        status = status,
                                        mimetype='application/json')               
    # - Houve solicitação de recomendação apenas para produto                                          
    elif(user_id == None and product_id != None):
        try:
            product_id = int(product_id)
        except:
            # - Houve erro semantico no envio no código do produto
            recommendations['error'].append('Código do produto inválido, insira um código válido.')
            return app.response_class(response = json.dumps(recommendations),
                                    status = 422,
                                    mimetype='application/json')
        product_recom = cart_recom.get_products_to_recommend(product_id)
        if(product_recom != None):
            recommendations['PRODUCT'] = product_recom
            return app.response_class(response = json.dumps(recommendations),
                                          status = 200,
                                          mimetype='application/json')                                              
        else:
            recommendations['error'].append('Código do produto não consta na base de vendas, tente outro.')
            return app.response_class(response = json.dumps(recommendations),
                                    status = 404,
                                    mimetype='application/json')
                                          
    else:
        recommendations['error'].append('Não há como gerar recomendações sem um produto ou cliente.')
        return app.response_class(response = json.dumps(recommendations),
                                    status = 406,
                                    mimetype='application/json')

# - Lista recomendações em que o produto aparece
@app.route('/recommendations/product/<string:product_id>', methods=['GET'])
def product_recom_summary(product_id):
    if(len(product_id) < 5):
        return jsonify({'error':'Não é um código de produto válido.'}), 404
    output = client_recom.get_clients_output()
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
    output = client_recom.get_clients_output()
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
    recom, return_text, return_code = bicluster_recom.recomenda_cliente(user_id)
    if (recom != None):
        recoms['BICLUSTER'] = recom
        return app.response_class(response = json.dumps(recoms),
                                             status = return_code,
                                             mimetype='application/json')
    else:
        return app.response_class(response = jsonify({'error': return_text}),
                                             status = return_code,
                                             mimetype='application/json')
        
# - Retreina o modelo
@app.route('/retrain', methods=['GET'])
def retrain():
    status = retrain_recom.retrain_model(bicluster_recom, cart_recom, client_recom)
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


# ************************************************************** #
# ******************** FUNÇÕES AUXILIARES ********************** #
# ************************************************************** #
def is_empty(recom_dict, error_msg = '', code_error = 404):
    """
        Função responsável por checar se a recomendação do cliente é vazia, e atualizar
        o status code e a mensagem de erro.
        Input:
            recom_dict: dicionário com as recomendações e erros
            error_msg: mensagem de erro a ser adicionada, default vazia
            code_error: código de erro a ser atualizado, default 404
        Retorno:
            recom_dict['error']: a mensagem de erro atualizada
            status: status da resposta 
    """
    status = ''
    recom_dict['error'].append(error_msg)
    if(recom_dict['CLIENT'] == None):
        status = code_error
    else:
        status = 200
    return recom_dict['error'], status



if __name__ == '__main__':
    #app.config['DEBUG'] = True
    app.run()
