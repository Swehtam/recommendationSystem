#ifndef SOLUTION_H
#define SOLUTION_H

#include <list>
#include <vector>
#include <set>
#include <string>

#include "Edge.h"
#include "Bicluster.h"

using namespace std; 

class Bigraph;

//Estrutura que representa um Bigrafo
class Solution
{
   public:
	//Contador de edicoes ao bigrafo
	unsigned int ev, e0, edit;

	//Matriz usada para fixacao das aretas:
	//-1 : forbidden
	//0 : free
	//+1 : permanent
	int **edges;
	
        //conjunto de biclusters da solução
	vector<Bicluster *> C;

	unsigned int calculateJoin(Bicluster &b1, Bicluster &b2);
	void join(int idOri, int idDes);
	int breakBicluster(Bicluster *b1, Bicluster *b2);

	Solution(Bigraph *);
        Solution(Solution &b);
	~Solution();
       
	//Grafo de entrada
	Bigraph *bg;
	//Calcula o numero de edicoes da solucao e atualiza o vetor DIFF caso updateDIFF == true
	unsigned int f(bool updateDIFF=true);
	
	//Implementada a busca local de Resende para o Cell Formation (vizinhanca de Resende adaptadoao Bilcuster Editing)
	Solution *bl1();
	Solution *bl1Random();
	
	//Implementada a junção de dois clusters (adaptado ao cell formation)
	Solution *bl2(bool f);
	//Força a juncao de biclusters até que nenhum biclique tenha em sua particao de produtos a quantidade < minProducts
	void forceJoin(int minProducts = 5);

	//Implementada a quebra de um custer em dois clusters
	Solution *bl3(bool f);

	void makeBicluster(int i, int j, vector<bool> &usedV, vector<bool> &usedU);
	void makeSingletons(vector<bool> &usedV, vector<bool> &usedU);
	void add(Bicluster *bc);

        std::string clustersAsStr();
	std::string getText();
	std::string getText(vector<Bicluster*> &);
	
	static bool compare(Solution *b1, Solution *b2){
    		if(b1->ev + 1.05*b1->e0 == b2->ev + 1.05*b2->e0)
			return false;
    		else
    			return (b1->ev + 1.05*b1->e0 < b2->ev + 1.05*b2->e0);
    	}

   private:
	void makeBicluster_n1(int i, int j, vector<bool> &usedV, vector<bool> &usedU);
	void makeBicluster_n2(int i, int j, vector<bool> &usedV, vector<bool> &usedU);
};

struct SolutionCompare
{
  bool operator()(Solution *b1, Solution *b2) const
  {
    if(b1->ev + 1.05*b1->e0 == b2->ev + 1.05*b2->e0)
	return false;
    else
    	return (b1->ev + 1.05*b1->e0 < b2->ev + 1.05*b2->e0);
  }
};

#endif
