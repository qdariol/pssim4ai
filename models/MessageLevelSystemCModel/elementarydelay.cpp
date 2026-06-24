/**
 ** File: elementarydelay.cpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#include <elementarydelay.hpp>
#include <cstdlib>
#include <iostream>

int DelayOffsetRead(int numTokens, int clock_gating_is_on)
{
    if(clock_gating_is_on==1){
        return (t_init_r_cg + t_p_cg + t_pr_r + t_r*numTokens+t_rl*(numTokens-1)+t_po_r+t_w);
    }
    else{
        return (t_init_r + t_p + t_pr_r + t_r*numTokens+t_rl*(numTokens-1)+t_po_r+t_w);
    }
}

int DelayOffsetWrite(int numTokens, int clock_gating_is_on)
{
    if(clock_gating_is_on==1){
        return (t_init_w_cg + t_p_cg + t_pr_r + t_w*numTokens+t_wl*(numTokens-1)+t_po_w+t_w);
    }
    else{
        return (t_init_w + t_p + t_pr_r + t_w*numTokens+t_wl*(numTokens-1)+t_po_w+t_w);
    }
}
