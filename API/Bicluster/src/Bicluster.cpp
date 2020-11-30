#include "Bicluster.h"
#include "Solution.h"
#include "Bigraph.h"

#include <algorithm>
#include <iostream>
#include <cstdlib>
#include<stdio.h>
#include <limits.h>

using namespace std;
      
Bicluster::Bicluster(Bigraph *b) :
   bg(b), diffV(b->V, 0), diffU(b->U, 0), 
   id(Bicluster::numBicluster++)
{
}
      
Bicluster::Bicluster(Bicluster &bc) : 
   bg(bc.bg), diffV(bc.diffV), diffU(bc.diffU),
   id(Bicluster::numBicluster++)
{
   Biclique::V = bc.V;
   Biclique::U = bc.U;
}


pair<bool, unsigned int> Bicluster::evaluateBreak(bool shake)
{
   pair<bool, unsigned int> result = std::make_pair(true, 0);
   double filtroV = 0;
   double filtroU = 0;	
   
   if(shake){
      for(int v : V)
	 filtroV += this->diffV[v];

      if(V.size() > 0)
	 filtroV /= V.size();

      for(int u : U)
	 filtroU += this->diffU[u];

      if(U.size() > 0)
	 filtroU /= U.size();
   }

   //this->print();
   vector<int> V1, V2, U1, U2;
   //Particao V
   for(int v : V)
   {
      if(this->diffV[v] >= filtroV)
	 V2.push_back(v);
      else
	 V1.push_back(v);
   }

   //Particao U
   for(int u : U)
   {
      if(this->diffU[u] >= filtroU)
	 U2.push_back(u);
      else
	 U1.push_back(u);
   }

   if((V1.size() + U1.size() == 0) || (U1.size() + U2.size() == 0))
      result.first = false;

   unsigned int ed = 0;
   
   for(int v1 : V1)
   {
      int *wv1 = bg->w[v1];
      for(int u2 : U2)
      {
	 //ed += wv1[u2];
	 ed += (wv1[u2] > 0 ? 1 : -1);
      }
   }
   for(int v2 : V2)
   {
      int *wv2 = bg->w[v2];
      for(int u1 : U1)
      {
	 //ed += wv2[u1];
	 ed += (wv2[u1] > 0 ? 1 : -1);
      }
   }

   result.second = ed;

   return result;
}
      
Bicluster *Bicluster::breakBicluster(Solution *sol, bool shake)
{
   Bicluster *bclu = new Bicluster(this->bg);
   
   double filtroV = 0;
   double filtroU = 0;	
   
   if(shake){
      for(int v : V)
	 filtroV += this->diffV[v];

      if(V.size() > 0)
	 filtroV /= V.size();

      for(int u : U)
	 filtroU += this->diffU[u];

      if(U.size() > 0)
	 filtroU /= U.size();
   }

   //Particao V
   list<int>::iterator itV = this->V.begin();
   for(; itV != this->V.end(); )
   {
      int v = *itV;
      if(this->diffV[v] >= filtroV)
      {
	 bclu->V.push_back(v);
	 itV = this->V.erase(itV);
      }else
	 ++itV;
   }

   //Particao U
   list<int>::iterator itU = this->U.begin();
   for(; itU != this->U.end(); )
   {
      int u = *itU;
      if(this->diffU[u] >= filtroU)
      {
	 bclu->U.push_back(u);
	 itU = this->U.erase(itU);
      }else
	 ++itU;
   }
   
   //Testa se criou bicluster vazio
   if(this->V.size() + this->U.size() == 0)
   {
      this->V = bclu->V;
      this->U = bclu->U;
      delete bclu;
      return NULL;
   }
   if(bclu->V.size() + bclu->U.size() == 0)
   {
      delete bclu;
      return NULL;
   }


   //Atualizando o Diff
   bclu->diffV = this->diffV;
   bclu->diffU = this->diffU;
   //Vertices contidos no cluster a ser quebrado
   for(int v : this->V)
   {
      int *wv = bg->w[v];
      int &thisdiffV = this->diffV[v];
      for(int u : bclu->U)
      {
	 //thisdiffV += wv[u];
	 //bclu->diffU[u] += wv[u];
	 thisdiffV += (wv[u] > 0 ? 1 : -1);
	 bclu->diffU[u] += (wv[u] > 0 ? 1 : -1);
      }
      
      int &bcludiffV = bclu->diffV[v];
      for(int u : this->U)
      {
	 //bcludiffV += wv[u];
	 //bclu->diffU[u] += wv[u];
	 bcludiffV += (wv[u] > 0 ? 1 : -1);
	 bclu->diffU[u] += (wv[u] > 0 ? 1 : -1);
      }
   }
   for(int v : bclu->V)
   {
      int *wv = bg->w[v];
      int &thisdiffV = this->diffV[v];
      for(int u : bclu->U)
      {
	 thisdiffV += (wv[u] > 0 ? 1 : -1);
	 this->diffU[u] += (wv[u] > 0 ? 1 : -1);
      }
      
      int &bcludiffV = bclu->diffV[v];
      for(int u : this->U)
      {
	 bcludiffV += (wv[u] > 0 ? 1 : -1);
	 this->diffU[u] += (wv[u] > 0 ? 1 : -1);
      }
   }
   
   //Vertices não contidos no bicluster a ser quebrado
   for(Bicluster *bc : sol->C)
   {
      if(bc != this)
      {
	 for(int v : bc->V)
	 {
      	    int *wv = bg->w[v];
	    int &bcludiffV = bclu->diffV[v];
	    for(int u : this->U)
	       bcludiffV += (wv[u] > 0 ? 1 : -1); 
	    
	    int &thisdiffV = this->diffV[v];
	    for(int u : bclu->U)
	       thisdiffV += (wv[u] > 0 ? 1 : -1); 
	 }
	 
	 for(int u : bc->U)
	 {
	    int &bcludiffU = bclu->diffU[u];
	    for(int v : this->V)
	       bcludiffU += (bg->w[v][u] > 0 ? 1 : -1); 
	    
	    int &thisdiffU = this->diffU[u];
	    for(int v : bclu->V)
	       thisdiffU += (bg->w[v][u] > 0 ? 1 : -1); 
	 }
      }
   }

   return bclu;
}

void Bicluster::print(){
   cout << getText() << endl;


   cout << "\nDIFF: ";
   for(int v=0; v < bg->V; ++v)
      cout << this->diffV[v] << ",";
   for(int u=0; u < bg->U; ++u)
      cout << this->diffU[u] << ",";
   cout << endl;
}

void Bicluster::removeV(Solution *s, int v)
{
   this->V.remove(v);

   int *wl = bg->w[v];
   for(int u=0; u < bg->U; ++u)
   {
      //atualiza Diff
      this->diffU[u] += (wl[u] > 0 ? 1 : -1);
   }
   s->edit -= this->diffV[v];
}

void Bicluster::removeU(Solution *s, int u)
{
   this->U.remove(u);

   for(int v=0; v < bg->V; ++v)
   {
      //atualiza diff
      this->diffV[v] += (bg->w[v][u] > 0 ? 1 : -1);
   }
   s->edit -= this->diffU[u];
}

void Bicluster::addV(Solution *s, int v)
{
   int *wl = bg->w[v];
   //atualiza Diff
   for(int u=0; u < bg->U; ++u)
      this->diffU[u] -= (wl[u] > 0 ? 1 : -1);
   
   this->V.push_back(v);
   
   s->edit += this->diffV[v];
}

void Bicluster::addU(Solution *s, int u)
{
   //atualiza diff
   for(int v=0; v < bg->V; ++v)
      this->diffV[v] -= (bg->w[v][u] > 0 ? 1 : -1);

   this->U.push_back(u);

   s->edit += this->diffU[u];
}

int Bicluster::numBicluster = 0;

string Biclique::getText()
{
     char v[10];
     string s = "(";
     list<int>::iterator it = V.begin();
     for(;it != V.end();){
	 sprintf(v, "%d", *it);
         s += v;
	 ++it;
	 if(it != V.end())
         	s += ",";
     }
     s += "),(";
     it = U.begin();
     for(;it != U.end();){
	 sprintf(v, "%d", *it);
         s += v;
	 ++it;
	 if(it != U.end())
         	s += ",";
     }
     s += ")";
     return s;
}

Biclique * Bicluster::getBiclique()
{
   Biclique *bc = new Biclique();
   bc->V = this->V;
   bc->U = this->U;
   return bc;
}
