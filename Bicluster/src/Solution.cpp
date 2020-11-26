#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <limits.h>
#include "Solution.h"
#include "Bigraph.h"
#include "Bicluster.h"

Solution::Solution(Bigraph *b) : ev(0), e0(0), edit(0)
{
   this->bg = b;
   this->edges = new int*[bg->V];
   for(int i=0; i < bg->V; ++i){
      this->edges[i] = new int[bg->U];
      memset(this->edges[i], Bigraph::FORBIDDEN, sizeof(int)*bg->U);
   }
}

Solution::Solution(Solution &b) : 
   ev(b.ev), e0(b.e0), edit(b.edit), bg(b.bg)   
{    
   this->edges = new int*[bg->V];
   for(int i=0; i < bg->V; ++i){
      this->edges[i] = new int[bg->U];
      memcpy(this->edges[i], b.edges[i], sizeof(int)*bg->U);
   }

   for(Bicluster *iB : b.C){
      this->C.push_back(new Bicluster(*iB));
   }
}

unsigned int Solution::f(bool updateDIFF)
{
   this->e0 = 0;
   this->ev = 0;
   this->edit = 0;

   //Zerando DIFF
   if(updateDIFF)
   {
      for(Bicluster *c : this->C)
      {
	 std::fill(c->diffV.begin(), c->diffV.end(), 0);
	 std::fill(c->diffU.begin(), c->diffU.end(), 0);
      }
   }

   //calculando o diff de cada vértice
   for(Bicluster *c1 : this->C)
   {
      for(int v : c1->V)
      {
	 int *wl = bg->w[v];
	 int &c1diffV = c1->diffV[v];
	 for(int u : c1->U)
	 {
	    if(updateDIFF)
	    {
	       c1diffV -= wl[u];
	       c1->diffU[u] -= wl[u];
	    }

	    //if((wl[u] < 0)&&(edges[v][u] > 0))
	    if(wl[u] < 0)
	       this->ev += 1;
	       //this->ev += abs(wl[u]);
	 }
	 //calcula diff para os outros clusters
	 for(Bicluster *c2 : this->C)
	 {
	    if(c1->id == c2->id)
	       continue;
	    
	    int &c2diffV = c2->diffV[v];
	    for(int u : c2->U)
	    {
	       if(updateDIFF)
	       {
		  c1->diffU[u] -= wl[u];
		  c2diffV -= wl[u];
	       }
	       //if((wl[u] > 0) && (edges[v][u] < 0))
	       if(wl[u] > 0)
		  this->e0 += 1;
		  //this->e0 += abs(wl[u]);
	    }
	 }

      }
   }
   this->edit = this->ev + this->e0;    
   return this->edit;
}


Solution *Solution::bl1Random()
{
   if(this->C.size() <= 1)
      return NULL;

   int bestOri = -1;
   int bestDest = -1;
   int bestVertice = -1;
   int bestPartition = 0; //(0 : V - 1 : U)

   //Escolhendo Cluster aleatorio, escolhendo um vertice aleatorio de uma particao
   int idOri = rand() % this->C.size();
   int idDes;
   if (idOri > 0)
      idDes = idOri - 1;
   else	
      idDes = idOri + 1;


   bestOri = idOri;
   bestDest = idDes;

   //Escolhendo a particao aleatória
   if(rand() % 2 == 0) //V
   {
      //Correndo os vertices da particao V de ori
      if(this->C[idOri]->V.size() <= 1)
	 return NULL;
      int c = (rand() % this->C[idOri]->V.size());
      int i = 0; 
      //Pegando o elemneto da posicao c na lista V do cluster
      for(int v : this->C[idOri]->V)
      {
	 if(c == i)
	 {
	    bestVertice = v;
	    break;
	 }
	 ++i;
      }
      bestPartition = 0;
   }else //U
   { 
      if(this->C[idOri]->U.size() <= 1)
	 return NULL;
      //Correndo os vertices da particao U de ori
      int c = (rand() % this->C[idOri]->U.size());
      int i = 0; 
      //Pegando o elemneto da posicao c na lista U na lista do cluster
      for(int u : this->C[idOri]->U) 
      {
	 if(c == i)
	 {
	    bestVertice = u;
	    break;
	 }
	 ++i;
      }
      bestPartition = 1;
   }

   //printf("V: %d\n", bestVertice);
   Solution *sol = new Solution(*this);
   //printf("Sol antes: %lu", sol->edit);
   //Removendo o nó da origem e adicionando no destino, atualizando a matriz edges.
   if(bestPartition == 0){ // particao V
      sol->C[bestOri]->removeV(sol, bestVertice);
      sol->C[bestDest]->addV(sol, bestVertice);

      int *edgeV = sol->edges[bestVertice];
      for(int u : sol->C[bestOri]->U)
	 edgeV[u] = Bigraph::FORBIDDEN;
      for(int u : sol->C[bestDest]->U)
	 edgeV[u] = Bigraph::PERMANENT;
   }else{ //particao U
      sol->C[bestOri]->removeU(sol, bestVertice);
      sol->C[bestDest]->addU(sol, bestVertice);

      for(int v : sol->C[bestOri]->V)
	 sol->edges[v][bestVertice] = Bigraph::FORBIDDEN;

      for(int v : sol->C[bestDest]->V)
	 sol->edges[v][bestVertice] = Bigraph::PERMANENT;  
   }
   //printf("Sol depoi: %lu", sol->edit);
   return sol;
}

Solution *Solution::bl1()
{
   if(this->C.size() <= 1)
      return NULL;
   unsigned int bestE = INT_MAX;
   int bestOri = -1;
   int bestDest = -1;
   int bestVertice = -1;
   int bestPartition = 0; //(0 : V - 1 : U)
   bool isSingleton = false;
   //Correndo cada Cluster, percorrendo seus vertices de cada particao
   int idOri = 0;
   for(Bicluster *ori : this->C)
   {
      if(ori->V.size() > 1)
      {
	 //Correndo os vertices da particao V de ori
	 for(int v : ori->V)
	 {
	    unsigned int edAntes = this->edit - ori->diffV[v];

	    //Corre todos os outros cluster != ori testando a melhor insercao dos vertices de ori.
	    int idDes = 0;
	    for(Bicluster *dest : this->C)
	    {
	       if((ori->id != dest->id) && (dest->U.size() > 0))
	       {
		  unsigned int edDepois = edAntes + dest->diffV[v];
		  if(bestE > edDepois){
		     bestE = edDepois;
		     bestOri = idOri;
		     bestDest = idDes;
		     bestVertice = v;
		     bestPartition = 0;
		     isSingleton = false;
		  }
	       }
	       ++idDes;
	    }
	    //Tenta adicionar iV em um Bicluster singleton.
	    //Para criar singleton basta computar a edicao de saida do cluster origem
	    if(bestE > edAntes)
	    {
	       bestE = edAntes;
	       bestOri = idOri;
	       bestVertice = v;
	       bestPartition = 0;
	       isSingleton = true;
	    }

	 }
      }             
      if(ori->U.size() == 1)
	 break;
      //Correndo os vertices da particao U de ori
      for(int u : ori->U)
      {
	 unsigned int edAntes = this->edit - ori->diffU[u];

	 //Procura o melhor cluster para adicionar u
	 int idDes = 0;
	 for(Bicluster *dest : this->C)
	 {
	    if((ori->id != dest->id) && (dest->V.size() > 0))
	    {
	       unsigned int edDepois = edAntes + dest->diffU[u];

	       if(bestE > edDepois){
		  bestE = edDepois;
		  bestOri = idOri;
		  bestDest = idDes;
		  bestVertice = u;
		  bestPartition = 1;
		  isSingleton = false;
	       }
	    }
	    ++idDes;
	 }

	 //Tenta adicionar iU em um Bicluster singleton.
	 //Para cirar singleton basta a edicao de saida do cluster origem    	
	 if(bestE > edAntes)
	 {
	    bestE = edAntes;
	    bestOri = idOri;
	    bestVertice = u;
	    bestPartition = 1;
	    isSingleton = true;
	 }

      }
      ++idOri;
   }

   if(bestE == INT_MAX)
      return NULL;

   Solution *sol = new Solution(*this);
   //Removendo o nó da origem e adicionando no destino, atualizando a matriz edges.
   Bicluster *dest=  NULL;
   if(isSingleton)
   {
      //cout << "Single" << endl;
      dest = new Bicluster(this->bg);
      sol->C.push_back(dest);
   }else{
      dest = sol->C[bestDest];
   }

	    //printf("BL1 antes: %lu\n", sol->edit);
   //bg->C[bestOri]->print();
   //dest->print();
   if(bestPartition == 0)
   { // particao V
      sol->C[bestOri]->removeV(sol, bestVertice);
      dest->addV(sol, bestVertice);

      int *edgeV = sol->edges[bestVertice];
      for(int u : sol->C[bestOri]->U)
	 edgeV[u] = Bigraph::FORBIDDEN;
      for(int u : dest->U)
	 edgeV[u] = Bigraph::PERMANENT;
   }else
   { //particao U
      sol->C[bestOri]->removeU(sol, bestVertice);
      dest->addU(sol, bestVertice);

      for(int v : sol->C[bestOri]->V)
	 sol->edges[v][bestVertice] = Bigraph::FORBIDDEN;

      for(int v : dest->V)
	 sol->edges[v][bestVertice] = Bigraph::PERMANENT;  
   }
	    //printf("BL1 depois: %lu\n", sol->edit);

   return sol;
}

//Join
Solution *Solution::bl2(bool f)
{
   int bestOri = -1;
   int bestDes = -1;
   unsigned int bestEdit = INT_MAX;
   //Correndo cada Cluster, percorrendo seus vertices de cada particao
   for(unsigned int idOri = 0; idOri < this->C.size(); ++idOri){
      Bicluster &ori = *this->C[idOri];
      //Corre todos os outros cluster != ori testando a melhor insercao dos vertices de ori.
      for(unsigned int idDes = idOri + 1; idDes < this->C.size(); ++idDes){
	 Bicluster &dest = *this->C[idDes];

	 //Nao juntar dois clusters sem elementos na mesma particao
	 if(((ori.V.size()==0)&&(dest.V.size()==0)) || ((ori.U.size()==0)&&(dest.U.size()==0)))
	    continue;

	 unsigned int e = this->calculateJoin(ori, dest);

	 if(f){
	    if(rand() % 10 < 2){
	       bestEdit = e;
	       bestOri = idOri;
	       bestDes = idDes;
	       break;
	    }

	 }else{

	    if(e < bestEdit){
	       bestEdit = e;
	       bestOri = idOri;
	       bestDes = idDes;
	    }
	 }
      }
   }
   if(bestOri == -1)
      return NULL; 
   Solution *sol = new Solution(*this);
   sol->join(bestOri, bestDes);
   return sol;
}

//Break Bicluster
Solution *Solution::bl3(bool f)
{
   unsigned int bestEdit = INT_MAX;
   int bestOri = -1;

   if(f)
   {
      //tenta quebra um bicluster aleatorio
      for(int i=0; i<2*C.size(); ++i)
      {
	 int oriID = rand() % C.size();
	 Bicluster *ori = this->C[oriID];
	 pair<bool, int> result = ori->evaluateBreak(true);
	 if(!result.first)
	    continue;

	 Solution *sol = new Solution(*this);
	 sol->edit += result.second;
	 ori = sol->C[oriID];
	 Bicluster *bclu = ori->breakBicluster(sol, true);
	 if(bclu == NULL)
	 {
	    delete sol;
	    continue;
	 }
	 sol->breakBicluster(ori, bclu);
	 return sol;
      }
      return NULL;

   }else
   {
      int idOri = 0;
      for(Bicluster *ori : this->C)
      {
	 if((ori->U.size() == 0) || (ori->V.size() == 0))
	    continue;

	 pair<bool, int> result = ori->evaluateBreak(false);
	 if(result.first)
	 {
	    if(result.second < bestEdit){
	       bestEdit = result.second;
	       bestOri = idOri;
	    }
	 }
	 ++idOri;
      }
   }

   if(bestOri < 0)
      return NULL;

   Solution *sol = new Solution(*this);
   sol->edit += bestEdit;
   Bicluster *bclu = sol->C[bestOri]->breakBicluster(sol, false);
   if(bclu == NULL)
   {
      delete sol;
      return NULL;
   }
   sol->breakBicluster(sol->C[bestOri], bclu);
   //cout << "REAl F: " << bg->edit << endl;

   /*if((bg->e0 < 0) || (bg->ev < 0)){
     this->print();
     bg->print();
     getchar();
     }*/
   return sol;
}

int Solution::breakBicluster(Bicluster *b1, Bicluster *b2)
{
   //Calculando as edicoes apos a separacao dos clusters.
   for(int  v : b1->V)
   {
      int *edgeV = this->edges[v];
      for(int u : b2->U)
      {
	 edgeV[u] = Bigraph::FORBIDDEN;  
      }
   }

   for(int u : b1->U){
      for(int v : b2->V){
	 this->edges[v][u] = Bigraph::FORBIDDEN;  
      }
   }

   this->C.push_back(b2);

   return this->C.size();
}


unsigned int Solution::calculateJoin(Bicluster &b1, Bicluster &b2)
{
   unsigned int aedit = 0;
   for(int v : b1.V)
      aedit += b2.diffV[v]; // target

   for(int u : b1.U)
      aedit += b2.diffU[u]; // target

   return this->edit + aedit;
}

void Solution::join(int idOri, int idDes)
{
   Bicluster &b1 = *this->C[idDes];
   Bicluster &b2 = *this->C[idOri];

   //Juntando os clusters
   //Atualizando a matriz de edicoes apos a juncao dos clusters.
   for(int v : b1.V)
      b1.diffV[v] += b2.diffV[v];
   for(int u : b1.U)
      b1.diffU[u] += b2.diffU[u];

   for(int u : b2.U)
   {
      b1.U.push_back(u);
      for(int v : b1.V)
	 this->edges[v][u] = Bigraph::PERMANENT;

      //Atualizando Diff
      edit += b1.diffU[u];
      b1.diffU[u] = b2.diffU[u] + b1.diffU[u];
   }
   for(int v : b2.V)
   {
      b1.V.push_back(v);
      int *edgesV = this->edges[v];
      for(int u : b1.U)
	 edgesV[u] = Bigraph::PERMANENT;  

      //Atualizando Diff
      edit += b1.diffV[v];
      b1.diffV[v] = b2.diffV[v] + b1.diffV[v];
   }

   //calculando o Diff dos vertices fora dos clusters juntados
   for(int bc=0; bc<C.size(); ++bc)
   {
      if((bc != idOri) && (bc != idDes))
      {
	 for(int v : C[bc]->V)
	    b1.diffV[v] += b2.diffV[v]; 
	 for(int u : C[bc]->U)
	    b1.diffU[u] += b2.diffU[u]; 
      }
   }

   //Remove o cluster idDes.
   this->C.erase(this->C.begin() + idOri);
   delete &b2;//limpando a memoria do bilcuster removido

}



void Solution::makeBicluster(int i, int j, vector<bool> &usedV, vector<bool> &usedU)
{
   this->makeBicluster_n1(i,j, usedV, usedU);
}

void Solution::makeBicluster_n1(int i, int j, vector<bool> &usedV, vector<bool> &usedU)
{
   Bicluster *bc = new Bicluster(this->bg);
   
   for(int u : bg->laV[i])
   {
      if(!usedU[u])
      {
	 bc->U.push_back(u);
	 usedU[u] = true;
      }
   }
   
   for(int v : bg->laU[j])
   {
      if(!usedV[v])
      {
	 bc->V.push_back(v);
	 usedV[v] = true;
      }
      int *edgeV = this->edges[v];
      for(int u : bc->U)
	 edgeV[j] = Bigraph::PERMANENT;
   }
   C.push_back(bc);
}

//Os elementos de V e U n visitados formam cada um, bicluster singleton.
void Solution::makeSingletons(vector<bool> &usedV, vector<bool> &usedU)
{
   for(int v=0; v < bg->V; ++v)
   {
      if(!usedV[v])
      {
	 Bicluster *bc = new Bicluster(this->bg);
	 bc->V.push_back(v);
	 C.push_back(bc);
      }
   }

   for(int u=0; u < bg->U; ++u)
   {
      if(!usedU[u]){
	 Bicluster *bc = new Bicluster(this->bg);
	 bc->U.push_back(u);
	 C.push_back(bc);
      }
   }
}

//retorna a representacao em string dos clusters do bigrafo
std::string Solution::clustersAsStr(){

   std::string bgStr="{";

   for(unsigned int idOri = 0; idOri < this->C.size(); ++idOri){
      Bicluster &ori = *this->C[idOri];
      bgStr+=ori.getText();
      bgStr += ";\n";
   }
   bgStr+="}";

   return bgStr;
}

std::string Solution::getText()
{
   return this->getText(this->C);
}

std::string Solution::getText(vector<Bicluster*> &clusters)
{

   std::string bgStr = "{";

   for(unsigned int idOri = 0; idOri < clusters.size(); ++idOri)
   {
      bgStr+="[";
      Bicluster &ori = *clusters[idOri];
      bgStr+=ori.getText();
      if(idOri < this->C.size()-1)
	 bgStr += "],";
      else
	 bgStr += "]";
   }
   bgStr+="}";

   return bgStr;
}


Solution::~Solution()
{

   for(Bicluster *bclu : this->C)
      delete bclu;

   for(int i=0; i < bg->V; ++i){
      delete this->edges[i];
   }
   delete this->edges;
}

