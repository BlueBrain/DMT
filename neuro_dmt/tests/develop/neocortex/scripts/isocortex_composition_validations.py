""""Run composition validations for all the isocortex regions"""
import os, sys, getopt
from contextlib\
    import redirect_stdout\
    ,      redirect_stderr
from dmt.vtk.utils\
    import datasets
from dmt.vtk.utils.logging\
    import Logger
from dmt.vtk.utils.utils\
    import timestamp
from neuro_dmt.tests.develop.neocortex\
    import *

logger=\
    Logger(
        "isocortex composition validations run",
        level=Logger.level.INFO)
composition_phenomenons=(
    "cell_density", "cell_ratio")
hemispheres=\
    ("left", "right")

def get_validator(
        region,
        hemisphere,
        circuits_dir,
        output_dir_path,
        direction="eff"):
    """..."""
    circuit_config_path=\
        os.path.join(
            circuits_dir,
            "{}@{}".format(region, hemisphere),
            "CircuitConfig-{}".format(direction))
    circuit_model=\
        get_iso_cortex_circuit_model(
            circuit_config_path,
            animal="mouse",
            region_label="region",
            hemisphere=hemisphere,
            representative_region=region)
    return\
        NeocortexAnalysisSuite(
            circuit_model,
            region_values=[region],
            output_dir_path=output_dir_path)


if __name__ == "__main__":
    try:
        opts, args=\
            getopt.getopt(
                sys.argv[1:], "hs:r:",
                ["help",
                 "regions=",
                 "sample-size="])
    except getopt.GetoptError as err:
        logger.alert(
            "Error while reading options",
            sys.exit(2))
        pass
    
    sample_size = 100
    for o, a in opts:
        if o in ("-r", "--regions"):
            regions=\
                datasets.load_yaml(
                    os.getcwd(),
                    a).iso_regions
        if o in ("-s", "--sample-size"):
            sample_size = a

    if len(args) == 0:
        raise ValueError(
            "No circuit provided to analyze!")
    circuits_dir=\
        args[0]
    if len(args) == 1:
        raise ValueError(
            "No place to output results in!")
    output_path=\
        args[1]

    
    for region in regions:
        for hemisphere in hemispheres:
            neocortical_analysis_suite=\
                get_validator(
                    region,
                    hemisphere,
                    circuits_dir=circuits_dir,
                    output_dir_path=output_path)
            timestamp=\
                timestamp()
            log_file_dir=\
                os.path.join(
                    output_path,
                    "runs",
                    region,
                    hemisphere,
                    timestamp.day,
                    timestamp.time)
            try:
                os.makedirs(
                    log_file_dir)
            except FileExistsError:
                pass
            for phenomenon in composition_phenomenons:
                log_file_path=\
                    os.path.join(
                        log_file_dir,
                        "{}.log".format(phenomenon))
                err_file_path=\
                    os.path.join(
                        log_file_dir,
                        "{}.err".format(phenomenon))
                logger.info(
                    "logs will go to {}".format(log_file_path),
                    "errs will go to {}".format(err_file_path))
                with open(log_file_path, 'w') as log_file:
                    with open(err_file_path, 'w') as err_file:
                        with redirect_stdout(log_file):
                            with redirect_stderr(err_file):
                                logger.info(
                                    logger.get_source_info(),
                                    "region: {}".format(region),
                                    "hemisphere: {}".format(region),
                                    "phenomenon: {}".format(region))
                                neocortical_analysis_suite\
                                    .get_report(
                                        phenomenon,
                                        region,
                                        analysis_type="validation",
                                        sample_size=sample_size)
                        
