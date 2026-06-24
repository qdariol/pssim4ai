/**
 ** File: time.cpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#include <time.hpp>
#include <cstdlib>
#include <iostream>

Time::Time(const size_t n, const unsigned int timearray[])
    : index(0)
    , length(n)
{
    this->timearray.resize(n);

    for(size_t i=0; i<n; i++)
        this->timearray[i] = timearray[i];

    std::random_shuffle(this->timearray.begin(), this->timearray.end());
}



sc_core::sc_time Time::GetTime()
{
    unsigned int time;
    time = this->timearray[this->index];
    this->index = (this->index + 1) % this->length;
    return sc_core::sc_time(time, sc_core::SC_NS);
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

