#include "FileBicluster.h"
#include "FileBigraph.h"
#include "VNS.h"
#include "GRASP.h"
#include <algorithm>
#include <stdio.h>
#include <limits.h>
#include <sstream>
#include <iostream>

using namespace std;

char *instancia;

int main(int argc, char** argv)
{
   	// ----- Carregar Dados ----- //
   	// Abre arquivo
    	instancia = argv[1];

	Biclusterizer *bcb = FileBigraph::loadFile(instancia);
  	if(bcb != NULL)
	{
		bcb->start();
   		cout << bcb->getHypothesis();
		/*int c1 = 0;
		int c2 = 0;
		int cn = 0;
		for(Biclique *b : bcb->bicliques)
		{
		   if(b->U.size() == 1)
		      ++c1;
		   if(b->U.size() == 2)
			++c2;
		   if(b->U.size() > 2)
		   {
		      cout << b->getText() << endl;
		      ++cn;
		   }
		}
		printf("Num Bicliques: %d\n", bcb->bicliques.size()); 
		printf("Num Bicliques 1: %d\n", c1); 
		printf("Num Bicliques 2: %d\n", c2); 
		printf("Num Bicliques n: %d\n", cn);*/ 
	}
/*	Bigraph *bg = FileBicluster::loadFileMatriz(instancia);
	bg->init();
	Solution *sol = execute_metaheuristic(bg, 30);
	
	cout << sol->getText() << endl;
	
	delete sol;
	delete bg;*/
}


