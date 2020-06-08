## Glossário

Para melhor compreensão das atividades desenvolvidas, faz-se necessário o entendimento de termos que são utilizados durante as descrições dos algoritmos.

1.  **Root Mean Squared Errors (RMSE)**
    É a raíz do erro quadrático médio, onde esse erro é a distância entre os valores obtidos e os valores esperados. Quanto menor o RMSE, melhor é a recomendação.

2.  **Recall**
    Nos algoritmos utilizados, é o percentual de produtos que um cliente comprou que foram, de fato, recomendados.

3.  **Precision**
    Nos algoritmos utilizados, representa quantos itens o cliente comprou dos recomendados.

4.  **Filtro Colaborativo**
    Filtro que recomenda itens baseado na semelhança entre compras de usuários.

## Bibliotecas 
```
import pandas as pd
import numpy as np
import turicreate as tc
from sklearn.model\_selection import train\_test\_split
```
## Algoritmos

1.  **Content-Based**
    Essa abordagem consiste no cálculo da correlação entre produtos, utilizando o nome do produto e a quantidade de compras do mesmo como fatores de peso para sugestão de itens entendidos pelo sistema como \"semelhantes\".
    Para o desenvolvimento desse sistema, houve primeiro uma \"limpeza\" na base de dados. As colunas irrelevantes para o algoritmo foram apagadas, a tabela utilizada contou então com as colunas:
    -   COD\_CLIENTE

    -   NOME\_PRODUTO

    -   CLASSIFICACAO

    -   QUANTIDADE

- Depois foi criada uma matriz para que a correlação entre os produtos pudesse ser calculada. A matriz era da forma:

  **NOME\_PRODUTO** como coluna, **COD\_CLIENTE** como linha, e **QUANTIDADE** como interseção.

  Com a matriz pronta, o sistema foi enfim montado, de forma que as recomendações foram feitas da seguinte forma:

  -   Cálculo da correlação de um produto com os demais utilizando a função **corrwith()**;

  -   Criação de uma tabela para guardar os produtos e suas correlações com os demais;

  -   Junção (**merge**) da base de dados original com a base contendo as correlações;

  -   Ordenar por correlação e filtrar produtos populares (quantidade de vendas maior do que um número n)

  -   Dado um nome de produto, retornar n produtos com melhor correlação.
```
 def get_cor_similar(product_name):
	    similar = matrix.corrwith(matrix[product_name])
	    corr_similar = pd.DataFrame(similar, columns=['correlation'])
	    corr_similar.dropna(inplace=True)
	    
	    return corr_similar

	def get_cor_product(corr_similar, original):
	    cor_with_product = pd.merge(left = corr_similar,
	                               right = original,
	                               on='NOME_PRODUTO')[['NOME_PRODUTO', 'correlation',
	                                             'QUANTIDADE']]
	    
	    cor_with_product.drop_duplicates().reset_index(drop=True)
	    
	    return cor_with_product

	def get_similar_products(cor_with_product, purchase_freq_filter = 5, n_recom = 10):
	       
	    result = cor_with_product[cor_with_product['QUANTIDADE'] 
	                              > purchase_freq_filter].drop_duplicates().sort_values(by='correlation', ascending = False)
	    return result.head(n_recom)
```
2.  **Purchase-Based**
    Essa abordagem usou dois conceitos para recomendação, o primeiro foi de popularidade, onde depois de um treino em cima da base de dados fornecida, os itens mais populares da base eram recomendados, o segundo usou a abstração de um filtro colaborativo para calcular a semelhança de compras entre os clientes.
    Assim como o algoritmo anterior, também foi realizada uma limpeza na base, mas também fora adicionada uma coluna nova indicando compra ou não compra (**variável dummy de compra**) de um produto, a base então ficou com as colunas:
    -   COD\_CLIENTE

    -   COD\_PRODUTO

    -   QUANTIDADE

    -   PURCHASE\_DUMMY

- Graças a existência da coluna dummy, foi realizada a **normalização da frequência de compra de cada item por cada usuário**.\
  Depois a base de dados foi dividida em **treino e teste** numa proporção de respectivamente **80:20**.
  A partir daí o sistema foi construído, o algoritmo base foi o de popularidade de itens, uma função **model** foi criada com auxilio da biblioteca **turicreate**.
```
  # Function for all models using turicreate
	def model(train_data, name, user_id, item_id, target, 
	          users_to_recommend, n_rec, n_display):
	    if name == 'popularity':
	        model = tc.popularity_recommender.create(train_data, 
	                                                    user_id = user_id, 
	                                                    item_id = item_id,
	                                                    target = target)
	    elif name == 'cosine':
	        model = tc.item_similarity_recommender.create(train_data, 
	                                                    user_id=user_id, 
	                                                    item_id=item_id, 
	                                                    target=target, 
	                                                    similarity_type='cosine')
	    elif name == 'pearson':
	        model = tc.item_similarity_recommender.create(train_data, 
	                                                    user_id=user_id, 
	                                                    item_id=item_id, 
	                                                    target=target, 
	                                                    similarity_type='pearson')
	        
	    recom = model.recommend(users=users_to_recommend, k=n_rec)
	    recom.print_rows(n_display)
	    return model
```
