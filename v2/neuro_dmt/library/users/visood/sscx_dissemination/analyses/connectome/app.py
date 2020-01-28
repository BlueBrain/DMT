"""
Analysis app to run from command line.
"""

import sys
import os
import yaml
from dmt.tk.journal import Logger
from neuro_dmt.analysis.reporting import CheetahReporter
from neuro_dmt.models.bluebrain.circuit.model import\
    BlueBrainCircuitModel,\
    CircuitProvenance
from neuro_dmt.models.bluebrain.circuit.adapter import\
    BlueBrainCircuitAdapter
from neuro_dmt.models.bluebrain.circuit.mock.circuit import\
    MockCircuit
from neuro_dmt.models.bluebrain.circuit.mock.test.mock_circuit_light import\
    circuit_composition,\
    circuit_connectivity
from neuro_dmt.library.users.visood.sscx_dissemination.analyses.connectome\
    import ConnectomeAnalysesSuite


LOGGER = Logger(client=__file__, level="INFO")

def _chunked(mtypes):
    """..."""
    return {
        "mtypes_L2_L3": [mtype for mtype in mtypes
         if "L2_" in mtype or "L23_" in mtype or "L3_" in mtype],
        "mtypes_L1_L4": [mtype for mtype in mtypes
         if "L1_" in mtype or "L4_" in mtype],
        "mtypes_L5": [mtype for mtype in mtypes
         if "L5_" in mtype],
        "mtypes_L6": [mtype for mtype in mtypes
         if "L6_" in mtype]}

def _load_mtypes(path_source_file):
    try:
        with open(path_source_file, 'r') as source_file:
            try:
                return {
                    "mtypes_chosen": yaml.load(
                        source_file, Loader=yaml.FullLoader)}
            except AttributeError:
                return yaml.load(source_file)
    except FileNotFoundError:
        return {}
    return {}

def _load_circuit(path_circuit_data):
    if path_circuit_data == "MOCK":
        bluepy_mock_circuit =\
            MockCircuit.build(
                circuit_composition,
            circuit_connectivity)
        return\
            BlueBrainCircuitModel(
                bluepy_mock_circuit,
                label="BlueBrainCircuitModelMockLight")
    return\
        BlueBrainCircuitModel(
            path_circuit_data=path_circuit_data,
            provenance=CircuitProvenance(
                label="SSCxDisseminationBioM",
                authors=["BBP Team"],
                release_date=os.path.basename(path_circuit_data),
                uri=path_circuit_data,
                animal="Wistar Rat",
                age="P14",
                brain_region="SSCx")) 

if __name__ == "__main__":
    index_argv = 1
    try:
        path_circuit_data =\
            sys.argv[index_argv]
        index_argv += 1
    except IndexError:
        raise Exception(
            """
            Missing path to the circuit.
            Pleas enter `MOCK` to run for a mock circuit.
            """)
    try:
        path_source_pre_mtypes = sys.argv[index_argv]
        index_argv += 1
    except IndexError:
        raise Exception(
            """
            Missing path to yaml file containing pre mtypes.
            Please enter 'NONE' to analyze all mtypes in the circuit.
            """)
    try:
        path_source_post_mtypes = sys.argv[index_argv]
        index_argv += 1
    except IndexError:
        raise Exception(
            """
            Missing path to yaml file containing post mtypes.
            Please enter 'NONE' to analyze all mtypes in the circuit.
            """)
    try:
        sample_size = int(sys.argv[index_argv])
        index_argv += 1
    except IndexError:
        sample_size = 20

    pre_mtypeses =\
        _load_mtypes(path_source_pre_mtypes)
    post_mtypeses =\
        _load_mtypes(path_source_post_mtypes)

    LOGGER.info(
        """
        Load the circuit at {}
        """.format(
            path_circuit_data))
    circuit_model =\
        _load_circuit(
            path_circuit_data)
    adapter =\
        BlueBrainCircuitAdapter()

    if not pre_mtypeses:
        pre_mtypeses =\
            _chunked(
                adapter.get_mtypes(circuit_model))
    if not post_mtypeses:
        post_mtypeses =\
            _chunked(
                adapter.get_mtypes(circuit_model))

    for kind_post_mtypes, post_mtypes in post_mtypeses.items():
        LOGGER.info(
            """
            Compute afferent connectivity for post-synaptic cell mtypes:
            \t {}.
            """.format(kind_post_mtypes))
        suite_analyses =\
            ConnectomeAnalysesSuite(
                sample_size=sample_size,
                post_synaptic_mtypes=post_mtypes)
        reporter =\
            CheetahReporter(
                path_output_folder=os.path.join(
                    suite_analyses.path_reports,
                    "analyses"))
        report =\
            suite_analyses.analysis_number_afferent_connections(
                circuit_model, adapter)

        LOGGER.info(
            """
            Report for afferent connectivity analysis posted at
            \t {}
            """.format(
                reporter.post(
                    report,
                    output_subfolder=kind_post_mtypes)))

    LOGGER.info("DONE")
