#ifndef EDGE_H
#define EDGE_H

struct Edge
{
	int i;
	int j;
	float g;

	Edge(int i, int j, int g): i(i), j(j), g(g){
	}

	static bool compare(Edge e, Edge e1){
		if(e.g > e1.g)
			return true;
		else 
			return false;
	}
};

#endif
