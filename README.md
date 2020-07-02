## IMPORTANTE
- Os códigos de teste constam no Jupyter Notebook (arquivo .ipynb)
- A API consta no diretório API. :smile:

## TO-DO 
- [x] Avaliação dos modelos 
- [x] Escolha do modelo final
- [x] Comparação de outputs com o site
- [x] Ataptação do código para API 

> **OBS.:** A API ainda precisa ter seu método de adição de novas compras generalizada para n adições. E também precisa apresentar freq de recomemdação por produto e indicar suas instâncias de recomendações.

## API 
| endpoint                            |                          descrição                           | Método          |
| ----------------------------------- | :----------------------------------------------------------: | --------------- |
| /recommendations                    |           Lista todas as recomendações por cliente           | recommendations |
| /recommendations/<string:'user_id'> |      Lista as recomendações para um determinado cliente      | recom_per_user  |
| /purchase/add                       | Adiciona uma nova instância de compra na BD e retreina as recomendações, gerando um novo output de recomendações | add_purchase    |

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

## Modelo Escolhido 
- Purchase-Based rankeando itens por similaridade baseado na quantidade de compras por usuário.

