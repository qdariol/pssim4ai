/**
 ** File: core/master.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef MASTER_HPP
#define MASTER_HPP

#include <systemc>
#include <tlm.h>

namespace core
{

class Master
    : public sc_core::sc_module
    , protected tlm::tlm_bw_transport_if<>
{
    public:
        SC_HAS_PROCESS(Master);
        Master(sc_core::sc_module_name);
        ~Master(){};

        tlm::tlm_initiator_socket<> initiator_socket;

    protected:
        virtual void Execute() = 0;
        int WriteBytes(sc_dt::uint64 addr, unsigned char* bytes, size_t numofbytes);
        int ReadBytes(sc_dt::uint64 addr, unsigned char* bytes, size_t numofbytes);

    private:
        virtual tlm::tlm_sync_enum nb_transport_bw(tlm::tlm_generic_payload&, tlm::tlm_phase&, sc_core::sc_time&);
        virtual void invalidate_direct_mem_ptr(sc_dt::uint64, sc_dt::uint64);
};

}

#endif
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

