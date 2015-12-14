import nest as sim
import imp

brain_file_path = '/home/igor/hbp/brains/braitenberg.py'
#brain_generator = imp.load_source('_dummy_brain', brain_file_path)

pop1 = sim.Create("iaf_neuron", params={"tau_minus": 30.0})
pop2 = sim.Create("iaf_neuron", params={"tau_minus": 30.0})
K = 1
conn_dict = {"rule": "fixed_indegree", "indegree": K}
#syn_dict = {"model": "stdp_synapse", "alpha": 1.0}
syn_dict = {"model": "tsodyks2_synapse"}
sim.Connect(pop1, pop2, conn_dict, syn_dict)

nodes = sim.GetLeaves([0])
conns = sim.GetConnections(nodes)

print(conns)