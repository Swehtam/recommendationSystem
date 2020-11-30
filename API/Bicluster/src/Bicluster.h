#ifndef BCLU_H
#define BCLU_H

#include <vector>
#include <list>
#include <string>

class Bigraph;
class Solution;
class BreakBicluster;

using namespace std;

class Biclique
{
   public:
      list<int> V;
      list<int> U;

      std::string getText();
};


class Bicluster : public Biclique
{
   public:
      static int numBicluster;
      int id;
      
       //indica o quanto o vertice esta ligado ao seu cluster atual
       //diff = (soma das ligacoes positivas - soma das ligacoes negativas) com o cluster atual
       vector<int> diffV, diffU;

      Bicluster(Bigraph *);
      Bigraph *bg;
      
      Bicluster(Bicluster &bc);
      void print();

       //Atualiza o edit do Bigraph e o diff dos vertices com relacao ao cluster.

       void removeV(Solution *s, int v);
       void removeU(Solution *s, int u); 
       void addV(Solution *s, int v);
       void addU(Solution *s, int u);

      pair<bool, unsigned int> evaluateBreak(bool shake);
      Bicluster *breakBicluster(Solution *s, bool shake);

      Biclique * getBiclique();

};

#endif

