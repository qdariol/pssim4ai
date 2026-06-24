/**
 ** File: bus.cpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#include <bus.hpp>
#include <iostream>



Bus& Bus::operator<< (Tile& tile)
{
    tile.initiator_socket(this->target_socket);
    return *this;
}



Bus& Bus::operator<< (SharedMemory& sharedmemory)
{
    this->initiator_socket(sharedmemory.target_socket);
    sc_dt::uint64 address = sharedmemory.GetAddress();
    unsigned int  size    = sharedmemory.GetSize();
    this->starts.push_back(address);
    this->ends.push_back(address + size);
    return *this;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

