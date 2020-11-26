#ifndef VNS_H
#define VNS_H

#include <stdlib.h>
#include <time.h>
#include <set>


#define NUM_ITER 40
#define FILTRO 1

#include "Solution.h"

class VNS
{
	private:
		static Solution *greedyConstruction();
		
	public:
		Solution *s;
		VNS();
		static Solution *vnd(Solution *,int kmax=2);
		static Solution *vns(Solution *solAtual, float maxTime);
		static Solution *vns(Solution *solAtual);
		void start();

		//Solution *ils(set<Solution*, SolutionCompare> elite);
		static Solution *ils(Solution *elite, float maxTime);
		static Solution *ils(Solution *elite);
};

#endif
