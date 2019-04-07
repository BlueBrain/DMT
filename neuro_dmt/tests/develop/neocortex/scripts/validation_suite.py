"""
Run validations and analysis.

Options:

-h, --help --> display this usage
-a, --available --> Analyses and  validations that are available
"""

import sys, os, getopt
from contextlib\
    import redirect_stdout\
    ,      redirect_stderr
from dmt.vtk.utils.collections\
    import POD
from dmt.vtk.utils.logging\
    import Logger
from dmt.vtk.utils\
    import datasets\
    ,      utils
from neuro_dmt.tests.develop.neocortex\
    import *
from neuro_dmt.measurement.parameter.spatial\
    import SomaDistance

logger=\
    Logger(
        "Validation Suit",
        level=Logger.level.INFO)

def usage():
    logger.info(
        __doc__)

class Info:
    phenomena_available=\
        NeocortexAnalysisSuite\
        .phenomenon\
        .keys()


def help():
    logger.dialog(
        "Available validations and analyses: ",
        "\n".join(
            "{})\t{}.".format(i + 1, phenomenon)
            for i, phenomenon in enumerate(
                    Info.phenomena_available)))
                    

if __name__=="__main__":
    try:
        opts, args=\
            getopt.getopt(
                sys.argv[1:], "hap:r:",
                ["help",
                 "phenomenon=",
                 "region=",
                 "analyze",
                 "validate",
                 "sample-size=",
                 "cache-size=",
                 "pathways=",
                 "mtypes=",
                 "by-distance",
                 "number-bins=",
                 "view="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        logger.error(
            sys.exit(2))

    logger.info(
        "opts {}".format(opts))
    logger.info(
        "args {}".format(args))

    region=\
        None
    phenomenon=\
        None
    analysis_type=\
        "validation"
    sample_size=\
        100
    cache_size=\
        100
    pathways=\
        set()
    mtypes=\
        []
    by_distance=\
        False
    number_bins=\
        75
    plot_view=\
        "Both"
    for o, a in opts:
        if o in ("-h", "--help"):
            help()
            sys.exit(0)
        if o in ("-a", "--available"):
            sys.stdout.write(
                "Available: ")
            for i, phenomenon in enumerate(
                    Info.phenomena_available):
                sys.stdout.write(
                    "\n{})\t{}.".format(i+1, phenomenon))
            sys.stdout.write("\n")
            sys.exit(0)
        if o in ("-p", "--phenomenon"):
            phenomenon = a
            logger.info(
                "Run {} analyses / validation".format(
                    phenomenon))
        if o in ("-r", "--region"):
            region = a
        if o == "--analyze":
            analysis_type = "analysis"
        if o == "--sample-size":
            sample_size = int(a)
        if o == "--cache-size":
            cache_size = int(a)
        if o == "--pathways":
            pathways_data=\
                datasets.load_yaml(
                    os.getcwd(),
                    a).pathways
            pathways={
                (pre_mtype, post_mtype)
                for pre_mtype, post_mtypes in pathways_data.items()
                for post_mtype in post_mtypes}
        if o == "--mtypes":
            mtypes=\
                datasets.load_yaml(
                    os.getcwd(),
                    a).mtypes
        if o == "--by-distance":
            by_distance = True
        if o == "--number-bins":
            number_bins = int(a)
        if o == "--view":
            plot_view = a

    if len(args) == 0:
        raise ValueError(
            "No circuit provided to analyze!")
    circuit_config_path=\
        args[0]
    if len(args) == 1:
        raise ValueError(
            "No place to output results in!")
    output_path=\
        args[1]
    is_isocortex_circuit=\
        "Isocortex" in circuit_config_path
    region=\
        region if region else(
            "SSp-ll@left"\
            if is_isocortex_circuit else\
            "mc2_Column")
    if not phenomenon:
        logger.error(
            logger.get_source_info(),
            "Provide a phenomenon to analyze.",
            "Choose one from: ",
            "\n".join(
                "{})\t{}.".format(i + 1, phenomenon)
                for i, phenomenon in enumerate(
                        Info.phenomena_available)))
        raise ValueError(
            "No phenomenon provided")

    if is_isocortex_circuit:
        hemisphere=\
            region.split("@")[1]
        circuit_model=\
            get_iso_cortex_circuit_model(
                circuit_config_path,
                animal="mouse",
                region_label="region",
                hemisphere=hemisphere,
                representative_subregion=region)
    else:
        circuit_model=\
            get_sscx_atlas_circuit_model(
                circuit_config_path,
                animal="mouse",
                region_label="region",
                representative_region="mc2_Column")

    neocortical_analysis_suite=\
        NeocortexAnalysisSuite(
            circuit_model,
            region_values=[region],
            mtypes=mtypes,
            output_dir_path=output_path)
    soma_distances=\
        None if not by_distance\
        else SomaDistance(0., 1500., number_bins)
    neocortical_analysis_suite\
        .get_report(
            phenomenon,
            region,
            analysis_type=analysis_type,
            sample_size=sample_size,
            cache_size=cache_size,
            by_distance=by_distance,
            soma_distances=soma_distances,
            pathways=set(pathways),
            plot_view=plot_view)
