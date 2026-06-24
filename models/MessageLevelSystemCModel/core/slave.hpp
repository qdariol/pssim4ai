/**
 ** File: core/slave.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef SLAVE_HPP
#define SLAVE_HPP

#define SC_INCLUDE_DYNAMIC_PROCESSES

#include <systemc>
#include <tlm.h>
#include <vector>

namespace core
{

class Memory
    : public sc_core::sc_module
    , protected tlm::tlm_fw_transport_if<>
{
    public:
        tlm::tlm_target_socket<> target_socket;
        Memory(sc_core::sc_module_name name, unsigned int size, sc_core::sc_time& readdelay, sc_core::sc_time& writedelay);
        ~Memory(){};

    private:
        int check_offset(sc_dt::uint64 offset);
        virtual void b_transport(tlm::tlm_generic_payload& trans, sc_core::sc_time& delay);

        std::vector<unsigned char> memory;
        sc_core::sc_time readdelay;
        sc_core::sc_time writedelay;

        virtual tlm::tlm_sync_enum nb_transport_fw(tlm::tlm_generic_payload&, tlm::tlm_phase&, sc_core::sc_time&);
        virtual bool get_direct_mem_ptr(tlm::tlm_generic_payload&, tlm::tlm_dmi&);
        virtual unsigned int transport_dbg(tlm::tlm_generic_payload&);
};

} // namespace core
#endif
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

