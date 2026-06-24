/**
 ** File: tile.cpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#include <tile.hpp>
#include <iostream>
#include <cstdlib>
#include <fstream>

Tile::Tile(sc_core::sc_module_name name)
    : core::Master(sc_core::sc_module_name(name))
{
}

bool Tile::WriteTokens(sc_core::sc_event& read_event, sc_core::sc_event& write_event, bool BufferAvail, bool sameCore, int numTokens, int delayLoop, int iterationNb, int clock_gating_is_on)
{
    int delayOffset;

    std::cout << iterationNb << "," << name() << ",POLLING,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
    //Polling
    if (BufferAvail != 1 & sameCore != 1)
    {
        pCount = pCount + 1;
        wait(read_event);
        pCount = pCount - 1;
    }
    std::cout << iterationNb << "," << name() << ",POLLING,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;

    std::cout << iterationNb << "," << name() << ",COMM,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
    //Writing
    wCount = wCount + 1;
    delayOffset= DelayOffsetWrite(numTokens, clock_gating_is_on);
    sc_core::wait(this->Delay(pCount, wCount, rCount, numTokens, delayOffset, delayLoop, clock_gating_is_on), sc_core::SC_NS);
    wCount = wCount - 1;

    write_event.notify();
    BufferAvail = 0;
    std::cout << iterationNb << "," << name() << ",COMM,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;

    return BufferAvail;
}

bool Tile::ReadTokens(sc_core::sc_event& read_event, sc_core::sc_event& write_event, bool BufferAvail, bool sameCore, int numTokens, int delayLoop, int iterationNb, int clock_gating_is_on)
{
    int delayOffset;

    std::cout << iterationNb << "," << name() << ",POLLING,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
    //Polling
    if(BufferAvail != 0 & sameCore != 1)
    {
        pCount = pCount + 1;
        wait(write_event);
        pCount = pCount - 1;
    }
    std::cout << iterationNb << "," << name() << ",POLLING,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;

    std::cout << iterationNb << "," << name() << ",COMM,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
    //Reading
    rCount = rCount + 1;
    delayOffset = DelayOffsetRead(numTokens, clock_gating_is_on);
    sc_core::wait(this->Delay(pCount, wCount, rCount, numTokens, delayOffset, delayLoop, clock_gating_is_on), sc_core::SC_NS);
    rCount = rCount - 1;

    read_event.notify();
    BufferAvail = 1;
    std::cout << iterationNb << "," << name() << ",COMM,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
    return BufferAvail;
}

int Tile::Delay(int pCount, int wCount, int rCount, int numTokens, int delayOffset, int delayLoop, int clock_gating_is_on)
{
    int delay, tmp_delay;
    if (pCount+wCount+rCount<=2) // two cores
    {
        //tmp_delay depends on whether interrupt+clock gating is on or not.
        if(clock_gating_is_on==1){
            tmp_delay = pCount*t_p_loop_cg+wCount*t_w_loop+rCount*t_r_loop-(pCount+rCount+wCount)*delayLoop;
        }
        else{
            tmp_delay = pCount*t_p_loop+wCount*t_w_loop+rCount*t_r_loop-(pCount+rCount+wCount)*delayLoop;
        }
        //delay depends on tmp_delay
        if (tmp_delay > 0){
            delay = delayOffset + tmp_delay*(numTokens+2); // 1 last polling + n tokens + 1 token update usage
        }
        else{
            delay = delayOffset;
        }
    }
    else
    {
        //tmp_delay depends on whether interrupt+clock gating is on or not.
        if(clock_gating_is_on==1){
            tmp_delay = pCount*t_p_cg+wCount*t_w+rCount*t_r-delayLoop;
        }
        else{
            tmp_delay = pCount*t_p+wCount*t_w+rCount*t_r-delayLoop;
        }
        //delay depends on tmp_delay
        if (tmp_delay > 0)    // n cores (n>2)
            delay = delayOffset + tmp_delay*(numTokens+2); // 1 last polling+ n tokens + 1 token update usage
        else
            delay = delayOffset + (t_r_loop-t_w_loop)*(numTokens+2); // 1 polling tokens + n tokens + 1 token update usage;
    }
    return delay; //delayOffset
}
