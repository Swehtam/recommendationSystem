#ifndef RB_H
#define RB_H

#include <list>
#include <vector>

#include "Bigraph.h"
#include "Biclusterizer.h"

class FileBigraph{
    public:
	
	static Biclusterizer *loadFile(char *);

};

#endif
