###
#
# 	Sample NEST script for benchmarking snapshot capabilities.
#
# 	Authon: Igor Peric (peric@fzi.de)
#
###

import numpy as np
import nest as sim
import imp
import cPickle as pickle
import logging
import pdb
import string

import hickle
import ujson

import h5py

import time

# serializing SLILiteral
from nest.pynestkernel import SLILiteral
import copy_reg
def recreate_sli(name):
    return SLILiteral(name)
def pickle_sli(sli_literal):
    return recreate_sli, (sli_literal.name,)
copy_reg.pickle(SLILiteral, pickle_sli)

def build_params_dict() :

	params = {
		'neurons': {}, # lists of parameters keyed with neuron NEST types
		'synapses': {}, # lists of parameters keyed with PyNN synapse types
		'pynn2nest': {}, # NEST names of equivalent PyNN synapse names without suffixes (_1, _2,...) 
		'nest2pynn': {}
	}

	###### supported neurons

	model = 'iaf_cond_alpha'
	params['neurons'][model] = [ 'E_ex', 'vp', 'V_reset', \
		'V_th', 'tau_minus', 'I_e', 'g_L', 't_spike', 'E_L', \
		'tau_syn_ex', 'V_m', 'tau_minus_triplet', 't_ref', \
		'E_in', 'C_m', 'tau_syn_in' ]

	#model = 'iaf_cond_exp'
	#params[model] = [ 'E_ex', 'vp', 'dg_in', 'V_reset', 'V_peak', \
	#	'V_th', 'tau_minus', 'I_e', 'g_L', 't_spike', 'tau_w', 'E_L', \
	#	'dg_ex','tau_syn_ex', 'Delta_T', 'V_m', 'tau_minus_triplet', 't_ref', \
	#	'a', 'b', 'E_in', 'C_m', 'g_ex', 'g_in', 'w',' tau_syn_in' ]

	###### supported synapses

	model = 'tsodyks_synapse_projection'
	params['synapses'][model] = [ 'source', 'target', 'weight', 'tau_psc', \
		'tau_rec', 'tau_fac', 'delay', 'U', 'u', 'sizeof', 'x', 'y']

	###### nest_names
	params['nest_names']['tsodyks_synapse_projection'] = 'tsodyks2_synapse'

	return params

def build_brain(brain_file_path):
	print('Loading brain from file: {0}'.format(brain_file_path))
	brain_generator = imp.load_source('_dummy_brain', brain_file_path)
	# root_population = brain_generator.Brain()
	#brain_generator.create_brain()

	#return root_population

def stream_input(brain):

	# build recording devices
	# v_meter = sim.Create('voltmeter')

	# build input devices
	# ...

	pass

# removes suffix from name
def get_real_model_name(model, params):
	real_model_name = None
	for model_name in params:
		if model.startswith(model_name):
			return model_name
	return real_model_name 

# accepts an ID of node as single int
# node_type can be 'neuron' or 'synapse'
def parse_node_info(node_id, node_type, params):

	params = params[node_type]

	#pdb.set_trace()
	if node_type == 'neurons':
		model = sim.GetStatus([node_id], 'model')[0].name
	else:
		model = sim.GetStatus([node_id], 'synapse_model')[0].name

	print('model: {}'.format(model))

	# search for names alike, to circumvent suffixes added by PyNN to model names
	real_model_name = get_real_model_name(model, params)

	# check if the neuron model is supported
	if real_model_name not in params:
		print("Network contains model unsupported by snapshot feature: {}.".format(model))

	# get the parameters specific for the model
	node_desc = sim.GetStatus([node_id], params[real_model_name])[0]
	L_params = len(params[real_model_name])
	
	return model, node_desc

def save_snapshot(brain, save_file_path):

	# build dict of params
	params = build_params_dict()

	# open the .h5 file for writing
	f = h5py.File(save_file_path, "w")
	
	# precompute sizes of synapse populations of each type
	running_pointer = {}
	synapse_type_counter = {}
	for supported_type in params['synapses']:
		# create running pointer dictionary for every supported synapse type
		running_pointer[supported_type] = 0
		supported_type = params['nest_names'][supported_type] # convert PyNN name to NEST name
		synapses = sim.GetConnections(synapse_model=supported_type)
		synapse_type_counter[supported_type] = len(synapses)
		print('----> There are {} synapses of type {}.'.format(len(synapses), supported_type))

	# for each supported neuron type...
	for neuron_model in params['neurons']:

		nodes = sim.GetLeaves([0], {'model': neuron_model}) # accepts a list of subnetwork IDs... ID=0 is root subnet
		nodes = nodes[0] # convert from tupple to scalar
		
		L_nodes = len(nodes)
		L_params = len(params['neurons'][neuron_model])

		# allocate dataset in the file
		neuron_storage = f.create_dataset(neuron_model, (L_nodes, L_params), dtype='f')

		for k in range(len(nodes)):
			neuron = nodes[k]

			# get numpy array describing the node according to schema
			model, param_list = parse_node_info(neuron, 'neurons', params)
			# store data into .h5 file
			neuron_storage[k] = param_list

			# get synapses for this neuron (list of IDs of postsynaptic neurons)
			ps_neurons = sim.GetConnections([neuron])
			print('ps_neurons: {}'.format(ps_neurons))
			for ps_neuron in ps_neurons:
				#pdb.set_trace()
				synapse_info = parse_node_info(ps_neuron, 'synapses', params)
				print(synapse_info)

	f.close()
	print('Done saving.')

def load_snapshot(path):
	
	# clear kernel
	sim.ResetKernel()
	# confirm that everything is resetted
	#syns = sim.GetConnections()
	#print('Connections:')
	#print(syns)

	# load the description of the network
	print('--- reading file...')
	t1 = time.clock()
	snap_file = open(path, 'r')
	brain_data = pickle.load(snap_file)
	t2 = time.clock()
	print('--- Done. It took {} seconds.'.format(t2-t1))
	#brain_data = hickle.load(snap_file)
	#brain_data = ujson.load(snap_file)
	
	#pdb.set_trace()

	print('--- creating nodes...')
	t1 = time.clock()
	# recreate nodes
	nodes = brain_data['nodes']
	for node in nodes:
		node_desc = node
		# handle node type (neuron, recording device, etc.)
		node_type = node_desc['model']
		#print('Node type: {}'.format(node_type))
		# remove irelevant parameters
		
		params = build_params_dict(node_desc)
		# handle recordables 
		# recordables = node_desc['recordables']
		my_node = sim.Create(node_type, 1, params=params)
		# for rec in recordables:
		# 	my_node.record()
	t2 = time.clock()
	print('--- Done. It took {} seconds.'.format(t2-t1))
	#sim.Create(nodes)

	# recreate connections
	print('--- creating connections...')
	connections = brain_data['connections']
	sim.DataConnect(connections)
	t1 = time.clock()
	print('--- Done. It took {} seconds.'.format(t1-t2))

	# check if the network has been loaded properly
	#syns = sim.GetConnections()
	#syn_desc = sim.GetStatus(syns)
	#print('Connections after load:')
	#print(syn_desc)

def run():
	
	# build brain
	print('Building brain...')
	t1 = time.clock()
	#brain_file_path = '/home/igor/hbp/brains/dummy_brain.py'
	brain_file_path = '/home/igor/hbp/brains/braitenberg.py'
	brain = build_brain(brain_file_path)
	t2 = time.clock()
	print('Done, it took {} seconds.'.format(t2-t1))

	print('Streaming input...')
	# stream certain input into the brain, thus changing it
	stream_input(brain)
	t1 = time.clock()
	print('Done, it took {} seconds.'.format(t1-t2))
	# save snapshot to file
	print('Saving brain snapshot...')
	snap_file_path = '/home/igor/hbp/brains/snapshot_dummy_brain.brain'
	save_snapshot(brain, snap_file_path)
	t2 = time.clock()
	print('Done, it took {} seconds.'.format(t2-t1))

	# instantiate new brain from saved one
	#print('Loading brain snapshot...')
	#new_brain = load_snapshot(snap_file_path)
	#t1 = time.clock()
	#print('Done, it took {} seconds.'.format(t1-t2))

	sim.PrintNetwork()

if __name__ == "__main__":
	run()