###
#
# 	Sample brain description written in PyNN 0.8
#
# 	Authon: Igor Peric (peric@fzi.de)
#
###

import pdb
import pyNN.nest as sim

in_layer1 = sim.Population(5, sim.IF_cond_alpha())
in_layer2 = sim.Population(5, sim.HH_cond_exp())
in_layer3 = sim.Population(5, sim.IF_cond_alpha())

stdp_synapse = {'model': 'stdp_synapse', \
    'weight': 2.5, \
    'delay': {'distribution': 'uniform', 'low': 0.8, 'high': 2.5}, \
    'alpha': {'distribution': 'normal_clipped', 'low': 0.5, 'mu': 5.0, 'sigma': 1.0} }

syn_params = {'U': 1.0, 'tau_rec': 0.0, 'tau_facil': 0.0}
SYN = sim.StaticSynapse(weight=2, delay=3)

SYN = sim.STDPMechanism( timing_dependence=sim.SpikePairRule(tau_plus=20.0, tau_minus=20.0,
                                                    A_plus=0.01, A_minus=0.012),
                weight_dependence=sim.AdditiveWeightDependence(w_min=0, w_max=0.0000001),
                weight=0.00000005,
                delay=1,
                dendritic_delay_fraction=1)

sim.Projection(presynaptic_population= in_layer1 ,\
               postsynaptic_population= in_layer2 ,\
               connector=sim.AllToAllConnector(),\
               synapse_type=SYN,\
               receptor_type='excitatory')

SYN = sim.TsodyksMarkramSynapse(weight=abs(2),
                                delay=3, **syn_params)

sim.Projection(presynaptic_population= in_layer2 ,\
               postsynaptic_population= in_layer3 ,\
               connector=sim.AllToAllConnector(),\
               synapse_type=SYN,\
               receptor_type='excitatory')

