#!/usr/bin/env  python3.6.9
# -*- coding: utf-8 -*- 
import psycopg2
import os
import pandas as pd
from sqlalchemy import create_engine
import io

class BdManagement:

    # - INFORMAÇÕES BANCO DE DADOS
    POSTGRES = {
        'user': os.environ.get('DATABASE_USER', None),
        'password': os.environ.get('DATABASE_PASS', None),
        'database': os.environ.get('DATABASE_NAME', None),
        'host': os.environ.get('DATABASE_HOST', None),
        'port': os.environ.get('DATABASE_PORT', None),
    }

    def connect(self, params_dic = POSTGRES):
        """ Conecta com o servidor do postgres """
        conn = None
        try:
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params_dic)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return
        print("Connection successful")
        return conn

    def getOutputRecom(self):
        """ Retorna a tabela de recomendação de clientes do banco """
        conn = self.connect()
        query = """SELECT "COD_CLIENTE", "recommendedProducts" FROM output_recom;"""
        output = None
        cursor = conn.cursor()
        try:
            output = pd.read_sql(query, conn)
        except psycopg2.Error as e:
            cursor.execute("rollback;")
            print(e)
        finally:
            conn.close()
            
        return output
       
    def getSalesTable(self):
        """ Retorna a tabela de vendas do banco """
        conn = self.connect()
        query = """SELECT "COD_FILIAL", 
                            "ORCAMENTO",
                            "HORA",	
                            "COD_CLIENTE",
                            "SEXO",	
                            "IDADE",
                            "COD_PRODUTO", 
                            "NOME_PRODUTO",
                            "CLASSIFICACAO",
                            "QUANTIDADE",
                            "CANAL" FROM vendas;"""
        data_armz = None
        cursor = conn.cursor()
        try:
            data_armz = pd.read_sql(query, conn)
        except psycopg2.Error as e:
            cursor.execute("rollback;")
            print(e)
        finally:
            conn.close()
            
        return data_armz

    def getProductsTable(self):
        """ Retorna a tabela de produtos do banco """
        conn = self.connect()
        query = """SELECT "NOME_PRODUTO",
                            "COD_PRODUTO",
                            "DESCRIPTION" FROM produtos;"""
        data_products = None
        cursor = conn.cursor()
        try:
            data_products = pd.read_sql(query, conn)
        except psycopg2.Error as e:
            cursor.execute("rollback;")
            print(e)
        finally:
            conn.close()
            
        return data_products

    def getClientRecomTable(self):
        """ Retorna as colunas necessárias da tabela de vendas do banco para 
            a recomendação utilizando TuriCreate
        """
        conn = self.connect()
        query = """SELECT "COD_CLIENTE","COD_PRODUTO","QUANTIDADE" FROM vendas;"""
        data_recom = None
        cursor = conn.cursor()
        try:
            data_recom = pd.read_sql(query, conn)
        except psycopg2.Error as e:
            cursor.execute("rollback;")
            print(e)
        finally:
            conn.close()
            
        return data_recom

    def updateProductTable(self, df_products):
        """ Dropa a tabela de produtos e depois atualiza com as novas informações de produtos obtidas. """
        conn = self.connect()
        query_drop = """DROP TABLE IF EXISTS produtos;"""
        cursor = conn.cursor()

        # - Drop na tabela
        try:
            cursor.execute(query_drop)
            cursor.commit()

            # - Update na tabela
            try:
                engine = create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(self.POSTGRES['user'], self.POSTGRES['password'],
                                                                                     self.POSTGRES['host'], self.POSTGRES['port'],
                                                                                     self.POSTGRES['database']))
                df_products.head(0).to_sql('produtos', engine, if_exists='replace',index=False) #truncates the table
                raw_conn = engine.raw_connection()
                cur = raw_conn.cursor()
                output = io.StringIO()
                df_products.to_csv(output, sep='\t', header=False, index=False)
                output.seek(0)
                #contents = output.getvalue() # - advindo do código base, inutil pra nós
                cur.copy_from(output, 'produtos', null="") # null values become ''
                raw_conn.commit()
            except psycopg2.Error as e:
                cursor.execute("rollback;")
                print(e)
            finally:
                raw_conn.close()

        except psycopg2.Error as e:
            cursor.execute("rollback;")
            print(e)
        finally:
            conn.close()

    def updateRecomTable(self, df_output):
        """ Dropa a tabela de recomendações e depois atualiza com as novas informações de recomendações para clientes obtidas. """
        conn = self.connect()
        query_drop = """DROP TABLE IF EXISTS output_recom;"""
        cursor = conn.cursor()

        # - Drop na tabela
        try:
            cursor.execute(query_drop)
            cursor.commit()

            # - Update na tabela
            try:
                engine = create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(self.POSTGRES['user'], self.POSTGRES['password'],
                                                                                     self.POSTGRES['host'], self.POSTGRES['port'],
                                                                                     self.POSTGRES['database']))
                df_output.head(0).to_sql('output_recom', engine, if_exists='replace',index=False) #truncates the table
                raw_conn = engine.raw_connection()
                cur = raw_conn.cursor()
                output = io.StringIO()
                df_output.to_csv(output, sep='\t', header=False, index=False)
                output.seek(0)
                #contents = output.getvalue() # - advindo do código base, inutil pra nós
                cur.copy_from(output, 'output_recom', null="") # null values become ''
                raw_conn.commit()
            except psycopg2.Error as e:
                cursor.execute("rollback;")
                print(e)
            finally:
                raw_conn.close()

        except psycopg2.Error as e:
            cursor.execute("rollback;")
            print(e)
        finally:
            conn.close()