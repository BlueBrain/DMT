import os
import time
from neuro_dmt.tests.develop.analysis.validations import TestCompositionValidation
from neuro_dmt.tests.develop.analysis import\
    iso_circuit_model, sscx_circuit_model


iso_regions = ['SSp-ll', 'GU', 'SSp-ul', 'VISp', 'MOp', 'MOs']

def validate_circuit(circuit_model, regions, with_atlas_data=True):
    tester = TestCompositionValidation(circuit_model=circuit_model,
                                       regions=regions, sample_size=100)

    # tester._adapter.sample_size = 100
    for R in regions:
        for phenomenon in ("cell_density", "cell_ratio"):
            report = tester.get_report(phenomenon, region=R,
                                       with_atlas_data=with_atlas_data)
            report.save(output_dir_path=os.path.join(
                os.path.dirname(circuit_model.circuit_config),
                "validations", phenomenon, R),
                        report_file_name=str(time.clock()) + ".html")
    return tester

t = validate_circuit(sscx_circuit_model, ["mc2_Column"], with_atlas_data=False)
