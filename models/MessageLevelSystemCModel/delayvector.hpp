/**
 ** File: delayvector.hpp
 ** License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
 **          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
 **/

#ifndef DELAYVECTOR_HPP
#define DELAYVECTOR_HPP

#include <vector>
#include <string>
#include <systemc.h>
#include <cstdlib>
#include <gsl/gsl_rng.h>

enum DISTRIBUTION
{
    INJECTED,
    GAUSSIAN,
    UNIFORM,
    WCET
};

enum NN_LAYER_TYPE //Neural network layer type
{
    NOT_NN_LAYER, //For the other delay functions based on probabilistic distribution
    DENSE,
    CONVOLUTION,
    MAXPOOLING,
    DENSE_LIBFANN,
    OTHER
};

enum NN_ACTIVATION_TYPE //Neural network layer type
{
    SIGMOID, //For the other delay functions based on probabilistic distribution
    RELU,
    NONE
};

// Important:
// Internal, this class works with doubles for the delays.
// A delay's unit is clock cycle.
// The external interfaces should be of type sc_time

class DelayVector
{
    public:
        DelayVector(const char *path, DISTRIBUTION distribution = DISTRIBUTION::INJECTED);
        DelayVector(std::string path, DISTRIBUTION distribution = DISTRIBUTION::INJECTED);
        DelayVector(unsigned int nb_neurons_previous_layer, unsigned int nb_neurons_this_layer); // FC LibFANN
        DelayVector(unsigned int coefficient_1, unsigned int coefficient_2, NN_LAYER_TYPE layer_type, NN_ACTIVATION_TYPE activation_type); // Dense Layer + MaxPooling CNN
        DelayVector(unsigned int number_of_filters, unsigned int input_img_dim, unsigned int filter_size, NN_LAYER_TYPE layer_type, NN_ACTIVATION_TYPE activation_type); // Convolution CNN
        DelayVector(unsigned int delay, NN_LAYER_TYPE layer_type); // Other layers without model (just pass directly the actor's delay)

        sc_core::sc_time GetDelay();

    private:
        double GetInjectedDelay();
        double GetGaussianDelay();
        double GetUniformDelay();
        double GetWCETDelay();
        double GetFunctionDelay();
        void ReadDelayVector(const char *path);

        // This vector holds all measured delay
        std::vector<double> delayvector;

        // These variables are properties of the measured delay are
        double BCET;  // Lowest delay
        double WCET;  // Highest delay
        double sigma;
        double mu;
        double delay_coefA;
        double delay_coefB;
        double delay_coefC;

        // Some variables for accessing the delays
        unsigned int delayindex; // Next delay in delay vector
        unsigned int nb_neurons_this_layer;
        unsigned int nb_neurons_previous_layer;
        unsigned int coefficient_1;
        unsigned int coefficient_2;

        unsigned int number_of_filters;
        unsigned int input_img_dim;
        unsigned int filter_size;

        NN_LAYER_TYPE layer_type;
        NN_ACTIVATION_TYPE activation_type;
        gsl_rng *rng;   // Random number generator for Normal/Uniform distribution
        DISTRIBUTION distribution;
};

#endif
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

