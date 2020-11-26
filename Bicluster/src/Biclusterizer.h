#ifndef BCB_H
#define BCB_H

#include <utility> 
#include <vector>
#include "Solution.h"

using namespace std;

struct Biclusterizer
{
   int V;
   int U;


   //Produto final da biclusterização
   vector<Biclique *> bicliques;

   //Lista de adjacencia original
   vector<vector<int>> laV;
   vector<vector<int>> laU;

   Biclusterizer(int v, int u) : 
      V(v), U(u), laV(V), laU(U), isCompV(V, false), 
      mapV(V, -1), mapU(U, -1), isSingletonV(V, true), isSingletonU(U, true)
   {}


   //Produtos com comprados em excesso
   //pair - first : identificador do produto - second : lista de seus clientes originais
   vector<pair<int, vector<int>>> outliersProducts;

   //Controla os clientes que já estão em pelo menos uma componente
   vector<bool> isCompV;

   //Indica se o vertice é singleton na solução final
   vector<bool> isSingletonV;
   vector<bool> isSingletonU;
   
   //Mapeia o vértice original no seu indice no otimizador
   vector<int> mapV;
   vector<int> mapU;

   //Identifica as componenetes desconexas e biclusteriza cada uma
   //Se a componenete for grande, separa a mesma com a distancia 3.
   void start();
   
   //Separa a componente em elementos a uma distancia 'dist'
   void divide(vector<int> &oriV, vector<int> &oriU, int dist=3);
   
   //Chama o otimizador sobre a Bicomponent e biclusteriza
   void optBicluster(vector<int> &compV, vector<int> &compU);

   //Adiciona os produtos ouliers no bliques com metade dos seus clientes
   void addOutliers();

   //Retorna a string contendo a hipotese de biclusterização
   std::string getHypothesis();
};

#endif
