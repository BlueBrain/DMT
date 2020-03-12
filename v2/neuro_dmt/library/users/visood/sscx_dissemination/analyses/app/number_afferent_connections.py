"""
Analyze number of afferent connections.
"""

from dmt.tk.journal import Logger
from neuro_dmt.library.users.visood.sscx_dissemination.analyses import *

LOGGER = Logger(client=__file__, level=Logger.Level.INFO)


class number_connections_afferent:
    """..."""
    phenomenon =\
        Phenomenon(
            "Number Afferent Connections",
            description="Number of afferent connections",
            group="Connectome")

    def __init__(self, target_cell_group):
        self.pathway_measurement =\
            PathwayMeasurement(
                direction="AFF",
                value=lambda connections: 1,
                variable=self.phenomenon.label,
                specifiers_cell_type=["mtype"],
                sampling_methodology=terminology.sampling_methodology.exhaustive,
                processing_methodology=terminology.processing_methodology.batch,
                batch_size=1000,
                return_primary_info=True,
                target=self.get_target(target_cell_group))

    @staticmethod
    def get_target(query):
        return\
            lambda adapter, circuit_model: adapter.get_cells(
                circuit_model, **query)

    def __call__(self,
            circuit_model, adapter,
            sampling_methodology=None,
            **parameter_set):
        """..."""
        return\
            self.pathway_measurement.collect(
                adapter, circuit_model,
                **parameter_set)
                

def get_mtypes(adapter, circuit_model):
    return pd.DataFrame(
        adapter.get_mtypes(circuit_model),
        columns=pd.MultiIndex.from_tuples([
            ("post_synaptic_cell_group", "mtype")]))

def get_analysis_report(circuit_model, adapter, target_cells):
    """
    Analyze

    Arguments
    -----------
    target_cells :: Mapping describing the subset of cells between which
    ~               the connections will be analyzed.
    """
    analysis =\
        BrainCircuitAnalysis(
            phenomenon=number_connections_afferent.phenomenon,
            introduction="""
            Number of afferent connections of a cell.
            """,
            methods="""
            Number of afferent connections were counted by mtype.
            """,
            AdapterInterface=ConnectomeAnalysesSuite.AdapterInterface,
            measurement_parameters=Parameters(get_mtypes),
            sample_measurement=number_connections_afferent(target_cells),
            measurement_collection=measurement.collection.series_type,
            processing_methodology=terminology.processing_methodology.serial,
            sampling_methodology=terminology.sampling_methodology.random,
            plotter=MultiPlot(
                mvar=("post_synaptic_cell", "mtype"),
                plotter=Bars(
                    xvar=("pre_synaptic_cell", "mtype"),
                    xlabel="pre-synaptic-cell-mtype",
                    yvar=number_connections_afferent.phenomenon.label,
                    ylabel=number_connections_afferent.phenomenon.name)))

    return analysis(circuit_model, adapter)


def parse_target(target_string):
    return{
        key: value for key, value in (
            pair.split('=') for pair in target_string.split(';'))}

def run(*args):
    """
    Run me
    """
    spec = AnalysisSpec()
    circuits = SSCxDisseminationCircuits()
    index_argv = 1
    try:
        name_circuit = args[index_argv]
        index_argv += 1
    except IndexError:
        raise Exception(
            """
            Missing argument for name of the circuit to analyze.
            Following circuits are available:
            {}
            """.format(
                '\n'.join(
                    "\t{}: {}".format(
                        key, value for key, value in circuits.variations))))
    LOGGER.info("Analyze circuit: {}".format(name_circuit))

    circuit_model = circuits.get(name_circuit)
    adapter = BlueBrainCircuitAdapter()

    try:
        target_string = args[index_argv]
        index_argv += 1
    except IndexError:
        target_string = "region=S1FL"

    target = parse_target(target_string)



if __name__ == "__main__":
    spec = AnalysisSpec()
    circuits = SSCxDisseminationCircuits()
    index_argv = 1
    try:
        name_circuit = sys.argv[index_argv]
        index_argv += 1
    except IndexError:
        raise Exception(
            """
            Missing name of the circuit.
            Following circuits are available:
            {}
            """.format(circuits.variations))
    sys.stdout.write("Analyze Circuit {}\n".format(name_circuit))

    circuit_model = circuits.get(name_circuit)

    adapter = BlueBrainCircuitAdapter()

    try:
        input_target = sys.argv[index_argv]
        index_argv += 1
    except IndexError:
        input_target = "region=S1FL"

    target = {key: value for key, value in (
         pair.split('=') for pair in input_target.split(';'))}

    try:
        path_output_folder = sys.argv[index_argv]
        index_argv += 1
    except IndexError:
        try:
            variant = getattr(circuits.variations, name_circuit)
        except AttributeError:
            variant = name_circuit
        path_output_folder = os.path.join(circuits.home, "analyses", variant)

    if not os.path.exists(path_output_folder):
        os.makedirs(path_output_folder)

    sys.stdout.write("Save reports in {}\n".format(path_output_folder))

    reporter = CheetahReporter(path_output_folder=path_output_folder)


    sys.stdout.write("Target cells: {}\n".format(target))
    reporter.post(get_analysis_report(circuit_model, adapter, target))
        

