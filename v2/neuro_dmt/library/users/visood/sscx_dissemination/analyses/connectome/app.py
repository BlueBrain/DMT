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
from neuro_dmt.library.users.visood.sscx_dissemination.analyses.connectome\
    import ConnectomeAnalysesSuite


LOGGER = Logger(client=__file__, level="INFO")

def _load_mtypes(path_source_file):
    try:
        with open(path_source_file, 'r') as source_file:
            try:
                return yaml.load(source_file, Loader=yaml.FullLoader)
            except AttributeError:
                return yaml.load(source_file)
    except FileNotFoundError:
        return []
    return []

if __name__ == "__main__":
    index_argv = 1
    path_circuit_data =\
        sys.argv[index_argv]
    index_argv += 1

    path_source_pre_mtypes = sys.argv[index_argv]
    index_argv += 1
    path_source_post_mtypes = sys.argv[index_argv]
    index_argv += 1

    try:
        sample_size = int(sys.argv[index_argv])
        index_argv += 1
    except IndexError:
        sample_size = 20

    pre_mtypes =\
        _load_mtypes(path_source_pre_mtypes)
    post_mtypes =\
        _load_mtypes(path_source_post_mtypes)

    LOGGER.info(
        """
        Load the circuit at {}
        """.format(
            path_circuit_data))
    circuit_model =\
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
    adapter =\
        BlueBrainCircuitAdapter()

    LOGGER.info(
        """
        Compute afferent connectivity for post-synaptic cell mtypes:
        \t {}.
        """.format(post_mtypes))
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
            reporter.post(report)))
