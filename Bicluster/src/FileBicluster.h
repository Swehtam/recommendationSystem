#ifndef FILEMED_H
#define FILEMED_H

#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <vector>



#define IN_PATH "entrada/"
#define OUT_PATH "saida/"

#define DIST_DELTA 100
#define CUSTO_BASE 65
#define CUSTO_DELTA 10

using namespace std;

class Bigraph;

class FileBicluster{
        public:
		
		static void loadFileLA(char *fileName, vector< vector<int> > &laV, int &V, int &U);
		static Bigraph *loadFileMatriz(char *fileName);

	   	static void printInstancia(char *exec, char *file, Bigraph *bg, int p);
		static void printInstancia(char *nameExec, char *file,  float edit_medio,int min_edit, float tempo_medio,int algorithm);
		static void printInstancia(char *exec, char *file, int min_edit, float tempo_medio, int algorithm);
        
        
};

#endif
