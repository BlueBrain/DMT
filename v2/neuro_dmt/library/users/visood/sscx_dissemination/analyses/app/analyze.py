"""
Analyze a circuit
"""


from dmt.tk.journal import Logger
from neuro_dmt.library.users.visood.sscx_dissemination.analyses import *

LOGGER = Logger(client=__file__, level=Logger.Level.INFO)

def parse_target(target_string):
    return{
        key: value for key, value in (
            pair.split('=') for pair in target_string.split(';'))}

def run(args):
    """
    Run me
    """
    spec = AnalysisSpec()
    circuits = SSCxDisseminationCircuits()
    index_argv = 0

    
    LOGGER.status("Run: {}".format(args))

    try:
        name_analysis = args[index_argv]
        index_argv +=1
    except IndexError:
        raise Exception(
        """
        Missing argument for name of the analysis.
        """)
    try:
        analysis_composition = getattr(composition, name_analysis)
    except:
        analysis_composition = NA
    try:
        analysis_connectome = getattr(connectome, name_analysis)
    except:
        analysis_connectome = NA

    if analysis_composition is NA and analysis_connectome is NA:
        raise ValueError(
            """
            Analysis {} is not available.
            """.format(name_analysis))

    if analysis_composition and analysis_connectome:
        raise ValueError(
            """
            Analysis {} is available for both circuit composition,
            and circuit connectome.
            Provide one of 
            \t --group=Composition
            \t --group=Connectome
            """)

    if analysis_composition:
        LOGGER.status("Analyze circuit composition {}".format(name_analysis))
        analysis = analysis_composition
    else:
        LOGGER.status("Analyze circuit connectome {}".format(name_analysis))
        analysis = analysis_connectome

    try:
        name_circuit = args[index_argv]
        index_argv += 1
    except IndexError:
        raise Exception(
            """
            Missing argument for name of the circuit to analyze.
            Following circuits are available:
            \t{}
            """.format(
                '\n\t\t'.join(
                    "{}: {}".format(key, value)
                    for key, value in circuits.variations.field_dict.items())))
    LOGGER.status("Analyze circuit: {}".format(name_circuit))

    circuit_model = circuits.get(name_circuit)
    adapter = BlueBrainCircuitAdapter()

    try:
        target_string = args[index_argv]
        index_argv += 1
    except IndexError:
        target_string = "region=S1FL"

    target = parse_target(target_string)
    LOGGER.status("Target cells: {}\n".format(target))

    try:
        path_output_folder = args[index_argv]
        index_argv += 1
    except IndexError:
        try:
            variant = getattr(circuits.variations, name_circuit)
        except AttributeError:
            variant = name_circuit
        path_output_folder = os.path.join(circuits.home, "analyses", variant)

    if not os.path.exists(path_output_folder):
        os.makedirs(path_output_folder)

    LOGGER.status("Save reports in {}.".format(path_output_folder))

    reporter = CheetahReporter(path_output_folder=path_output_folder)

    reporter.post(analysis(circuit_model, adapter, target))


if __name__ == "__main__":
    LOGGER.status(format(sys.argv))
    run(sys.argv[1:])
