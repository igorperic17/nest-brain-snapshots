###
#
# 	Sample brain description written in pure NEST.
#
# 	Authon: Igor Peric (peric@fzi.de)
#
###

import nest
import pdb

class Brain:

	def build_neurons(self):

		# build populations
		#ndict = [{"I_e": 200.0, "tau_m": 20.0} for i in range(3)]
		self.in_layer = nest.Create("iaf_neuron", 300)
		self.hidden_layer = nest.Create("iaf_neuron", 500)
		self.out_layer = nest.Create("iaf_neuron", 300)

	def connect_neurons(self):
		stdp_synapse = {'model': 'stdp_synapse',
            'weight': 2.5,
            'delay': {'distribution': 'uniform', 'low': 0.8, 'high': 2.5},
            'alpha': {'distribution': 'normal_clipped', 'low': 0.5, 'mu': 5.0, 'sigma': 1.0}
           }
		nest.Connect(self.in_layer, self.hidden_layer, 'all_to_all', syn_spec = stdp_synapse)
		nest.Connect(self.hidden_layer, self.out_layer, 'all_to_all')
		#nest.Connect(self.out_layer, self.v_meter)

	# Method that builds the NEST network 
	def __init__(self, with_connection=True):
		self.build_neurons()
		self.connect_neurons()

if __name__ == '__main__':
	pass

	nest_object = Brain()

	#################################### labels
	in_population = nest_object.in_layer
	reward_population = nest_object.hidden_layer[0:3]
	out_population = nest_object.out_layer