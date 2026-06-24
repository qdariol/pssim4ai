/**
 ** File: elementarydelay.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef ELEMENTARYDELAY_HPP
#define ELEMENTARYDELAY_HPP

#include <vector>
#include <string>
#include <systemc.h>
#include <cstdlib>

/** Difference between POLLING WITHOUT CLOCK GATING and INTERRUPT-BASED WITH CLOCK GATING
 *      - t_p, t_pl, t_p_loop set to 0: no polling so no delay linked to polling
 *      - t_init_r, t_init_w increased: setting up the ISR routine, generating interrupt when Rd/Wr completed causes delays
 * **/
const int   t_r=8,                      //read
            t_p=8,                      //polling
            t_w=5,                      //write
            t_rl=14,                    //wait to the next read
            t_wl=13,                    //wait to the next write
            t_r_loop=22,                //t_r_loop=t_r+t_rl
            t_w_loop=18,                //t_w_loop=t_w+t_wl
            t_p_loop=15,                //t_p_loop=t_p+t_pl -- t_pl=7 (deprecated, not used in favor to t_p_loop)
            t_pr_r=15,                  //t_pre_read
            t_po_r=11,                  //t_post_read
            t_pr_w=15,                  //t_pre_write
            t_po_w=9,                   //t_post_write
            t_init_r=15,                //t_init_read
            t_init_w=16,                //t_init_write
            t_init_r_cg=15+333,         //t_init_read with clock gating
            t_init_w_cg=16+333,         //t_init_write with clock gating
            t_p_cg=0,                   //polling with clock gating
            t_p_loop_cg=0;              //t_p_loop=t_p+t_pl with clock gating

int DelayOffsetRead(int numTokens, int clock_gating_is_on);
int DelayOffsetWrite(int numTokens,  int clock_gating_is_on);


#endif
