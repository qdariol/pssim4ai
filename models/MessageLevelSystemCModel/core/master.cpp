/**
 ** File: core/master.cpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#include <core/master.hpp>
#include <iostream>

namespace core
{


Master::Master(sc_core::sc_module_name name)
    : sc_core::sc_module(name)
    , initiator_socket("socket")
{
    std::cerr << "\e[1;30mMaster constructor called for \033[0m" << this->name() << std::endl;
    this->initiator_socket.bind(*this);
    SC_THREAD(Execute);
}



int Master::WriteBytes(sc_dt::uint64 addr, unsigned char* bytes, size_t numofbytes)
{
    tlm::tlm_generic_payload pl;
    pl.set_byte_enable_ptr(NULL);
    pl.set_byte_enable_length(0);
    pl.set_dmi_allowed(false);

    pl.set_data_length(numofbytes);
    pl.set_streaming_width(numofbytes);
    pl.set_data_ptr(bytes);

    pl.set_address(addr);
    pl.set_command(tlm::TLM_WRITE_COMMAND);
    pl.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);

    sc_core::sc_time nodelay = sc_core::SC_ZERO_TIME;
    initiator_socket->b_transport(pl, nodelay);

    if(pl.get_response_status() != tlm::TLM_OK_RESPONSE)
    {
        std::cerr << "\e[1;37m" << this->name() << " \033[1;36mwrite"
            << "\033[1;31m failed"
            << "\033[1;37m at " << sc_core::sc_time_stamp()
            << std::endl;
    }

    return 0;
}



int Master::ReadBytes(sc_dt::uint64 addr, unsigned char* bytes, size_t numofbytes)
{
    tlm::tlm_generic_payload pl;
    pl.set_byte_enable_ptr(NULL);
    pl.set_byte_enable_length(0);
    pl.set_dmi_allowed(false);

    pl.set_data_length(numofbytes);
    pl.set_streaming_width(numofbytes);
    pl.set_data_ptr(bytes);

    pl.set_address(addr);
    pl.set_command(tlm::TLM_READ_COMMAND);
    pl.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);

    sc_core::sc_time nodelay = sc_core::SC_ZERO_TIME;
    initiator_socket->b_transport(pl, nodelay);

    if(pl.get_response_status() != tlm::TLM_OK_RESPONSE)
    {
        std::cerr << "\e[1;37m" << this->name() << " \033[1;36mread"
            << "\033[1;31m failed"
            << "\033[1;37m at " << sc_core::sc_time_stamp()
            << std::endl;
    }

    return 0;

}



tlm::tlm_sync_enum Master::nb_transport_bw(tlm::tlm_generic_payload&, tlm::tlm_phase&, sc_core::sc_time& )
{
    std::cerr << "\e[0;33minvalidate_direct_mem_ptr called" << std::endl;
    return tlm::TLM_COMPLETED;
}

void Master::invalidate_direct_mem_ptr(sc_dt::uint64, sc_dt::uint64 )
{
    std::cerr << "\e[0;33minvalidate_direct_mem_ptr called" << std::endl;
}

} // namespace core

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

