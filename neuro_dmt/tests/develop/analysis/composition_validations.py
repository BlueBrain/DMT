import os
import time
from neuro_dmt.tests.develop.analysis.validations import\
    TestCompositionValidation

from neuro_dmt.tests.develop.analysis import\
    iso_circuit_model, sscx_circuit_model


iso_regions = ['PERI',
               'VISpm',
               'AUDp',
               'VISli',
               'ACAd',
               'AUDv',
               'VISam',
               'VISpl',
               'VISrl',
               'VISpor',
               'AIv',
               'PL',
               'AUDpo',
               'ILA',
               'VISC',
               'SSp-bfd',
               'VISp',
               'SSp-n',
               'SSp-ll',
               'ORBvl',
               'RSPd',
               'ECT',
               'TEa',
               'SSs',
               'VISal',
               'SSp-ul',
               'VISa',
               'GU',
               'AId',
               'ORBl',
               'FRP',
               'MOp',
               'VISl',
               'ACAv',
               'AIp',
               'ORBm',
               'SSp-un',
               'MOs',
               'SSp-tr',
               'RSPv',
               'SSp-m']
# ['FRP',
              #           'MOp',
              #           'MOs',
              #           'SSp-n',
              #           # 'VISrll',
              #           'SSp-ll',
              #           'SSp-m',
              #           'SSp-ul',
              #           'SSp-tr',
              #           'SSp-un',
              #           'SSs',
              #           'GU',
              #           'VISC',
              #           # 'VISlla',
              #           'AUDp',
              #           'AUDpo',
              #           'AUDv',
              #           'VISal',
              #           'VISam',
              #           'VISl',
              #           'VISp',
              #           'VISpl',
              #           'VISpm',
              #           'VISli',
              #           'VISpor',
              #           'ACAd',
              #           'ACAv',
              #           'PL',
              #           'ILA',
              #           'ORBl',
              #           'ORBm',
              #           'ORBv',
              #           'ORBvl',
              #           'AId',
              #           'AIp',
              #           'AIv',
              #           # 'VISmma',
              #           'VISmmp',
              #           'VISm',
              #           'RSPd',
              #           'RSPv',
              #           'VISa',
              #           # 'VISrl',
              #           'TEa',
              #           'PERI',
              #           'ECT']

def validate_circuit(circuit_model, regions, with_atlas_data=True):
    tester = TestCompositionValidation(circuit_model=circuit_model,
                                       regions=regions, sample_size=25)

    # tester._adapter.sample_size = 100
    for R in regions:
        for phenomenon in ("cell_density", "cell_ratio"):
            report = tester.get_report(phenomenon, region=R,
                                       with_atlas_data=with_atlas_data)
            print("CIRCUITCONFIG", circuit_model.circuit_config)
            report.save(output_dir_path=os.path.join(
                os.path.dirname(circuit_model.circuit_config),
                "validations", phenomenon, R),
                        report_file_name=str(time.clock()) + ".html")
    return tester

# t = validate_circuit(iso_circuit_model, iso_regions, with_atlas_data=True)
t2 = validate_circuit(sscx_circuit_model, ["mc2_Column"], with_atlas_data=False)
