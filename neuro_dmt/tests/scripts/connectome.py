"""A script to run some connectome validations"""
import time
import datetime
from bluepy.v2.circuit import Circuit
from dmt.vtk.measurement import StatisticalMeasurement
from dmt.vtk.measurement.parameters import get_grouped_values
from neuro_dmt.models.bluebrain.circuit.parameters import PreMtype, PostMtype
from neuro_dmt.models.bluebrain.circuit.measurements.connectome \
    import PairSynapseCount

cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)

mtype_pre = PreMtype(circuit)
mtype_post = PostMtype(circuit)

syn_count = StatisticalMeasurement(method=PairSynapseCount(circuit),
                                   by=[mtype_pre, mtype_post])


def usage():
    print("Explain how to use.")

if __name__=="__main__":
    today = datetime.date.today().strftime("%Y%m%d")
    now = time.localtime()
    print("TIME: {}-{}".format(today, now))
    print("Testing synapse count.")
    with open("./output.log", "w") as f:
        f.write("TIME: {}\n".format(now))
        f.write("Testing synapse count.")
    measurement = syn_count(sample_size=2)
    now = time.localtime()
    print("TIME: {}-{}".format(today, now))
    print("Synapses counted for {} pathways."\
          .format(measurement.data.shape[0]))
    with open("./output.log", "w") as f:
        f.write("TIME: {}\n".format(now))
        f.write("Synapses counted for {} pathways."\
                .format(measurement.data.shape[0]))
    print("writing data frame to CSV")
    measurement.data.to_csv("./pathway_synapse_count.csv")
