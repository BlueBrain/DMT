"""A script to run some connectome validations"""
import time
import datetime
from bluepy.v2.circuit import Circuit
from dmt.vtk.measurement import StatisticalMeasurement
from dmt.vtk.measurement.parameters import get_grouped_values
from neuro_dmt.models.bluebrain.circuit.parameters import PreMtype, PostMtype
from neuro_dmt.models.bluebrain.circuit.measurements.connectome \
    import PairSynapseCount

cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/S1.v6a/20171206/CircuitConfig"
circuit = Circuit(cpath)

mtype_pre = PreMtype(circuit)
mtype_post = PostMtype(circuit)

syn_count = StatisticalMeasurement(method=PairSynapseCount(circuit),
                                   by=[mtype_pre, mtype_post])

def log_message(msg):
    print("TIME: {}".format(time.localtime()))
    print(msg)
    with open("./connectome_test.log", "a") as f:
        f.write("TIME: {}".format(time.localtime()))
        f.write(msg)

def usage():
    print("Explain how to use.")

if __name__=="__main__":
    today = datetime.date.today().strftime("%Y%m%d")
    now = time.localtime()
    log_message("Testing synapse count.")
    measurement = syn_count(sample_size=100)
    now = time.localtime()
    log_message("Synapses counted for {} pathways."\
                .format(measurement.data.shape[0]))
    log_message("writing data frame to CSV")
    measurement.data.to_csv("./pathway_synapse_count.csv")
