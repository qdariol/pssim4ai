/**
 ** File: monitor.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef MONITOR_HPP
#define MONITOR_HPP

sc_time T_LATENCY, T_ITERSTART, T_ITEREND;
int MEASURED_ITERATION = -1;

#define ITERATION_BEGIN() \
        if(MEASURED_ITERATION == -1) \
        { \
            T_ITERSTART = sc_time_stamp(); \
            MEASURED_ITERATION = i; \
        }

#define ITERATION_END() \
        if(MEASURED_ITERATION == i) \
        { \
            T_ITEREND = sc_time_stamp(); \
            T_LATENCY = T_ITEREND - T_ITERSTART; \
            std::cout << std::dec  \
                << T_LATENCY.value() / 1000 << std::endl; \
            std::cerr << "\e[s" << ((i-SKIP_ITERATIONS) / double(NUM_OF_ITERATIONS - SKIP_ITERATIONS)) * 100.0 << "%\e[u"; \
            MEASURED_ITERATION = -1; \
        }



#endif
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

