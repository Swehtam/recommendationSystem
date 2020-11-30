#include "FileBicluster.h"
#include "Bigraph.h"
#include <fstream>
#include <sstream>
#include <string>
#include <iostream>

using namespace std;

void FileBicluster::printInstancia(char *exec, char *file, float edit_medio, int min_edit, float tempo_medio, int algorithm){
       	FILE *pf;
	char *nn = new char[100];
	sprintf(nn, "%s%s%s", OUT_PATH, exec,".txt");
        if((pf = fopen(nn,"a")) ==NULL){
               	printf("\nNao consigo abrir o arquivo %s!", nn);
                exit(1);
        }
	fprintf(pf, "%s::%f::%d::%f::%d\n", file,edit_medio,min_edit,tempo_medio,algorithm);
	fclose(pf);		
	delete nn;
}

void FileBicluster::printInstancia(char *exec, char *file, int min_edit, float tempo_medio, int algorithm){
       	FILE *pf;
	char *nn = new char[100];
	sprintf(nn, "%s%s%s", OUT_PATH, exec,".txt");
        if((pf = fopen(nn,"a")) ==NULL){
               	printf("\nNao consigo abrir o arquivo %s!", nn);
                exit(1);
        }
	fprintf(pf, "%s::%d::%f::%d\n", file, min_edit,tempo_medio,algorithm);
	fclose(pf);		
	delete nn;
}

void FileBicluster::loadFileLA(char *fileName, vector< vector<int> > &laV, int &V, int &U)
{
	std::ifstream Instancia;
	Instancia.open(fileName);
	int rSize;

	if (!Instancia) {
		printf("Arquivo nao pode ser aberto\n");
		return;
	}
	Instancia >> V; // numero de pecas
	Instancia >> U; // numero de maquinas
	laV.resize(V);
	std::string line;
	for (int i = 0; std::getline(Instancia, line); i++) {
		int dado;
		std::stringstream is(line);
		while (is >> dado) {
			laV[i].push_back(dado);
			//printf("%d ", dado );
		}
		//printf("\n");
	}
	Instancia.close();
}

Bigraph *FileBicluster::loadFileMatriz(char *fileName)
{
   ifstream Instancia(fileName, ios::in);
   int rSize;

   if (!Instancia) {
      cerr << "Arquivo nao pode ser aberto" << endl;
      return NULL;
   }
   //string header;
   //std::getline(Instancia, header);

   int v, u;
   Instancia >> v; // numero de pecas
   Instancia >> u; // numero de maquinas

   Bigraph *bg = new Bigraph(v, u);

   for (int i = 0; i < v; i++) 
   {
      for (int j = 0; j < u; j++) 
      {
	 int data;
	 Instancia >> data;
	 if(data == 1)
	 {
	    bg->w[i][j] = 1;
	    bg->laV[i].push_back(j);
	    bg->laU[j].push_back(i);
	 }else
	    bg->w[i][j] = -1;
      }//printf("\n");
   }
   Instancia.close();
   return bg;
}

