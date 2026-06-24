/**
 ** File: tile.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef TILE_HPP
#define TILE_HPP

#include <core/master.hpp>
#include <delayvector.hpp>
#include <elementarydelay.hpp>

extern int pCount, wCount, rCount;

class Tile : public core::Master
{
    public:
        Tile(sc_core::sc_module_name name);
        ~Tile(){};

        virtual void Execute() = 0;

    protected:
        bool WriteTokens(sc_core::sc_event& read_event, sc_core::sc_event& write_event, bool BufferAvail, bool sameCore, int numTokens, int delayLoop, int iterationNb, int clock_gating_is_on);
        bool ReadTokens(sc_core::sc_event& read_event, sc_core::sc_event& write_event, bool BufferAvail, bool sameCore, int numTokens, int delayLoop, int iterationNb, int clock_gating_is_on);
        int Delay(int pCount, int wCount, int rCount, int numTokens, int delayOffset, int delayLoop, int clock_gating_is_on);
    private:

};

#endif
