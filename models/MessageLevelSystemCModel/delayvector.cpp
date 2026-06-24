/**
 ** File: delayvector.cpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#include <delayvector.hpp>
#include <cstdlib>
#include <iostream>
#include <gsl/gsl_randist.h>
#include <gsl/gsl_statistics_double.h>
#include <algorithm>

unsigned int GetDelayLoop(unsigned int i){
    return 12*i + 11;
}

DelayVector::DelayVector(const char *path, DISTRIBUTION distribution)
    : delayindex(0)
    , rng(NULL)
    , distribution(distribution)
    , layer_type(NOT_NN_LAYER)
{
    this->ReadDelayVector(path);
    this->rng = gsl_rng_alloc(gsl_rng_default);
    // By default, the random number generator gets seeded with 0
    // This shall not be changed to get reproducible results
}

DelayVector::DelayVector(std::string path, DISTRIBUTION distribution)
    : delayindex(0)
    , rng(NULL)
    , distribution(distribution)
    , layer_type(NOT_NN_LAYER)
{
    this->ReadDelayVector(path.c_str());
    this->rng = gsl_rng_alloc(gsl_rng_default);
    // By default, the random number generator gets seeded with 0
    // This shall not be changed to get reproducible results
}

DelayVector::DelayVector(unsigned int nb_neurons_previous_layer, unsigned int nb_neurons_this_layer) // Dense Layer (LibFANN, compatible older versions)
    : delayindex(0)
    , rng(NULL)
    , nb_neurons_previous_layer(nb_neurons_previous_layer)
    , nb_neurons_this_layer(nb_neurons_this_layer)
    , delay_coefA(47)
    , delay_coefB(146) //LibFANN - SIGMOID:17001, RELU:146
    , delay_coefC(39)
    , layer_type(DENSE_LIBFANN)
{
}

// Added layer type argument for the CNN application
//NOTE: This procedure can be used both for fully-connected layer and pooling.
DelayVector::DelayVector(unsigned int coefficient_1, unsigned int coefficient_2, NN_LAYER_TYPE layer_type, NN_ACTIVATION_TYPE activation_type) // Dense Layer CNN
    : delayindex(0)
    , rng(NULL)
    , coefficient_1(coefficient_1) // if FC: nb_neurons_previous_layer, if Pooling: number of filters
    , coefficient_2(coefficient_2) // if FC: nb_neurons_this_layer, if Pooling: input image size
    , delay_coefA(50.00094763) // 40 - 47
    , delay_coefC(31.145031640157413) // 39 -39
    , layer_type(layer_type)
{
    if(layer_type == MAXPOOLING){
        delay_coefC = 106.2099835381523;
        delay_coefA = 99.3564911;
        delay_coefB = 0;
    }
    else{ //Fully-connected
        delay_coefC = 31.145031640157413;
        delay_coefA = 50.00094763;
        if(activation_type == SIGMOID){
            delay_coefB = 43540;
        }
        if(activation_type == RELU){
            delay_coefB = 105.64417806876287; //69.342600
        }
        if(activation_type == NONE){
            delay_coefB = 52.924848515984515;
        }
    }
}

//Convolution
DelayVector::DelayVector(unsigned int number_of_filters, unsigned int input_img_dim, unsigned int filter_size, NN_LAYER_TYPE layer_type, NN_ACTIVATION_TYPE activation_type)
    : delayindex(0)
    , rng(NULL)
    , number_of_filters(number_of_filters)
    , input_img_dim(input_img_dim)
    , filter_size(filter_size)
    , delay_coefA(77) //D_a = 40
    , delay_coefC(28) //D_c = 28
    , layer_type(layer_type)
{
    if(activation_type == SIGMOID){
        delay_coefB = 42+73+43540; // 42: variable initialization, 73: adding bias, Sigmoid: 43540 +- 4477, ReLU: 109.422000
    }
    if(activation_type == RELU){
        delay_coefB = 631.3270408163265; //old 109.422000, new 224
    }
    if(activation_type == NONE){
        delay_coefB = 42+73;
    }
}

//Actor delay directly passed
DelayVector::DelayVector(unsigned int mydelay, NN_LAYER_TYPE layer_type)
    : delayindex(0)
    , rng(NULL)
    , delay_coefA(mydelay)
    , layer_type(layer_type)
{
}

sc_core::sc_time DelayVector::GetDelay()
{
    double delay;

    if(layer_type == NOT_NN_LAYER){

        switch(this->distribution)
        {
            case DISTRIBUTION::INJECTED:
                delay = this->GetInjectedDelay();
                break;

            case DISTRIBUTION::GAUSSIAN:
                delay = this->GetGaussianDelay();
                break;

            case DISTRIBUTION::UNIFORM:
                delay = this->GetUniformDelay();
                break;

            case DISTRIBUTION::WCET:
                delay = this->GetWCETDelay();
                break;
        }

    }

    else{

        delay = this->GetFunctionDelay();

    }

    return sc_core::sc_time(delay, sc_core::SC_NS);
}

double DelayVector::GetFunctionDelay()
{
    unsigned int delay = 0;

    //coefficient_1 means if FC: nb_neurons_previous_layer, if Pooling: number of filters
    //coefficient_2 means if FC: nb_neurons_this_layer, if Pooling: input image size
    if(layer_type == DENSE){
        delay = coefficient_2 * ((coefficient_1) * delay_coefA + delay_coefB) + delay_coefC;
    }
    if(layer_type == CONVOLUTION){
        delay = delay_coefC + number_of_filters*input_img_dim*(delay_coefB + filter_size*delay_coefA);
    }
    if(layer_type == MAXPOOLING){
        delay = delay_coefC + coefficient_1 * coefficient_2 * delay_coefA;
    }
    if(layer_type == DENSE_LIBFANN){
        delay = nb_neurons_this_layer * ((nb_neurons_previous_layer) * delay_coefA + delay_coefB) + delay_coefC;
    }
    if(layer_type == OTHER){ //Direct passing delay
        delay = delay_coefA;
    }
    return delay;
}



double DelayVector::GetInjectedDelay()
{
    double delay = this->delayvector[this->delayindex];
    this->delayindex = (this->delayindex + 1) % this->delayvector.size();

    return delay;
}



double DelayVector::GetGaussianDelay()
{
    auto delay = gsl_ran_gaussian(this->rng, this->sigma);
    delay += this->mu;

    return delay;
}



double DelayVector::GetUniformDelay()
{
    auto delay = gsl_ran_flat(this->rng, this->BCET, this->WCET);

    return delay;
}



double DelayVector::GetWCETDelay()
{
    return this->WCET;
}



void DelayVector::ReadDelayVector(const char *path)
{
    std::ifstream ifs;
    ifs.open(path);

    // Initialize min/max with opposite extremes
    // to approach to the actual values from the file
    this->WCET = 0.0;
    this->BCET = std::numeric_limits<decltype(this->BCET)>::max();

    for(std::string line; std::getline(ifs, line); )
    {
        double time;
        try
        {
            time = std::stod(line);
        }
        catch(std::exception &e)
        {
            std::cerr << "Parsing line \""
                      << line
                      << "\" failed."
                      << "This line will be ignored!\n";
        }

        this->delayvector.emplace_back(time);
        if(time > this->WCET)
            this->WCET = time;
        if(time < this->BCET)
            this->BCET = time;

    }

    // Shuffle delay vector to make sure it is not just a repetition of the measured data
    std::random_shuffle(this->delayvector.begin(), this->delayvector.end());

    // Get further properties from the measured data
    double *data = this->delayvector.data();
    size_t  n    = this->delayvector.size();
    this->sigma  = gsl_stats_sd(  data, 1, n);
    this->mu     = gsl_stats_mean(data, 1, n);

    ifs.close();
    return;
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

