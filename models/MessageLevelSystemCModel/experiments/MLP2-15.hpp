#ifndef EXPERIMENT_HPP
#define EXPERIMENT_HPP

#include <iostream>
#include <cstdlib>
#include <fstream>
#include <tile.hpp>
#include <channel.hpp>
#include <utils.hpp>


/** Cluster sizes definition **/

#define INPUT_TOKENS_SIZE 784
#define L1_TOTAL_TOKENS_OUT 32
#define L1_C1 32
#define L2_TOTAL_TOKENS_OUT 16
#define L2_C1 16
#define L3_TOTAL_TOKENS_OUT 10
#define L3_C1 10

/** Delay definition **/

auto Delay_L1_C1 = DelayVector(INPUT_TOKENS_SIZE, L1_C1);
auto Delay_L2_C1 = DelayVector(L1_TOTAL_TOKENS_OUT, L2_C1);
auto Delay_L3_C1 = DelayVector(L2_TOTAL_TOKENS_OUT, L3_C1);

/** Event definition **/

sc_core::sc_event   write_input_l1c1, read_input_l1c1, 
                    write_l1c1_l2c1, read_l1c1_l2c1, 
                    write_l2c1_l3c1, read_l2c1_l3c1, 
                    write_l3c1_output, read_l3c1_output; 

/** Buffer availability definition **/

bool buff_input_l1c1 = 1;
bool buff_l1c1_l2c1 = 1;
bool buff_l2c1_l3c1 = 1;
bool buff_l3c1_output = 1;

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

        // Actor L2_C1
        buff_l1c1_l2c1 = this->ReadTokens(read_l1c1_l2c1, write_l1c1_l2c1, buff_l1c1_l2c1, 0, L1_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB0,L2_C1,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L2_C1.GetDelay());
        std::cout << i << ",MB0,L2_C1,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l2c1_l3c1 = this->WriteTokens(read_l2c1_l3c1, write_l2c1_l3c1, buff_l2c1_l3c1, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);

        // Actor L3_C1
        buff_l2c1_l3c1 = this->ReadTokens(read_l2c1_l3c1, write_l2c1_l3c1, buff_l2c1_l3c1, 0, L2_C1, t_r_loop, i, ENABLE_CLOCK_GATING);
        std::cout << i << ",MB0,L3_C1,START," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        sc_core::wait(Delay_L3_C1.GetDelay());
        std::cout << i << ",MB0,L3_C1,STOP," << sc_core::sc_time_stamp().value()/1000 << std::endl;
        buff_l3c1_output = this->WriteTokens(read_l3c1_output, write_l3c1_output, buff_l3c1_output, 1, L3_C1, t_r_loop, i, ENABLE_CLOCK_GATING);

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
    }
}

#endif