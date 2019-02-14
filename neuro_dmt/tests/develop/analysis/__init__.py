"""Test develop (generic) neuro_dmt Analysis."""

import os
import numpy as np
import pandas as pd
from bluepy.v2.enums\
    import Cell
from dmt.vtk.measurement\
     import StatisticalMeasurement
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.utils.logging\
    import Logger
from dmt.vtk.utils.collections\
    import Record\
    ,      take
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.measurement.parameter\
    import AtlasRegion\
    ,      CorticalLayer\
    ,      CorticalLayer6abSplit
from neuro_dmt.library.bluebrain.circuit.models.sscx\
   import get_sscx_fake_atlas_circuit_model\
   ,      get_sscx_atlas_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest
from neuro_dmt.models.bluebrain.circuit.adapter\
     import BlueBrainModelAdapter
from neuro_dmt.analysis.circuit.composition.by_layer\
    import CellDensityAnalysis\
    ,      CellRatioAnalysis\
    ,      InhibitorySynapseDensityAnalysis\
    ,      SynapseDensityAnalysis
 

logger=\
    Logger(
        "Test develop neuro_dmt Analysis",
        level=Logger.level.DEBUG)
bbadapter=\
    BlueBrainModelAdapter(
        brain_region=brain_regions.sscx,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=20)
sscx_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64", "circuits",
        "O1.v6a/20171212",
        "CircuitConfig")
sscx_circuit_model=\
    get_sscx_atlas_circuit_model(
        sscx_circuit_config,
        animal="rat",
        atlas_path=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64", "entities",
            "dev", "atlas",
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018"))
sscx_circuit_model.geometry.circuit_specialization.representative_region=\
    "mc2_Column"
sscx_circuit=\
    sscx_circuit_model.bluepy_circuit

sscx_atlas_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64", "circuits",
        "S1.v6a/20171206",
        "CircuitConfig")
sscx_atlas_circuit_model=\
    get_sscx_atlas_circuit_model(
        sscx_atlas_circuit_config,
        animal="rat",
        atlas_path=os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64", "circuits",
        "S1.v6a/20171206",
            ".atlas", "C63CB79F-392A-4873-9949-0D347682253A"))
sscx_atlas_circuit=\
    sscx_atlas_circuit_model.bluepy_circuit


iso_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj68/circuits",
        "Isocortex/20190212/",
        "CircuitConfig")
iso_circuit_model=\
    get_iso_cortex_circuit_model(
        iso_circuit_config,
        "mouse")
iso_circuit=\
     iso_circuit_model.bluepy_circuit


class TestCompositionAnalysis:
    """Test behavior of Composition Analysis subclasses"""

    AnalysisType=dict(
        cell_density=CellDensityAnalysis,
        cell_ratio=CellRatioAnalysis,
        inhibitory_synapse_density=InhibitorySynapseDensityAnalysis,
        syn_density=SynapseDensityAnalysis)
    
    def __init__(self,
            circuit_model=iso_circuit_model,
            sample_size=100,
            sampled_box_shape=25. * np.ones(3),
            regions=["SSp-ll"],
            *args, **kwargs):
        """"..."""
        self._circuit_model=\
            circuit_model
        self._adapter=\
            BlueBrainModelAdapter(
                brain_region=self._circuit_model.brain_region,
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                spatial_random_variate=RandomRegionOfInterest,
                model_label="in-silico")
        self._circuit_regions=\
            AtlasRegion(
                values=regions)
        self._measurements=\
            {} # map phenomenon (label) to its Measurement
        self._reports=\
            {}

    @classmethod
    def get_analysis_type(cls,
            phenomenon):
        return cls.AnalysisType[phenomenon]

    def get_instance(self,
            phenomenon,
            circuit_regions=None,
            *args, **kwargs):
        """..."""
        circuit_regions=\
            circuit_regions if circuit_regions\
            else self._circuit_regions
        AnalysisType=\
            self.get_analysis_type(
                phenomenon)
        return\
            AnalysisType(
                adapter=self._adapter,
                animal=self._circuit_model.animal,
                measurement_parameters=[
                    circuit_regions,
                    CorticalLayer()],
                spatial_parameters=[
                    circuit_regions,
                    CorticalLayer()],
                plotting_parameter=CorticalLayer(),
                *args, **kwargs)
            
    def _already_measured(self,
            phenomenon,
            region):
        """..."""
        if not self._measurements:
            return False
        phenomenon_label=\
            getattr(
                phenomenon, "label",
                phenomenon)
        measurement=\
            self._measurements.get(
                phenomenon,
                None)
        if measurement is None:
            return False
        index=\
            measurement.data.index
        return\
            region in index.levels[index.names.index(Cell.REGION)]

    def _append_measurment(self,
            measurement):
        """..."""
        phenomenon=\
            measurement.phenomenon.label
        if phenomenon not in self._measurements:
            self._measurements[phenomenon]=\
                measurement
        else:
            self._measurements[phenomenon].data=\
                pd.concat([
                    self._measurements[phenomenon].data,
                    measurement.data])

    def _save_report(self,
            analysis,
            region,
            report):
        """..."""
        report_path=\
            analysis.save_report(
                report,
                output_dir="region-{}".format(region))
        phenomenon_label=\
            analysis.phenomenon.label
        if phenomenon_label not in self._reports:
            self._reports[phenomenon_label]= {}
        if region not in self._reports[phenomenon_label]:
            self._reports[phenomenon_label][region]= []
        self._reports[phenomenon_label][region]\
            .append(report_path)
        return self._reports


    def get_report(self,
            phenomenon,
            region="SSp-ll",
            save=True,
            *args, **kwargs):
        """Analysis of only one region may be reported"""
        logger.debug(
            logger.get_source_info(),
            "get report for phenomenon {}, region {}"\
            .format(phenomenon, region))
        analysis=\
            self.get_instance(
                phenomenon,
                circuit_regions=AtlasRegion(
                    values=[region]))
        if not self._already_measured(phenomenon, region):
            logger.debug(
                logger.get_source_info(),
                """not already measured""")
            measurement=\
                analysis.get_measurement(
                    self._circuit_model,
                    *args, **kwargs)
            self._append_measurment(
                measurement)
            logger.debug(
                logger.get_source_info(),
                """appended measurement""",
                "{}".format(measurement))
        else:
            logger.debug(
                logger.get_source_info(),
                """Already measured""")
        logger.debug(
            logger.get_source_info(),
            """measurement after getting one for {}""".format(phenomenon))
        for p, m in self._measurements.items():
            logger.debug(
                "{}: {}".format(p, m))
        report=\
            analysis.get_report(
                self._measurements[phenomenon],
                region=region,
                *args, **kwargs)
        if save:
            self._save_report(
                analysis,
                region,
                report)
        return report


