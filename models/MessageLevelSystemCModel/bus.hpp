/**
 ** File: bus.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef BUS_HPP
#define BUS_HPP

#include <core/bus.hpp>
#include <tile.hpp>
#include <sharedmemory.hpp>

class Bus
    : public core::Bus
{
    public:
        Bus(const char* name)
            : core::Bus(name) {};

        Bus& operator<< (Tile& tile);
        Bus& operator<< (SharedMemory& sharedmemory);
};


#endif
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

