#ifndef BBCLU_H
#define BBCLU_H

class Bicluster;

struct BreakBicluster
{
	Bicluster *b1;
	Bicluster *b2;
	float T;
	int edit;
};

#endif
