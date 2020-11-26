#include <stdio.h>
#include <string>
#include <fstream>
#include <sstream>
#include <iostream>
#include <math.h>
#include <algorithm>
#include <set>

#include "FileBigraph.h"
#include "Biclusterizer.h"

using namespace std;


Biclusterizer *FileBigraph::loadFile(char *fileName)
{
   std::ifstream Instancia;
   Instancia.open(fileName);

   if (!Instancia) {
      printf("Arquivo %s nao pode ser aberto\n", fileName);
      return NULL;
   }

   int V, U;
   Instancia >> V;
   Instancia >> U;
   
   printf("ORI V: %d \n", V);
   printf("ORI U: %d \n", U);

   //Lista de Adjacencia original
   vector<vector<int>> laV(V);
   vector<vector<int>> laU(U);
   
   std::string line;
   std::getline(Instancia, line);//Limpando o \n da leitura anterior
   int u;

   
   for (int v = 0; v < V; ++v) 
   {
      vector<int> &nv = laV[v];
      std::getline(Instancia, line);
      std::stringstream is(line);
      while (is >> u)
      {
	 //if(u >= Bigraph::U)
	    //printf("%d ", u);
	 nv.push_back(u);
	 laU[u].push_back(v);

      }
   }
   Instancia.close();
   
   //Criando os mapas de vertices originais que foram removidos  
   /*vector<int> mapV(V, -1);
   vector<int> mapInvV;
   vector<int> mapU(U, -1);
   vector<int> mapInvU;
   int numV = 0;
   int numU = 0;*/
   

   vector<bool> isFiltredV(V, false);
   vector<bool> isFiltredU(U, false);
   //Criando o grafo filtrada
   Biclusterizer *bcb = new Biclusterizer(V, U);
   printf("V: %d \n", bcb->V);
   printf("U: %d \n", bcb->U);

   for(int v=0; v < V; ++v)
   {
      if(laV[v].size() <= 1)
	 isFiltredV[v] = true;
   }
   
   for(int u=0; u < U; ++u)
   {
      if(laU[u].size() > 200)
      {
	 isFiltredU[u] = true;
	 bcb->outliersProducts.push_back(std::make_pair(u, laU[u]));
      }
      
      if(laU[u].size() <= 1)
	 isFiltredU[u] = true;
   }

   //Filtrando a LA de entrada
   for(int v=0; v<bcb->V; ++v)
   {
      if(!isFiltredV[v])
      {
	 for(int u : laV[v])
	 {
	    if(!isFiltredU[u])
	    {
	       bcb->laV[v].push_back(u);
	       bcb->laU[u].push_back(v);
	    }
	 }
      }
   }

   return bcb;
}
