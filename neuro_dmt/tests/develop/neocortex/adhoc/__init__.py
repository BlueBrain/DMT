"Some adhoc tests"

import numpy as np
import pandas as pd
from bluepy.v2.circuit\
    import Circuit
from bluepy.v2.enums\
    import Cell
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.tests.develop.circuits\
    import *

logger = Logger(
    "Adhoc tests for the isocortex connetome",
    level=Logger.level.DEBUG)


proj68_circuits=\
    os.path.join(
        "/gpfs/bbp.cscs.ch",
        "project/proj68",
        "circuits")
sscx_circuit_nrn_config=\
    os.path.join(
        proj68_circuits,
        "O1/20190307",
        "connectome",
        "functional-nrn", "All",
        "CircuitConfig")
sscx_circuit_nrn=\
    Circuit(sscx_circuit_nrn_config)
sscx_circuit_son_aff_config=\
    os.path.join(
        proj68_circuits,
        "O1/20190307",
        "connectome",
        "functional", "All",
        "CircuitConfig-aff")
sscx_circuit_son_eff_config=\
    os.path.join(
        proj68_circuits,
        "O1/20190307",
        "connectome",
        "functional", "All",
        "CircuitConfig-eff")
mtypes=\
    sscx_circuit_nrn.cells.mtypes
sscx_dia_measurement_index=\
    pd.MultiIndex.from_tuples(
        tuples=[(mtype, mtype, region)
               for mtype in mtypes
               for region in ["mc{}_Column".format(c) 
                              for c in range(7)]],
    names=["pre_mtype", "post_mtype", "region"])
sscx_measurement_index=\
    pd.MultiIndex.from_tuples(
        tuples=[(pre, post, region)
                for pre in mtypes
                for post in mtypes
                for region in ["mc{}_Column".format(c) 
                              for c in range(7)]],
        names=["pre_mtype", "post_mtype", "region"])
iso_dia_measurement_index=\
    pd.MultiIndex.from_tuples(
        tuples=[(mtype, mtype, region)
                for mtype in mtypes
                for region in ["{}@{}".format(r, h)
                                for r in ["ACAd", "GU", "SSp-ll", "SSp-ul", "VISp"]
                                for h in ["left", "right"]]],
    names=["pre_mtype", "post_mtype", "region"])

def sscx_circuit_config(
        connectome_type,
        direction):
    """..."""
    if connectome_type == "nrn":
        return sscx_circuit_nrn_config
    if direction == "eff":
        return sscx_circuit_son_eff_config
    return sscx_circuit_son_aff_config

def iso_circuit_config(
        region,
        direction):
    return\
        os.path.join(
            proj68_circuits,
            "Isocortex/20190307",
            "connectome",
            "functional",
            region,
            "CircuitConfig-{}".format(direction))
    
output_path=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/home/sood/",
        "work/validations/",
        "release", "neocortex-2019", "arxiv",
        "validation", "mouse", "somatosensory_cortex",
        "connectome", "adhoc")

def get_number_connections(
        connectome,
        pre_mtype,
        post_mtype,
        region):
    """..."""
    pre_cell_type={
        "mtype": pre_mtype}
    post_cell_type={
        "mtype": post_mtype}
    if region:
        pre_cell_type["region"]=\
            region
        post_cell_type["region"]=\
            region
    connections=\
        connectome.iter_connections(
            pre_cell_type,
            post_cell_type)
    number=\
        sum(1 for _ in connections)
    print(
        "pre_mtype {}, post_mtype {}, region {} connections {}"\
        .format(pre_mtype, post_mtype, region, number))
    return number

def get_sscx_number_connections(
        pre_mtype,
        post_mtype,
        region,
        connectome_type,
        direction):
    """..."""
    circuit_config=\
        sscx_circuit_config(
            connectome_type,
            direction)
    conn = Circuit(circuit_config).connectome
    return get_number_connections(conn, pre_mtype, post_mtype, region)

def get_iso_number_connections(
        pre_mtype,
        post_mtype,
        region):
    """..."""
    circuit_config=\
        iso_circuit_config(region)
    conn = Circuit(circuit_config).connectome
    
    return get_number_connections(conn, pre_mtype, post_mtype, region)

def get_synapse_count(
        connectome,
        pre_mtype,
        post_mtype,
        region):
    """..."""
    synapse_counts=\
        connectome.iter_connections(
            {"mtype": pre_mtype, "region": region},
            {"mtype": post_mtype, "region": region},
            return_synapse_count=True)
    return {"mean": np.mean(list(synapse_counts)),
            "std":  np.std(list(synapse_counts))}



def run_iso_connections(
        regions=["ACAd", "GU", "SSp-ll", "SSp-ul", "VISp"],
        only_diagonal=True):
    """..."""
    def get_measurement_index(region):
        return pd.MultiIndex.from_tuples(
            tuples=[(mtype, mtype, region) for mtype in mtypes],
            names=["pre_mtype", "post_mtype", "region"])
    for region in regions:
        print(
            "measure {} for region {}"\
            .format(
                "only symmetric pathways" if only_diagonal else "all pathways",
                region))
        measurement_index=\
            get_measurement_index("{}@left".format(region))
        measurement=\
            pd.DataFrame(
                [{"number": get_iso_number_connections(*row)}
                 for row in measurement_index],
                index=meaurement_index)
        print(
            "total number of connections in symmetric pathways in {} is {}"\
            .format(region, measurement.sum()))
        measurement.to_csv(
            os.path.join(
                output_path,
                "iso_circuit_{}_dia.csv".format(region)))

