#include "Util.h"

float calculaTempo(struct timeval*antes,struct timeval* depois ){

        float tempo_total;
        timeval dif;
        //tempo total
        timersub(depois, antes, &dif);
        if(dif.tv_usec != 0)
                tempo_total = dif.tv_sec*1000 + dif.tv_usec/1000;
        else
                tempo_total = dif.tv_sec*1000;

        return tempo_total;

}

