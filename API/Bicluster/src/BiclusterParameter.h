#ifndef BCLUPARAM_H
#define BCLUPARAM_H

class BiclusterParameter
{
   public:
      //Indica a quantidade mínima de compras associadas a um cliente ou produto 
      //para que o mesmo seja considerado na hipotese
      static int MIN_BUY;

      //Quantidade máxima de compras que um produto obteve para ser condiderado outiliear
      //passando deste valor sua hipotese é tratada após a biclusterizacao 
      static int OUTLIER_PRODUCT;
      
      //os produtos outliers não são utilizando durante o proceso de biclusterização 
      //(torna as componentes muto conexas gerando complexidade computacional)
      //Cada produto outilier é adicionada as bicliques cuja a interceção de clientes da biclique e que 
      //compraram o outilier seja maior que a porcentagem OUTLIER_PORC_CLIENTS de clientes da biclique
      static float OUTLIER_PORC_CLIENTS;
      
      //Tamanho mínimo da componente para não realizar quebra.
      //Toda componente do grafo bipartido que tiver uma de suas dimensoes abaixo deste valor
      //se torna uma biclique na hipotese de recomendação.
      static int MIN_SHAPE_COMPONENT;
      
      //Distância máxima que todos os vértices de cada componente deve ter a partir de seu vértice inicial
      //durante o processo de divisão das grande componenetes.
      //Cada subcomponenete será biclusterizada pelo otimizador.
      static int MAX_DIST_COMPONENT;
      
      //Número iterações que a metaheuristica de biclusterização aplica sobre cada componente.
      static int NUM_ITER_METAHEURISTIC;
      
      //Números de execuções da meta-heurística. 
      //A hipotese é formada pela melhor bilcusterizacao entre todas as execuções
      static int NUM_EXEC_METAHEURISTIC;
      
};

#endif

