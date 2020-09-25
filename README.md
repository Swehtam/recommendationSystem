## IMPORTANTE
- Os códigos de teste constam no Jupyter Notebook (arquivo .ipynb)
- A API consta no diretório API. :smile:


## API 
| Tipo | Endpoint                                       |                          Descrição                           | Método                |
| ---- | ---------------------------------------------- | :----------------------------------------------------------: | --------------------- |
| GET  | /recommendations                               |           Lista todas as recomendações por cliente           | recommendations       |
| GET  | /recommendations/<string:'user_id'>            |      Lista as recomendações para um determinado cliente      | recom_per_user        |
| GET  | /recommendations/desc/<string:'user_id'>       | Lista 10 das recomendações para o cliente, e para cada produto recomendado, lista 3 produtos de descrição similar | recom_desc_user       |
| GET  | /recommendations/count/<string:'product_id'>   | Informa a quantidade de recomendações feitas com esse produto. | product_recom_count   |
| GET  | /recommendations/product/<string:'product_id'> |    Lista as recomendações contendo um determinado produto    | product_recom_summary |
| POST | /purchase/add                                  |   Adiciona uma nova instância de compra na base de treino    | add_purchase          |
| POST | /update                                        |    Adiciona novo produto na base com todas as descrições     | add_new_product       |
| GET  | /retrain                                       | Retreina as recomendações, gerando um novo output de recomendações | retrain               |
| GET  | /                                              |        Default: retorna a mensagem "Você se conectou"        | home                  |

## Inputs e Outputs

- Exemplo input de dados (/purchase/add)

  ```json
  [{
  "COD_CLIENTE" : "123456",
  "COD_PRODUTO" : "123456",
  "QUANTIDADE" : "1"
  }]
  ```

- Exemplo input de dados (/update)

  ```json
  [{
  "COD_PRODUTO" : "25172",
  "NOME_PRODUTO" : "SMARTPHONE LG K9 TV LM-X210BMW PRETO"
  }]
  ```

- Exemplo output de dados 

  Recomendações para o cliente de código 000021

  ```json
  {
  	"COD_CLIENTE":{"0":"000021"},
  	"recommendedProducts": {"0":"26460|26588|24526|15558|26432|22086|25598|25703|19729|25436"}
  }
  ```