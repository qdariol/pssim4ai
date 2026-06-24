/**
 ** File: channel.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef CHANNEL_HPP
#define CHANNEL_HPP

#define BYTES_PER_TOKEN 1
typedef unsigned char Token;

struct Channel
{
    Channel(const char* name, unsigned int prate, unsigned int crate, unsigned int size)
        : name(name)
        , usageaddress(0)
        , indexaddress(0)
        , fifoaddress(0)
        , producerate(prate)
        , consumerate(crate)
        , fifosize(size)
    {};
    const char* name;
    unsigned long long usageaddress; // Virtual address
    unsigned long long indexaddress; // Virtual address - index of the first token in the FIFO
    unsigned long long fifoaddress;  // Virtual address
    unsigned int producerate;
    unsigned int consumerate;

    unsigned int fifosize; // in tokens
};


#endif
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

