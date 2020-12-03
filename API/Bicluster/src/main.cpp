#include "BiclusterParameter.h"
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
   	if (argc != 9) {
	   cout << endl;
	   cout << "Parametros invalidos" << endl;
	   cout << " ./bc Instancia(string) min_buy(int) outlier_product(int) outlier_porc_clients(float) max_dist_component(int) num_exec_metaheuristic(int) num_iter_metaheuristic(int) min_shape_component(int) " << endl;
	   cout << endl;
	   return 0;
	}


   	// ----- Carregar Dados ----- //
   	// Abre arquivo
    	instancia = argv[1];
	BiclusterParameter::MIN_BUY = atoi(argv[2]);
	BiclusterParameter::OUTLIER_PRODUCT = atoi(argv[3]);
	BiclusterParameter::OUTLIER_PORC_CLIENTS = atof(argv[4]);
	BiclusterParameter::MAX_DIST_COMPONENT = atoi(argv[5]);
	BiclusterParameter::NUM_EXEC_METAHEURISTIC = atoi(argv[6]);
	BiclusterParameter::NUM_ITER_METAHEURISTIC = atoi(argv[7]);
	BiclusterParameter::MIN_SHAPE_COMPONENT = atoi(argv[8]);


	Biclusterizer *bcb = FileBigraph::loadFile(instancia);
  	if(bcb != NULL)
	{
		bcb->start();
		cout << bcb->getHypothesis();
	}else
	   return 0;

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

	/*Bigraph *bg = FileBicluster::loadFileMatriz(instancia);
	bg->init();
	Solution *sol = execute_metaheuristic(bg, 30);

	cout << sol->getText() << endl;

	delete sol;
	delete bg;*/
}


