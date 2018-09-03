"""A script to run some connectome validations"""
import time
import datetime
import numpy as np
from bluepy.v2.circuit import Circuit
from dmt.vtk.measurement import StatisticalMeasurement
from dmt.vtk.measurement.parameters import get_grouped_values
from neuro_dmt.models.bluebrain.circuit.parameters import PreMtype, PostMtype
from neuro_dmt.models.bluebrain.circuit.measurements.connectome \
    import PairSynapseCount, EfferentSynapseCount

if __name__ == "__main__":
    cpath\
        = "/gpfs/bbp.cscs.ch/project/proj64/circuits/S1.v6a/20171206/CircuitConfig"
    circuit = Circuit(cpath)
    cells = circuit.cells.get().index
    eff_syn_count = EfferentSynapseCount(circuit)

    print("TIME: {}".format(time.localtime()))
    print("Count number of synapses.")
    syn_count_samples = []
    for i in range(20):
        n = np.sum([eff_syn_count(g) for g in np.random.choice(cells, 1000)])
        syn_count_samples.append(n)
        print("TIME: {}".format(time.localtime()))
        print("sample {} synapse number {}".format(i, n))

    mean = np.mean(syn_count_samples)
    std  = np.std(syn_count_samples)
    print("TIME: {}".format(time.localtime()))
    print("mean: {}, std: {}".format(mean, std))

    


