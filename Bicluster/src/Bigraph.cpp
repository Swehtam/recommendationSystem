#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fstream>
#include<sstream>
#include <iostream>
#include <algorithm>
#include <limits.h>
#include "Bigraph.h"
#include "Edge.h"


Bigraph::Bigraph(int v, int u) 
	: V(v), U(u), laV(v), laU(u)//, laV2(v), laU2(u)
{
   this->w = new int*[V];
   for(int i = 0; i < V; ++i)
   {
      this->w[i] = new int[U];
      memset(this->w[i], -1, sizeof(int)*U);
   }
}

void Bigraph::init()
{
   //this->createN2();
   this->initCandidates();
}

void Bigraph::initCandidates()
{
   //iniciando a lista de candidatos
   for(int v=0 ; v < V; ++v)
   {
      for(int u : laV[v])
      {
	 int g = Bigraph::g_n1(v,u);
	 candidatos.push_back(Edge(v,u,g));
      }
   }
   candidatos.sort(Edge::compare);
}

void Bigraph::createN1()
{
   for (int i = 0; i < V; i++)
      for (int j = 0; j < U; j++)
	 if(w[i][j] > 0)
	 {
	    laV[i].push_back(j);
	    laU[j].push_back(i);

	 }
}

/*void Bigraph::createN2()
{
   for(int i=0 ; i < V; ++i)
      if(!laV[i].empty())
	 for(int u : laV[i])
	    for(int  v : laU[u])
	       laV2[i].insert(v);

   for(int j=0 ; j < U; ++j)
      if(!laU[j].empty())
	 for(int v : laU[j])
	    for(int u : laV[v])
	       laU2[j].insert(u);
}*/

Bigraph::~Bigraph()
{
   for(int i = 0; i < V; ++i)
      delete this->w[i];
   delete this->w;
}

float Bigraph::g_n1(int i, int j)
{
   list<int> &N1i = this->laV[i];
   list<int> &N1j = this->laU[j];

   //Custo da ligacao de i com j
   int *wi = this->w[i]; 
   int cij = wi[j];
   //soma das ligacoes entre os elementos de N1(i) com os elementos N1(j) 
   int inij = 0;
   //soma das ligacoes dos elementos de N1(i) e N1(j) que n se ligam entre si
   int outij = 0;
   //Soma das ligacoes que faltam entre N1(i) e N1(j) para fechar o bicluster.
   int diffij = 0;

   //////////////////////////////
   //computa in e diff
   for(int v : N1j)
   { //itera em N1(j)
      int *wv = this->w[v];
      for(int u : N1i)
      { //itera em N1(i)
	 if(wv[u]>0)
	    inij += wv[u];
	 else diffij += wv[u];
      }
   }
   //////////////////////////////

   //////////////////////////////	
   //calcula outij

   //soma dos pesos das arestas que comecam N1(j) e não terminam em N1(i)
   for(int v : N1j)
   {
      int *wv = this->w[v];
      //vizinhos do elemento *itNj, que esta em N1(j). Esses vizinhos devem estar em N1(i)
      for(int u : N1i)
      {
	 if(wi[u] < 0)
	    outij += wv[u];
      }
   }

   //soma dos pesos das arestas que comecam N1(i) e não terminam em N1(j)
   for(int v : N1j)
   { 
      int *wv = this->w[v];
      //vizinhos do elemento *itNj, que esta em N1(j). Esses vizinhos devem estar em N1(i)
      for(int u : N1i)
      {
	 if(wv[j] < 0)
	    outij += wv[u];
      }
   }	
   //////////////////////////////

   return inij + cij +  diffij - outij;
}

/*float Bigraph::g_n2(int i, int j)
{
   set<int> N2i = this->laV2[i];
   set<int> N2j = this->laU2[j];
   //Custo da ligacao de i com j
   int *wi = this->w[i];
   int cij = wi[j];
   //soma das ligacoes entre os elementos de N2(i) com os elementos N2(j) 
   int inij = 0;
   //soma das ligacoes dos elementos de N2(i) e N2(j) que n se ligam entre si
   int outij = 0;
   //Soma das ligacoes que faltam entre N2(i) e N2(j) para fechar o bicluster.
   int diffij = 0;


   //Ligacoes fora de N2(j)
   for(int  u : this->laV[i])
   {
      if(std::find(N2j.begin(), N2j.end(), u) == N2j.end())
	 outij += wi[u];
   }

   //Calcula os pesos das ligacoes entre o i e N2(j)
   for(int u : N2j)
   {
      if(wi[u] > 0)
	 inij += wi[u];
      else
	 diffij += wi[u];
   }

   for(int v : this->laU[j])
   {
      if(std::find(N2i.begin(), N2i.end(), v) == N2i.end())
	 outij += this->w[v][j];
   }

   //Calcula os pesos das ligacoes entre o j e N2(i)
   for(int v : N2i)
   {
      if(this->w[v][j] > 0)
	 inij += this->w[v][j];
      else
	 diffij += this->w[v][j];
   }

   return inij + cij +  diffij - outij;
}*/


const int Bigraph::FORBIDDEN = -1;
const int Bigraph::FREE = 0;
const int Bigraph::PERMANENT = 1;
const int Bigraph::N2_N2 = 1;
const int Bigraph::N2_N1 = 2;
const int Bigraph::N1_N1 = 3;
int Bigraph::constr_type = 3;


