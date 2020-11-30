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


//Join
void Solution::forceJoin(int minProducts)
{
   bool hasMinProducts = true;
   while(true)
   {
      hasMinProducts = false;
      //Se tiver apenas uma biclique pode parar
      if(this->C.size() == 1) break;
      //Procura o bicluster que tenha a quatidade de produtos < minProducts
      unsigned int idOri = 0;
      Bicluster *ori = NULL;
      for(; idOri < this->C.size(); ++idOri)
      {
	 ori = this->C[idOri];
	 if(ori->U.size() >= minProducts)
	    continue;
	 else
	 {
	    hasMinProducts = true;
	    break;
	 }
      }
      if(hasMinProducts)
      {
	 int bestDes = -1;
	 unsigned int bestEdit = INT_MAX;
	 //Corre todos os outros cluster != ori testando a melhor insercao dos vertices de ori.
	 for(unsigned int idDes = 0; idDes < this->C.size(); ++idDes)
	 {
	    if(idDes == idOri) continue;
	    Bicluster &dest = *this->C[idDes];

	    unsigned int e = this->calculateJoin(*ori, dest);

	    if(e < bestEdit){
	       bestEdit = e;
	       bestDes = idDes;
	    }
	 }
	 this->join(idOri, bestDes);
      }else
	 break;
   }
}

