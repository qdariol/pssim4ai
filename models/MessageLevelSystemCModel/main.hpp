/**
 ** File: main.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef MAIN_HPP
#define MAIN_HPP

#ifdef MAIN_CPP
#define REPORT_DEFINE_GLOBALS
#include <tlm.h>
#include <systemc.h>
#include <cstdlib>
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <random>
#include <sharedmemory.hpp>
#include <bus.hpp>
#include <channel.hpp>
#include <delayvector.hpp>
#include <chrono>
#include <ctime>
#include "monitor.hpp"
int pCount, wCount, rCount;
int num_iter = 100;
sc_core::sc_time readdelay(18, sc_core::SC_NS);  // \_ per token
sc_core::sc_time writedelay(14, sc_core::SC_NS); // /
int startCounter, stopCounter;

/**  ENABLE_CLOCK_GATING allows to select the communication procedure and use of power management.
 *
 *   "ENABLE_CLOCK_GATING 1" => Interrupt-based communications with clock gating.
 *   "ENABLE_CLOCK_GATING 0" => Polling-based communications without clock gating. **/
#define ENABLE_CLOCK_GATING 1


/**    Change scenario by uncommenting the file corresponding to the scenario to evaluate  **/
//~ #include <experiments/MLP1-1.hpp>
//~ #include <experiments/MLP1-2.hpp>
//~ #include <experiments/MLP1-3.hpp>
//~ #include <experiments/MLP1-4.hpp>
//~ #include <experiments/MLP1-5.hpp>
//~ #include <experiments/MLP1-6.hpp>
//~ #include <experiments/MLP1-7.hpp>

//~ #include <experiments/MLP2-15.hpp>
//~ #include <experiments/MLP2-16.hpp>
//~ #include <experiments/MLP2-17.hpp>
//~ #include <experiments/MLP2-18.hpp>
//~ #include <experiments/MLP2-19.hpp>
//~ #include <experiments/MLP2-20.hpp>
//~ #include <experiments/MLP2-21.hpp>

//~ #include <experiments/MLP3-29.hpp>
//~ #include <experiments/MLP3-30.hpp>
//~ #include <experiments/MLP3-31.hpp>
//~ #include <experiments/MLP3-32.hpp>
//~ #include <experiments/MLP3-33.hpp>
//~ #include <experiments/MLP3-34.hpp>
//~ #include <experiments/MLP3-35.hpp>

//~ #include <experiments/CNN-43.hpp>
//~ #include <experiments/CNN-44.hpp>
//~ #include <experiments/CNN-45.hpp>
//~ #include <experiments/CNN-46.hpp>
//~ #include <experiments/CNN-47.hpp>
//~ #include <experiments/CNN-48.hpp>

#include <experiments/dse_mapping.hpp>

#endif
#endif
