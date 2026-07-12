/**
 ** File: time.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Sébastien Le Nours, Sébastien Pillement, Ralf Stemmer,
 **          Domenik Helms, Kim Grüttner, Hai Dang Vu - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef TIME_HPP
#define TIME_HPP

#include <vector>
#include <systemc.h>
#include <cstdlib>

class Time
{
    public:
        Time(const size_t n, const unsigned int timearray[]);

        sc_core::sc_time GetTime();

    private:
        std::vector<unsigned int> timearray;
        unsigned int index;
        size_t length;
};

#endif
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

