
import nest
import pdb

def queryNodeList():

	ret = {}

	node_list = nest.Models(mtype='nodes')
	for node_type in node_list:
		print('Building node type: {}'.format(node_type))
		try:
			m = nest.Create(node_type, 1)
			ret[node_type] = nest.GetStatus(m)
			print('Success.')
		except:
			print('No success.')

	return node_list, ret

if __name__ == '__main__':

	supported_nodes = ['aeif_cond_alpha', 'aeif_cond_exp', 'hh_psc_alpha', 'iaf_cond_alpha', 'iaf_cond_exp', 'iaf_neuron', 'izhikevich', 'poisson_generator', 'spike_generator', 'dc_generator']

	nodes_list, nodes_properties = queryNodeList()
	#synapse_list = querySynapseList()

	#pdb.set_trace()

	#print nodes_list

	print('----------------PROPERTIES:')
	for node_type in nodes_list:
		print('--- NODE_TYPE: {}'.format(node_type))
		if node_type in nodes_properties and node_type in supported_nodes:
			print(nodes_properties[node_type])
		else:
			print('Not in the list.')
