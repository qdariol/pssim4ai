/**
 ** File: sharedmemory.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef SHAREDMEMORY_HPP
#define SHAREDMEMORY_HPP

#include <core/slave.hpp>
#include <channel.hpp>


class SharedMemory : public core::Memory
{
    public:
        SharedMemory(const char* name, sc_dt::uint64 address, unsigned int size, sc_core::sc_time readdelay, sc_core::sc_time writedelay)
            : Memory(name, size, readdelay, writedelay)
            , address(address), size(size), used(0), channels(0) {};

        unsigned int GetSize() const;
        sc_dt::uint64 GetAddress() const;

        SharedMemory& operator<< (Channel& channel);

    private:
        unsigned long long AllocateMemory(unsigned int numbytes);
        Channel* GetChannelByOffset(unsigned long long offset);

        unsigned int  size; // actual size in bytes
        unsigned int  used; // used bytes
        sc_dt::uint64 address;
        std::vector<Channel*> channels;
};


#endif
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

