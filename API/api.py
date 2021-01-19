#!/usr/bin/env  python3.6.9
# -*- coding: utf-8 -*- 

import sys
sys.path.append(".")
from flask import Flask, jsonify, request, json, Response
import json
import pandas as pd
from Recommendation import Recommendation
from Description import Description
from CartRecom import CartRecom
from Bicluster.BiclusterRecom import BiclusterRecom
from BdManagement import BdManagement
from ClientRecom import ClientRecom

app = Flask(__name__)

retrain_recom = Recommendation()
description = Description()
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
    filial_id = request.args.get('filial_id', None)
    recommendations = {'CLIENT' : None, 'PRODUCT' : None, 'error': []}
    status = None
    if(user_id != None):
        print("Output recebido do BD.")
        # - Checar na recomendação do turicreate
        recom = client_recom.get_client_to_recommend(user_id)
        if(recom != None):
            recommendations['CLIENT'] = recom
            status = 200
            
        else: 
            # - Checar na recomendação do bicluster
            recom_bi, return_text, return_code = bicluster_recom.recomenda_cliente(user_id)
            if(recom_bi != None):
                recommendations['CLIENT'] = recom_bi
                status = 200
                
            else:
                #------POR ENQUANTO COMO NÃO TEM COD_FILIAL, ENTAO DEIXA ISSO AQUI COMENTADO------
                if(filial_id != None):
                    filial_erro = False
                    try:
                        filial_id = int(filial_id)
                    except:
                        # - Houve erro semantico no envio no código do produto
                        recommendations['error'].append('Codigo de filial invalido, insira um codigo valido.')
                        status = 406
                        filial_erro = True
                                    
                    if(not filial_erro):
                        #Fazer chamar a recomendação pra cliente novo
                        recom_new = client_recom.recommend_to_new_client(filial_id)
                        if(recom_new != None):
                            recommendations['CLIENT'] = recom_new
                            status = 200
                            
                        else:
                            recommendations['error'].append('Codigo de filial nao consta na base de vendas, tente outro.')
                            status = 500       
                        
                else: #------QUALQUER COISA SO TIRAR ESSE ELSE------
                    recommendations['error'].append('Codigo da filial nao foi informado para a requisao de novo cliente.')
                    status = 400

                #------POR ENQUANTO DEIXA ESSE DAQUI------
                #recommendations['error'].append('Código do cliente não consta na base de vendas, tente outro.')
        # - Recomendação do produto não solicitada
        if(product_id == None):
           # - Checa se a recomendação do cliente é vazia ou não
            recommendations['error'], status = is_empty(recommendations, code_error = status)
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
                                                            error_msg='Codigo do produto invalido, insira um codigo valido.',
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
                                                            error_msg='Codigo do produto nao consta na base de vendas, tente outro.',
                                                            code_error=status)
                return  app.response_class(response = json.dumps(recommendations),
                                        status = status,
                                        mimetype='application/json')               
    # - Houve solicitação de recomendação apenas para produto                                          
    elif(user_id == None and product_id != None):
        try:
            product_id = int(product_id)
        except:
            # - Houve erro semantico no envio no código do produto
            recommendations['error'].append('Codigo do produto invalido, insira um codigo valido.')
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
            recommendations['error'].append('Codigo do produto nao consta na base de vendas, tente outro.')
            return app.response_class(response = json.dumps(recommendations),
                                    status = 404,
                                    mimetype='application/json')
                                          
    else:
        recommendations['error'].append('Nao ha como gerar recomendaçoes sem um produto ou cliente.')
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
