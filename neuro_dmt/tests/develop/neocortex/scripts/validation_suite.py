"""
Run validations and analysis.

Options:

-h, --help --> display this usage
-a, --available --> Analyses and  validations that are available
"""

import sys, os, getopt
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.tests.develop.neocortex\
    import *

logger=\
    Logger(
        "Validation Suit",
        level=Logger.level.DEBUG)

def usage():
    logger.info(
        __doc__)


phenomena_available=\
    NeocortexAnalysisSuite.phenomenon.keys()

def help():
    logger.info(
        "Available validations and analyses: ",
        "\n".join(
            "{})\t{}.".format(i + 1, phenomenon)
            for i, phenomenon in enumerate(phenomena_available)))
                    

if __name__=="__main__":
    try:
        opts, args=\
            getopt.getopt(
                sys.argv[1:], "hap:r:o:",
                ["help",
                 "phenomenon=",
                 "region=",
                 "analyze",
                 "validate",
                 "output_path=",
                 "sample_size=",
                 "cache_size="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        logger.error(
            sys.exit(2))

    logger.info(
        "opts {}".format(opts))
    logger.info(
        "args {}".format(args))

    if len(args) == 0:
        raise ValueError(
            "No circuit provided to analyze.")
    circuit_config_path=\
        args[0]
    is_isocortex_circuit=\
        "Isocortex" in circuit_config_path
    region=\
        "SSp-ll@left"\
        if is_isocortex_circuit else\
           "mc2_Column"
    phenomenon=\
        None
    analysis_type=\
        "validation"
    output_path=\
        os.getcwd()
    sample_size=\
        100
    cache_size=\
        100
    for o, a in opts:
        if o in ("-h", "--help"):
            help()
            sys.exit(0)
        if o in ("-a", "--available"):
            sys.stdout.write(
                "Available: ")
            for i, phenomenon in enumerate(phenomena_available):
                sys.stdout.write(
                    "\n{})\t{}.".format(i+1, phenomenon))
            sys.stdout.write("\n")
            sys.exit(0)
        if o in ("-p", "--phenomenon"):
            phenomenon=\
                a
            logger.info(
                "Run {} analyses / validation".format(
                    phenomenon))
        if o in ("-r", "--region"):
            region=\
                a
        if o in ("-o", "--output_path"):
            output_path=\
                a
        if o == "--analyze":
            analysis_type=\
                "analysis"

        if o == "--sample_size":
            sample_size=\
                a
        if o == "--cache_size":
            cache_size=\
                a

    if not phenomenon:
        logger.error(
            logger.get_source_info(),
            "Provide a phenomenon to analyze.",
            "Choose one from: ",
            "\n".join(
                "{})\t{}.".format(i + 1, phenomenon)
                for i, phenomenon in enumerate(phenomena_available)))
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
            region_values=[region])
    neocortical_analysis_suite\
        .get_report(
            phenomenon,
            region,
            sample_size=sample_size,
            cache_size=cache_size,
            output_dir_path=output_path)




