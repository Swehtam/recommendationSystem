#ifndef GRASP_H
#define GRASP_H

#include <stdlib.h>
#include <time.h>

#include "VNS.h"
#include "Bigraph.h"
#include "Util.h"

#define NUM_ITER 40
#define FILTRO 1


#define GVNS 1
#define GILS 2

#define N_EXEC 2

Solution *execute_metaheuristic(Bigraph *bg, int num_exec, int num_iter);

class GRASP{

	private:
		double alpha;
		Bigraph *bg;
		Solution *buscaLocal(Solution *sol);
		VNS perturbacao;
		Solution* iteracao();
	public:
		GRASP(double a, Bigraph *);
		Solution* run(int iteracoes);
		Solution* construcao();
		Solution* grasp_vns(int n_iter);
		Solution* grasp_ils(int n_iter);

};

#endif
