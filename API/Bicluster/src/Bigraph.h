#ifndef BIG_H
#define BIG_H

#include <list>
#include <vector>
#include <set>


using namespace std; 

class Edge;

//Estrutura que representa um Bigrafo
class Bigraph
{
   public:
      //dimensoes
	int V, U;

	//tipo de construcao a ser utilizada pelo GRASP (avaliar n1, fechar n1; avaliar n2, fechar n2; avaliar n2, fechar n1)
	static int constr_type;
 	//constantes que representam os tipos de construcoes possiveis
        static const int N1_N1;
        static const int N2_N2;
        static const int N2_N1;

	//Listas de Adjacencia de cada particao de vertices (N1)
	vector<list<int> > laV;
	vector<list<int> > laU;
	
	void createN1();
		
	//Listas de Adjacencia dos vizinhos de cada vertices de cada particao(N2)
	//vector<set<int> > laV2;
	//vector<set<int> > laU2;
	
	//void createN2();
	 
	list<Edge> candidatos;
	void initCandidates();

	//Matriz de adjacencia
	int **w;
	static const int FORBIDDEN;
    	static const int FREE;
    	static const int PERMANENT;
        
	Bigraph(int v, int u);
	~Bigraph();
      
	//Inicializa as vizinhanças N1 e N2 e os candidatos do GRASP
	void init();

	//funcoes gulosas usadas nas construcoes
	float g_n2(int i, int j); 
	float g_n1(int i,int j);

	void print();

};
#endif
