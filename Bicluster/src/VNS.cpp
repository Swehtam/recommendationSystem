#include <list>
#include <iostream>
#include <limits.h>
#include<sys/time.h>
#include "VNS.h"
#include "Util.h"
#include "Solution.h"

VNS::VNS()
{
   this->s = NULL;
}

Solution *VNS::ils(Solution *solAtual){

   Solution *bestBL = NULL;
   Solution *sils = new Solution(*solAtual);


   for(int i = 0; i < 3; ++i)
   {
      //realiza pertubacoes na solucao
      int r = 2 + (rand() % 10);  
      for(int j=0; j < r; ++j)
      {
	 int mov = rand() % 3;
	 if(mov == 1){
	    Solution *pert = sils->bl2(true);
	    if(pert != NULL)
	    {
	       if(sils)
		  delete sils;
	       sils = pert;
	    }

	 }else{
	    if(mov == 2){
	       Solution *pert = sils->bl3(true);
	       if(pert != NULL)
	       {
		  if(sils)
		  	delete sils;
		  sils = pert;
	       }
	    }else{
	       Solution *pert = sils->bl1Random();
	       if(pert != NULL)
	       {
		  if(sils)
		  	delete sils;
		  sils = pert;
	       }
	    }
	 }
      }

      //inicia o vnd a partir da solucao resultante da pertubacao
      Solution *vnd = VNS::vnd(sils, 2);
      delete sils;

      if(vnd)
      {
	 if(bestBL)
	 {
	    if(vnd->edit < bestBL->edit){
	       delete bestBL;
	       bestBL = new Solution(*vnd);
	       sils = vnd;
	       i = 0;
	    }else{
	       sils = vnd;
	    }
	 }else
	 {
	    bestBL = new Solution(*vnd);
	    sils = vnd;
	 }
      }else
	 break;
      //Testa se o algoritmo finalizou
      if(i==2)
	 delete vnd;
   }

   return bestBL;
}

Solution *VNS::vnd(Solution *solAtual,int kmax){

   unsigned int bestEdit = solAtual->edit;
   Solution *bestBL = new Solution(*solAtual);

	    //printf("VND antes: %lu\n", bestBL->edit);

   Solution *bl = NULL;
   while(true)
   {
      while(true)
      {
	 //cout << "bl1 init ******" << endl;
	 bl = bestBL->bl1();

	 if(bl != NULL)
	 {
	    //bl->printSolution();
	    if(bl->edit < bestEdit){
	       //cout << "bl1 F: " << bl->edit << " Clusters: " << bl->C.size() << endl;
	       bestEdit = bl->edit;
	       delete bestBL;
	       bestBL = bl;
	    }else{
	       delete bl;
	       break;
	    }
	 }else
	    break;
      }

      if(kmax<1)break;

      //cout << "bl2 init" << endl;
      bl = bestBL->bl2(false);
      //bl->printSolution();
      if(bl != NULL)
      {
	 if(bl->edit < bestEdit)
	 {
	    //cout << "bl2 F: " << bl->edit << " Clusters: " << bl->C.size() << endl;
	    //if(bl->edit < 7)
	    bestEdit = bl->edit;
	    delete bestBL;
	    bestBL = bl;
	    continue;
	 }else{
	    delete bl;
	 }
      }

      //break;
      if(kmax<2)break;

      bl = bestBL->bl3(false);
      if(bl == NULL)
	 return bestBL;

      if(bl->edit < bestEdit)
      {
	 //cout << "BL3 melhorou" << endl;
	 bestEdit = bl->edit;
	 delete bestBL;
	 bestBL = bl;
	 continue;
      }else{
	 delete bl;
	 break;
      }

   }
   //cout << "vnd fim" << endl;
   return bestBL;
}

#include <algorithm>

Solution *VNS::greedyConstruction()
{
   return NULL;
}


Solution *VNS::vns(Solution *sol)
{
   Solution *bestBL = NULL;
   //Solution *svns = sol;
   int k = 0;

   Solution *pert = new Solution(*sol);
   while(k < 3)
   {
      int count = 2 + rand()%10; 
	    //printf("PERT antes: %lu\n", pert->edit);

      for(int i = 0; i < count; ++i)
      {
      	 Solution *aux = NULL;
	 switch(k){
	    case 0:
	       aux = pert->bl1Random();
	       break;
	    case 1:
	       aux = pert->bl2(true);
	       break;
	    case 2:
	       aux = pert->bl3(true);
	       break;
	 }
	 /*printf("Pert K: %d - %d: %lu\n", k, i, pert->edit);
	 if((sol->edit > 0) && (pert->edit == 0))
	    getchar();*/
	 if(aux != NULL){
	    //printf("Aux: %lu\n", aux->edit);
	    delete pert;
	    pert = aux;
	 }
      }


	   // printf("PERT depois: %lu\n", pert->edit);
      Solution *vnd = VNS::vnd(pert, 0);
      if(vnd == NULL)
      {
	 ++k;
	 continue;
      }
	    //printf("VND depois: %lu\n", vnd->edit);
      delete pert;

      if(bestBL)
      {
	 if(vnd->edit < bestBL->edit){
	    delete bestBL;
	    bestBL = new Solution(*vnd);
	    pert = vnd;
	    k = 0;
	 }else{
	    pert = vnd;
	    ++k;
	 }
      }else
      {
	    bestBL = new Solution(*vnd);
	    pert = vnd;
	    k = 0;
      }
      //Teste se chegou ao fim
      if(k==3)
	 delete vnd;
   }

   return bestBL;
}
