#ifndef EXPERIMENT_HPP
#define EXPERIMENT_HPP

#include <iostream>
#include <cstdlib>
#include <fstream>
#include <tile.hpp>
#include <channel.hpp>
#include <utils.hpp>


/** Cluster sizes definition **/

#define INPUT_TOKENS_SIZE 576
#define L1_TOTAL_TOKENS_OUT 30
#define L1_C1 10
#define L1_C2 10
#define L1_C3 10
#define L2_TOTAL_TOKENS_OUT 30
#define L2_C1 30
#define L3_TOTAL_TOKENS_OUT 43
#define L3_C1 6
#define L3_C2 6
#define L3_C3 6
#define L3_C4 6
#define L3_C5 6
#define L3_C6 6
#define L3_C7 7

/** Delay definition **/

auto Delay_L1_C1 = DelayVector(INPUT_TOKENS_SIZE, L1_C1);
auto Delay_L1_C2 = DelayVector(INPUT_TOKENS_SIZE, L1_C2);
auto Delay_L1_C3 = DelayVector(INPUT_TOKENS_SIZE, L1_C3);
auto Delay_L2_C1 = DelayVector(L1_TOTAL_TOKENS_OUT, L2_C1);
auto Delay_L3_C1 = DelayVector(L2_TOTAL_TOKENS_OUT, L3_C1);
auto Delay_L3_C2 = DelayVector(L2_TOTAL_TOKENS_OUT, L3_C2);
auto Delay_L3_C3 = DelayVector(L2_TOTAL_TOKENS_OUT, L3_C3);
auto Delay_L3_C4 = DelayVector(L2_TOTAL_TOKENS_OUT, L3_C4);
auto Delay_L3_C5 = DelayVector(L2_TOTAL_TOKENS_OUT, L3_C5);
auto Delay_L3_C6 = DelayVector(L2_TOTAL_TOKENS_OUT, L3_C6);
auto Delay_L3_C7 = DelayVector(L2_TOTAL_TOKENS_OUT, L3_C7);

/** Event definition **/

sc_core::sc_event   write_input_l1c1, read_input_l1c1, 
                    write_input_l1c2, read_input_l1c2, 
                    write_input_l1c3, read_input_l1c3, 
                    write_l1c1_l2c1, read_l1c1_l2c1, 
                    write_l1c2_l2c1, read_l1c2_l2c1, 
                    write_l1c3_l2c1, read_l1c3_l2c1, 
                    write_l2c1_l3c1, read_l2c1_l3c1, 
                    write_l2c1_l3c2, read_l2c1_l3c2, 
                    write_l2c1_l3c3, read_l2c1_l3c3, 
                    write_l2c1_l3c4, read_l2c1_l3c4, 
                    write_l2c1_l3c5, read_l2c1_l3c5, 
                    write_l2c1_l3c6, read_l2c1_l3c6, 
                    write_l2c1_l3c7, read_l2c1_l3c7, 
                    write_l3c1_decoder, read_l3c1_decoder, 
                    write_l3c2_decoder, read_l3c2_decoder, 
                    write_l3c3_decoder, read_l3c3_decoder, 
                    write_l3c4_decoder, read_l3c4_decoder, 
                    write_l3c5_decoder, read_l3c5_decoder, 
                    write_l3c6_decoder, read_l3c6_decoder, 
                    write_l3c7_decoder, read_l3c7_decoder, 
                    write_decoder_output, read_decoder_output; 

/** Buffer availability definition **/

bool buff_input_l1c1 = 1;
bool buff_input_l1c2 = 1;
bool buff_input_l1c3 = 1;
bool buff_l1c1_l2c1 = 1;
bool buff_l1c2_l2c1 = 1;
bool buff_l1c3_l2c1 = 1;
bool buff_l2c1_l3c1 = 1;
bool buff_l2c1_l3c2 = 1;
bool buff_l2c1_l3c3 = 1;
bool buff_l2c1_l3c4 = 1;
bool buff_l2c1_l3c5 = 1;
bool buff_l2c1_l3c6 = 1;
bool buff_l2c1_l3c7 = 1;
bool buff_l3c1_decoder = 1;
bool buff_l3c2_decoder = 1;
bool buff_l3c3_decoder = 1;
bool buff_l3c4_decoder = 1;
bool buff_l3c5_decoder = 1;
bool buff_l3c6_decoder = 1;
bool buff_l3c7_decoder = 1;
bool buff_decoder_output = 1;

/** Main latency markers definition **/

double t_latency = 0;
sc_core::sc_time start[1000000];
sc_core::sc_time stop[1000000];
sc_core::sc_time latency[1000000];




/** Tiles and mapping **/

class MB0 : public Tile
{
    public:
        MB0() : Tile(sc_core::sc_module_name("MB0")) {};
    protected:
        void Execute();
};

void MB0::Execute()
{
    for(int i = 0; i < num_iter; i++)
    {
        //Source
        std::cout << i << ",ITERATION,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;

        // Actor L1_C1
        buff_input_l1c1 = this->ReadTokens(read_input_l1c1, write_input_l1c1, buff_input_l1c1, 1, INPUT_TOKENS_SIZE, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB0,L1_C1,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L1_C1.GetDelay());
        std::cout << i << ",MB0,L1_C1,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l1c1_l2c1 = this->WriteTokens(read_l1c1_l2c1, write_l1c1_l2c1, buff_l1c1_l2c1, 0, L1_C1, t_r_loop, i, ENABLE_CLOCK_GATING);

        // Actor L3_C1
        buff_l2c1_l3c1 = this->ReadTokens(read_l2c1_l3c1, write_l2c1_l3c1, buff_l2c1_l3c1, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB0,L3_C1,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L3_C1.GetDelay());
        std::cout << i << ",MB0,L3_C1,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l3c1_decoder = this->WriteTokens(read_l3c1_decoder, write_l3c1_decoder, buff_l3c1_decoder, 0, L3_C1, t_r_loop, i, ENABLE_CLOCK_GATING);

        // Actor L3_C2
        buff_l2c1_l3c2 = this->ReadTokens(read_l2c1_l3c2, write_l2c1_l3c2, buff_l2c1_l3c2, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB0,L3_C2,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L3_C2.GetDelay());
        std::cout << i << ",MB0,L3_C2,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l3c2_decoder = this->WriteTokens(read_l3c2_decoder, write_l3c2_decoder, buff_l3c2_decoder, 0, L3_C2, t_r_loop, i, ENABLE_CLOCK_GATING);

        // Actor L3_C3
        buff_l2c1_l3c3 = this->ReadTokens(read_l2c1_l3c3, write_l2c1_l3c3, buff_l2c1_l3c3, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB0,L3_C3,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L3_C3.GetDelay());
        std::cout << i << ",MB0,L3_C3,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l3c3_decoder = this->WriteTokens(read_l3c3_decoder, write_l3c3_decoder, buff_l3c3_decoder, 0, L3_C3, t_r_loop, i, ENABLE_CLOCK_GATING);

        // Actor L3_C6
        buff_l2c1_l3c6 = this->ReadTokens(read_l2c1_l3c6, write_l2c1_l3c6, buff_l2c1_l3c6, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB0,L3_C6,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L3_C6.GetDelay());
        std::cout << i << ",MB0,L3_C6,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l3c6_decoder = this->WriteTokens(read_l3c6_decoder, write_l3c6_decoder, buff_l3c6_decoder, 0, L3_C6, t_r_loop, i, ENABLE_CLOCK_GATING);

        // Actor Decoder
        buff_l3c1_decoder = this->ReadTokens(read_l3c1_decoder, write_l3c1_decoder, buff_l3c1_decoder, 0, L3_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l3c2_decoder = this->ReadTokens(read_l3c2_decoder, write_l3c2_decoder, buff_l3c2_decoder, 0, L3_C2, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l3c3_decoder = this->ReadTokens(read_l3c3_decoder, write_l3c3_decoder, buff_l3c3_decoder, 0, L3_C3, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l3c4_decoder = this->ReadTokens(read_l3c4_decoder, write_l3c4_decoder, buff_l3c4_decoder, 0, L3_C4, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l3c5_decoder = this->ReadTokens(read_l3c5_decoder, write_l3c5_decoder, buff_l3c5_decoder, 0, L3_C5, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l3c6_decoder = this->ReadTokens(read_l3c6_decoder, write_l3c6_decoder, buff_l3c6_decoder, 0, L3_C6, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l3c7_decoder = this->ReadTokens(read_l3c7_decoder, write_l3c7_decoder, buff_l3c7_decoder, 0, L3_C7, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_decoder_output = this->WriteTokens(read_decoder_output, write_decoder_output, buff_decoder_output, 1, L3_TOTAL_TOKENS_OUT, t_r_loop, i, ENABLE_CLOCK_GATING);

        //Sink
        std::cout << i << ",ITERATION,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
    }
}

class MB1 : public Tile
{
    public:
        MB1() : Tile(sc_core::sc_module_name("MB1")) {};
    protected:
        void Execute();
};

void MB1::Execute()
{
    for(int i = 0; i < num_iter; i++)
    {
        // Actor L1_C2
        buff_input_l1c2 = this->ReadTokens(read_input_l1c2, write_input_l1c2, buff_input_l1c2, 1, INPUT_TOKENS_SIZE, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB1,L1_C2,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L1_C2.GetDelay());
        std::cout << i << ",MB1,L1_C2,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l1c2_l2c1 = this->WriteTokens(read_l1c2_l2c1, write_l1c2_l2c1, buff_l1c2_l2c1, 0, L1_C2, t_r_loop, i, ENABLE_CLOCK_GATING);

        // Actor L2_C1
        buff_l1c1_l2c1 = this->ReadTokens(read_l1c1_l2c1, write_l1c1_l2c1, buff_l1c1_l2c1, 0, L1_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l1c2_l2c1 = this->ReadTokens(read_l1c2_l2c1, write_l1c2_l2c1, buff_l1c2_l2c1, 0, L1_C2, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l1c3_l2c1 = this->ReadTokens(read_l1c3_l2c1, write_l1c3_l2c1, buff_l1c3_l2c1, 0, L1_C3, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB1,L2_C1,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L2_C1.GetDelay());
        std::cout << i << ",MB1,L2_C1,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l2c1_l3c1 = this->WriteTokens(read_l2c1_l3c1, write_l2c1_l3c1, buff_l2c1_l3c1, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l2c1_l3c2 = this->WriteTokens(read_l2c1_l3c2, write_l2c1_l3c2, buff_l2c1_l3c2, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l2c1_l3c3 = this->WriteTokens(read_l2c1_l3c3, write_l2c1_l3c3, buff_l2c1_l3c3, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l2c1_l3c4 = this->WriteTokens(read_l2c1_l3c4, write_l2c1_l3c4, buff_l2c1_l3c4, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l2c1_l3c5 = this->WriteTokens(read_l2c1_l3c5, write_l2c1_l3c5, buff_l2c1_l3c5, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l2c1_l3c6 = this->WriteTokens(read_l2c1_l3c6, write_l2c1_l3c6, buff_l2c1_l3c6, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        buff_l2c1_l3c7 = this->WriteTokens(read_l2c1_l3c7, write_l2c1_l3c7, buff_l2c1_l3c7, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);

        // Actor L3_C4
        buff_l2c1_l3c4 = this->ReadTokens(read_l2c1_l3c4, write_l2c1_l3c4, buff_l2c1_l3c4, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB1,L3_C4,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L3_C4.GetDelay());
        std::cout << i << ",MB1,L3_C4,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l3c4_decoder = this->WriteTokens(read_l3c4_decoder, write_l3c4_decoder, buff_l3c4_decoder, 0, L3_C4, t_r_loop, i, ENABLE_CLOCK_GATING);

    }
}

class MB2 : public Tile
{
    public:
        MB2() : Tile(sc_core::sc_module_name("MB2")) {};
    protected:
        void Execute();
};

void MB2::Execute()
{
    for(int i = 0; i < num_iter; i++)
    {
        // Actor L1_C3
        buff_input_l1c3 = this->ReadTokens(read_input_l1c3, write_input_l1c3, buff_input_l1c3, 1, INPUT_TOKENS_SIZE, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB2,L1_C3,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L1_C3.GetDelay());
        std::cout << i << ",MB2,L1_C3,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l1c3_l2c1 = this->WriteTokens(read_l1c3_l2c1, write_l1c3_l2c1, buff_l1c3_l2c1, 0, L1_C3, t_r_loop, i, ENABLE_CLOCK_GATING);

        // Actor L3_C5
        buff_l2c1_l3c5 = this->ReadTokens(read_l2c1_l3c5, write_l2c1_l3c5, buff_l2c1_l3c5, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB2,L3_C5,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L3_C5.GetDelay());
        std::cout << i << ",MB2,L3_C5,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l3c5_decoder = this->WriteTokens(read_l3c5_decoder, write_l3c5_decoder, buff_l3c5_decoder, 0, L3_C5, t_r_loop, i, ENABLE_CLOCK_GATING);

    }
}

class MB3 : public Tile
{
    public:
        MB3() : Tile(sc_core::sc_module_name("MB3")) {};
    protected:
        void Execute();
};

void MB3::Execute()
{
    for(int i = 0; i < num_iter; i++)
    {
    }
}

class MB4 : public Tile
{
    public:
        MB4() : Tile(sc_core::sc_module_name("MB4")) {};
    protected:
        void Execute();
};

void MB4::Execute()
{
    for(int i = 0; i < num_iter; i++)
    {
    }
}

class MB5 : public Tile
{
    public:
        MB5() : Tile(sc_core::sc_module_name("MB5")) {};
    protected:
        void Execute();
};

void MB5::Execute()
{
    for(int i = 0; i < num_iter; i++)
    {
    }
}

class MB6 : public Tile
{
    public:
        MB6() : Tile(sc_core::sc_module_name("MB6")) {};
    protected:
        void Execute();
};

void MB6::Execute()
{
    for(int i = 0; i < num_iter; i++)
    {
        // Actor L3_C7
        buff_l2c1_l3c7 = this->ReadTokens(read_l2c1_l3c7, write_l2c1_l3c7, buff_l2c1_l3c7, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB6,L3_C7,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L3_C7.GetDelay());
        std::cout << i << ",MB6,L3_C7,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l3c7_decoder = this->WriteTokens(read_l3c7_decoder, write_l3c7_decoder, buff_l3c7_decoder, 0, L3_C7, t_r_loop, i, ENABLE_CLOCK_GATING);

    }
}

#endif