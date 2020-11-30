#include <list>
#include <iostream>
#include <vector>
#include <limits.h>

#include "GRASP.h"
#include "VNS.h"
#include "Edge.h"

using namespace std;

Solution *execute_metaheuristic(Bigraph *bg, int num_iter)
{
   struct timeval tempoAntes, ta;
   struct timeval tempoDepois, td;
   srand(time(NULL));	

   unsigned int min_grasp = INT_MAX;
   double media_grasp = 0;
   float tempo_medio_grasp = 0;

   GRASP g(0.5, bg);

   //execucoes do GRASP
   //cout << "GRASP" << endl;
   gettimeofday(&tempoAntes,NULL);
   srand(time(NULL));
   Solution *solBest = NULL;
   for(int i=0;i<N_EXEC;i++)
   {
      Solution* sol = NULL;
      if(i % 2 == 0)
	 sol = g.grasp_vns(num_iter);
      else
	 sol = g.grasp_ils(num_iter);
      media_grasp+=sol->edit;
      //printf("Media: %lu\n", sol->edit);
      if(sol->edit < min_grasp)
	 min_grasp = sol->edit;

      //	FileBicluster::printInstancia("nin", instancia, sol, i);
      //cout << sol->clustersAsStr() << endl << endl;
      if(solBest == NULL)
	 solBest = sol;
      else{
	 if(sol->edit < solBest->edit)
	 {
	    delete solBest;
	    solBest = sol;
	 }else
	    delete sol;
      }
   }
   gettimeofday(&tempoDepois, NULL);
   tempo_medio_grasp = calculaTempo(&tempoAntes, &tempoDepois)/N_EXEC;
   media_grasp /= N_EXEC;

   cout << "Min_grasp: " << min_grasp << " Media: " << media_grasp << " TempoMed: " << tempo_medio_grasp << endl; 
   return solBest;
}

GRASP::GRASP(double a, Bigraph *b) : bg(b), alpha(a)
{
}

Solution* GRASP::grasp_vns(int n_iter)
{
   Solution* best = NULL;

   for(int i = 0; i < n_iter; i++)
   {
      Solution* sol_constr = this->construcao();
      //printf("Contr: %lu\n", sol_constr->edit);
      Solution *sol_vnd = VNS::vnd(sol_constr, 2);
      delete sol_constr;
      //printf("VND: %lu\n", sol_vnd->edit);
      Solution* sol_vns = VNS::vns(sol_vnd);
      delete sol_vnd;
      sol_vns->forceJoin();
      //printf("VNS: %lu\n", sol_vns->edit);

      if(sol_vns == NULL)
      {
	 continue;
      }

      if(best == NULL)
      {
	 best = sol_vns;
      }else
      {
	 if(sol_vns != NULL and sol_vns->edit < best->edit)
	 {
	 	delete best;
	 	best = sol_vns;
	 }else
	 	delete sol_vns;
      }
   }

   return best;
}

Solution* GRASP::grasp_ils(int n_iter)
{
	Solution* best = NULL;

	for(int i = 0; i < n_iter; i++)
	{
		Solution* sol_constr = this->construcao();
      		//printf("Contr: %lu\n", sol_constr->edit);
      		Solution *sol_vnd = VNS::vnd(sol_constr, 2);
		delete sol_constr;
      		//printf("VND: %lu\n", sol_vnd->edit);
		Solution* sol_ils = VNS::ils(sol_vnd);
		delete sol_vnd;
      		sol_ils->forceJoin();
      		//printf("ILS: %lu\n", sol_ils->edit);

		if( best == NULL or (sol_ils != NULL and sol_ils->edit < best->edit))
		{
			delete best;
			best = sol_ils;
		}else
		{
			delete sol_ils;
		}

	}

	return best;
}


#include <algorithm>

Solution* GRASP::run(int iteracoes)
{
	Solution* bestSol = NULL;

	for(int i=0;i < iteracoes;i++)
	{
		Solution* aux = this->iteracao();
		if(bestSol == NULL || aux->edit < bestSol->edit)
		{
			delete bestSol;
			bestSol = aux;
		}else
		   delete aux;
	}

	//cout << "F: " << bestSol->edit << " AVAL: " << bestSol->countEdit() << endl;

	return bestSol;
}

//uma iteracao GRASP consiste em duas fases: construcao e busca local
Solution* GRASP::iteracao(){
	Solution *sol = this->construcao();
	Solution *solVND = VNS::vnd(sol);
        delete sol;
        return solVND;
}

Solution *GRASP::construcao()
{
	Solution *sol = new Solution(this->bg);

	list<Edge> candidatos = this->bg->candidatos; 
	vector<bool> usedV(bg->V, false);
	vector<bool> usedU(bg->U, false);
	
	while(true)
	{ 
		//Setando o valor de filtro dos elementos do LCR
		double gmax = (*candidatos.begin()).g;
 	    	double gmin = (*candidatos.rbegin()).g;
		double filtro = gmax - this->alpha*(gmax - gmin);
		//printf("MIN: %f - MAX: %f FILTRO: %f\n", gmin, gmax, filtro);
		//Inicializando o LCR
		
		//vector<Edge> LCR;
		int posFiltro = 0;
		for(Edge &e : candidatos)
		{
			if(e.g >= filtro)
			   	++posFiltro;
				//LCR.push_back(e);
			else
				break;
		}
		//if(LCR.empty())
		if(posFiltro == 0)
			break;

		//cout << "SIZE LCR: " << LCR.size() << endl;
		
		//Escolha aleatoria do elemento na LCR
		//int pos = rand()%LCR.size();
		//Edge &e = LCR[pos];
		int pos = rand()%posFiltro;
		auto it = candidatos.begin();
		advance(it, pos);
		Edge &e = *it;
				
		//cout << "I: " << e.i <<  " J: " << e.j << endl;
		
		sol->makeBicluster(e.i, e.j, usedV, usedU);
		//sol->print();

		//Remove os candidatos já tratados
		list<Edge>::iterator ite = candidatos.begin();
		while(true)
		{
			if(ite == candidatos.end())
			   break;
			Edge &e = *ite;
			if(usedV[e.i] || usedU[e.j])
			{
				ite = candidatos.erase(ite);
				
			}else
			   ++ite;

		}
		if(candidatos.empty())
			break;
	}
	sol->makeSingletons(usedV, usedU);
        sol->f();
	//cout << sol->getText() << endl;
	
	return sol;
}

