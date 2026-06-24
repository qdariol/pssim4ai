/**
 ** File: main.cpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#define MAIN_CPP

/** To modify 1. the operation mode (output of SystemC models) and 2. the current scenario (partitionning and mapping)
 ** please refer to the main.hpp file.
 **/
#include <main.hpp>

int sc_main(int argc, char *argv[])
{
    auto begin = std::chrono::system_clock::now();
    // Create Architecture Components
    MB0 mb0;
    MB1 mb1;
    MB2 mb2;
    MB3 mb3;
    MB4 mb4;
    MB5 mb5;
    MB6 mb6;

    SharedMemory sharedmemory("SharedMemory", 0x1000, 32*1024,
            readdelay, writedelay);
    Bus bus("AXIBus");

    // Build Architecture
    bus << mb0;
    bus << mb1;
    bus << mb2;
    bus << mb3;
    bus << mb4;
    bus << mb5;
    bus << mb6;
    bus << sharedmemory;

    // Initialize simulation
    std::srand(0); // 0 is the seed - this is not very random but OK in this case

    // Start simulation
    //~ mon_observer* obs = local_observer::createInstance(1,  &mb0);
    sc_core::sc_start();

    //~ auto end = std::chrono::system_clock::now();

    //~ std::chrono::duration<double> elapsed_seconds = end-begin;
    //~ std::time_t begin_time = std::chrono::system_clock::to_time_t(begin);
    //~ std::time_t end_time = std::chrono::system_clock::to_time_t(end);
    //~ std::cout << "Start Simulation at " << std::ctime(&begin_time);
    //~ std::cout << "End Simulation at " << std::ctime(&end_time)
              //~ << "Simulation time: " << elapsed_seconds.count() << "s\n";
    return 0;
}

