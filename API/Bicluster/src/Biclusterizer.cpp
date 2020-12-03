#include "Bicluster.h"
#include "BiclusterParameter.h"
#include "Biclusterizer.h"
#include "GRASP.h"
#include <queue>
#include <stdio.h>
#include <iostream>

using namespace std;
      
int BiclusterParameter::MIN_BUY = 2;
int BiclusterParameter::OUTLIER_PRODUCT = 200;
float BiclusterParameter::OUTLIER_PORC_CLIENTS = 0.25;
int BiclusterParameter::MIN_SHAPE_COMPONENT = 2;
int BiclusterParameter::MAX_DIST_COMPONENT = 3;
int BiclusterParameter::NUM_ITER_METAHEURISTIC = 30;
int BiclusterParameter::NUM_EXEC_METAHEURISTIC = 2;
   
void Biclusterizer::addOutliers()
{
   for(pair<int, vector<int>> &product : this->outliersProducts)
   {
      vector<bool>isClient(this->V, false);
      for(int v : product.second) //product.second possui a lista de cliente que compram este produto considerado outlier
      {
	 isClient[v] = true;
      }

      //Contabiliza quantos clientes do produto outlier estão na biclique (numClients)
      //Se numClients for maior que a porcentagem OUTLIER_PORC_CLIENTS dos clientes desta biclique 
      //então adiciona o outlier na biclique
      for(Biclique *bc : this->bicliques)
      {
	 if(bc->V.size() < 2)
	    continue;
	 int numClients = 0;
	 for(int v : bc->V)
	 {
	    if(isClient[v])
	       ++numClients;
	 }
	 if(numClients > (bc->V.size() * BiclusterParameter::OUTLIER_PORC_CLIENTS))
	 {
	    //printf("Biclique: %d - V: %d - Cli: %d\n", product.first, bc->V.size(), numClients);
	    bc->U.push_back(product.first);
	    this->isSingletonU[product.first] = false;
	 }
      }
   }

}

void Biclusterizer::optBicluster(vector<int> &compV, vector<int> &compU)
{
	 //printf("V - %d \n", compV.size());
	 //printf("U - %d \n", compU.size());

   vector<int> mapInvV;
   vector<int> mapInvU;
   int numV = 0;
   int numU = 0;
   //Mapeando os vertices reais com os vertices do otimizador
   for(int v : compV)
   {	
      this->mapV[v] = numV++;
      mapInvV.push_back(v);
   }
   for(int u : compU)
   {	
      this->mapU[u] = numU++;
      mapInvU.push_back(u);
   }
   //Construindo o Bigraph
   Bigraph bg(numV, numU);
   for(int vOri : compV)
   {
      int v = this->mapV[vOri];
      //printf("Vori: %d V: %d - ", vOri, v);
      for(int uOri : laV[vOri])
      {
	 int u = mapU[uOri];
	 if(u >= 0)
	 {
	    //printf("%d ", uOri);
	    bg.laV[v].push_back(u);
	    bg.laU[u].push_back(v);
	    bg.w[v][u] = 1;
	 }//else
	    //printf("%dX ", uOri);
      }
      //printf("\n");
   }
   bg.init();

   //Executando o otimizador
   Solution *sol = execute_metaheuristic(&bg, 
	 				 BiclusterParameter::NUM_EXEC_METAHEURISTIC,
	 				 BiclusterParameter::NUM_ITER_METAHEURISTIC);

   //cout << sol->getText() << endl << endl;

   //Adicionando biclusters não singleton
   for(Bicluster *bclu : sol->C)
   {
      //if(bclu->U.size() < 5)
	 //printf("IIIIIIIIIIIIIIIOOOOOOOOOOOOOOOOOOOOOOOOOO");
      if((bclu->V.size() > 0) && (bclu->U.size() > 0))
      {
	 //Mapeando os bicluster e depois adicionando o biclique no conjunto final
	 for(int &vopt : bclu->V)
	 {
	    vopt = mapInvV[vopt];
	    this->isSingletonV[vopt] = false;
	 }

	 for(int &uopt : bclu->U)
	 {
	    uopt = mapInvU[uopt];
	    this->isSingletonU[uopt] = false;
	 }

	 this->bicliques.push_back(bclu->getBiclique());
      }
   }
   //cout << sol->getText() << endl;
   
   delete sol;
   
   //Limpando o mapV e mapU
   for(int v : compV)
      this->mapV[v] = -1;
   for(int u : compU)
      this->mapU[u] = -1;
}

void Biclusterizer::divide(vector<int> &oriV, vector<int> &oriU, int dist)
{
   queue<int> qV;
   queue<int> qU;
   //Iniciando as visitas pela parte V
   for(int i : oriV)
   {
      if(!isCompV[i])
      {
	 //printf("Comp: %d\n", i);
	 vector<bool> isVisitedV(V, false);
	 vector<bool> isVisitedU(U, false);
	 
	 vector<int> compV;
	 vector<int> compU;

	 isCompV[i] = true;
	 qV.push(i);

	 for(int d=0; d < dist; d+=2) //Até distancia 5
	 {
	    while(!qV.empty())
	    {
	       int v = qV.front();
	       compV.push_back(v);
	       qV.pop();
	       for(int u : laV[v])
	       {
		  if(!isVisitedU[u])
		  {
		     qU.push(u);
		     isVisitedU[u] = true;
		  }
	       }
	    }

	    while(!qU.empty())
	    {
	       int u = qU.front();
	       compU.push_back(u);
	       qU.pop();
	       for(int v : laU[u])
	       {
		  if(!isVisitedV[v])
		  {
		     qV.push(v);
		     isCompV[v] = true;
		     isVisitedV[v] = true;
		  }
	       }
	    }
	    if(qV.empty())
	       break;
	 }
	 //Descarta singleton
	 if((compV.empty()) || (compU.empty()))
	    continue;
	 //printf("Comp: %d\n", i);
	 this->optBicluster(compV, compU);

      }//FIM IF
   }
}

void Biclusterizer::start()
{
   vector<bool> visitV(V, false);
   vector<bool> visitU(U, false);
   
   queue<int> qV;
   queue<int> qU;

   //Iniciando as visitas pela parte V
   for(int i = 0; i < V; ++i)
   {
      if((!laV[i].empty()) && (!visitV[i]))
      {
	 //printf("Comp: %d\n", i);
	 vector<int> compV;
	 vector<int> compU;

	 visitV[i] = true;
	 qV.push(i);

	 while(true)
	 {
	    while(!qV.empty())
	    {
	       int v = qV.front();
	       compV.push_back(v);
	       qV.pop();
	       for(int u : laV[v])
	       {
		  if(!visitU[u])
		  {
		     visitU[u] = true;
		     qU.push(u);
		  }
	       }
	    }

	    while(!qU.empty())
	    {
	       int u = qU.front();
	       compU.push_back(u);
	       qU.pop();
	       for(int v : laU[u])
	       {
		  if(!visitV[v])
		  {
		     visitV[v] = true;
		     qV.push(v);
		  }
	       }
	    }
	    if(qV.empty())
	       break;
	 }

	 if(compV.size() > BiclusterParameter::MIN_SHAPE_COMPONENT && compU.size() > BiclusterParameter::MIN_SHAPE_COMPONENT)
	    this->divide(compV, compU, BiclusterParameter::MAX_DIST_COMPONENT);
	 else
	 {
	    Biclique *bc = new Biclique();
	    for(int v : compV)
	    {
	       isSingletonV[v] = false;
	       bc->V.push_back(v);
	    }
	    for(int u : compU)
	    {
	       isSingletonU[u] = false;
	       bc->U.push_back(u);
	    }

	    this->bicliques.push_back(bc);
	 }
      }//FIM IF
   }

   this->addOutliers();
}

std::string Biclusterizer::getHypothesis()
{

   std::string bgStr = "{";

   for(unsigned int idOri = 0; idOri < this->bicliques.size(); ++idOri)
   {
      bgStr+="[";
      Biclique &ori = *this->bicliques[idOri];
      bgStr += ori.getText();
      if(idOri < this->bicliques.size()-1)
	 bgStr += "],";
      else
	 bgStr += "]";
   }

   //Imprime os singletons
   char v[100];
   bgStr+="},{(";
   vector<int> aux;
   for(int i = 0; i < V; ++i)
      if(this->isSingletonV[i])
	 aux.push_back(i);
   for(int i = 0; i < aux.size(); ++i)
   {
      if(i < aux.size() - 1)
	 sprintf(v, "%d,", aux[i]);
      else
	 sprintf(v, "%d", aux[i]);
      bgStr += v;
   }
   aux.clear();

   bgStr += "),(";
   
   for(int i = 0; i < U; ++i)
      if(this->isSingletonU[i])
	 aux.push_back(i);
   for(int i = 0; i < aux.size(); ++i)
   {
      if(i < aux.size() - 1)
	 sprintf(v, "%d,", aux[i]);
      else
	 sprintf(v, "%d", aux[i]);
      bgStr += v;
   }
   
   bgStr+=")}";

   return bgStr;
}

