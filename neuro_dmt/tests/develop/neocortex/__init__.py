"""Validations for the neocortex (isocortex) circuit to be released
in 2019 March."""

from abc import ABC, abstractmethod
import os
import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell
from dmt.vtk.utils.logging\
    import Logger
from dmt.vtk.phenomenon\
    import Phenomenon
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest
from neuro_dmt.measurement.parameter\
    import AtlasRegion\
    ,      CorticalLayer
from neuro_dmt.models.bluebrain.circuit.parameters\
     import Mtype
from neuro_dmt.models.bluebrain.circuit.adapter\
     import BlueBrainModelAdapter
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSSCxCompositionData
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSSCxCompositionData
from neuro_dmt.data.bluebrain.circuit.atlas.atlas_cell_density\
    import AtlasBasedCellDensityData\
    ,      AtlasBasedEIRatioData
from neuro_dmt.analysis.comparison.validation.circuit.composition.by_layer\
    import CellDensityAnalysis\
    ,      CellDensityValidation\
    ,      CellRatioAnalysis\
    ,      CellRatioValidation\
    ,      SynapseDensityAnalysis\
    ,      SynapseDensityValidation\
    ,      InhibitorySynapseDensityAnalysis\
    ,      InhibitorySynapseDensityValidation
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.connectome\
    import RatSSCxConnectomeData
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.connectome\
    import MouseSSCxConnectomeData
from neuro_dmt.analysis.comparison.validation.circuit.connectome.by_mtype\
    import PairSynapseCountAnalysis\
    ,      PairSynapseCountValidation\
    ,      PairConnectionAnalysis\
    ,      PairConnectionValidation\
    ,      PathwayConnectionProbabilityAnalysis\
    ,      PathwayConnectionProbabilityValidation\
    ,      CellBoutonDensityAnalysis\
    ,      CellBoutonDensityValidation
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import EfferentConnectionCountAnalysis\
    ,      AfferentConnectionCountAnalysis
from neuro_dmt.tests.develop.circuits\
    import *

logger=\
    Logger(
        "NeocortexAnalysisSuite",
        level=Logger.level.DEBUG)

class NeocortexAnalysisSuite(
        ABC):
    """Test neocortex."""

    phenomenon = {
        "cell_density"\
        : Phenomenon(
            "Cell Density",
            "Number of cells in a unit volume",
            group="composition"),
        "cell_ratio"\
        : Phenomenon(
            "Cell Ratio",
            "Fraction of inhibitory cells in the circuit.",
            group="composition"),
        "synapse_density"\
        : Phenomenon(
            "excitatory_synapse_density",
            "Number of excitatory synapses in a unit volume",
            group="composition"),
        "inhibitory_synapse_density"\
        : Phenomenon(
            "inhibitory_synapse_density",
            "Number of inhibitory synapses in a unit volume",
            group="composition"),
        "pair_synapse_count"\
        : Phenomenon(
            "Pair Synapse Count",
            "Number of synapses connecting mtype-->mtype \
            pathway cell pairs",
            group="connectome"),
        "pair_connection"\
        : Phenomenon(
            "Pair Connection",
            "Existence of a connection between a pair of cells.",
            group="connectome"),
        "pathway_connection_probability"\
        : Phenomenon(
            "Pathway Connection Probability",
            "Probability that a mtype-->mtype pathway cell pair \
            is connected",
            group="connectome"),
        "efferent_connection_count"\
        : Phenomenon(
                "Pathway Efferent Connection Count",
                """Number of efferent connections in an mtype --> mtype,
                by distance.""",
                group="connectome"),
        "afferent_connection_count"\
        : Phenomenon(
                "Pathway Efferent Connection Count",
                """Number of efferent connections in an mtype --> mtype,
                by distance.""",
                group="connectome"),
        "bouton_density"\
        : Phenomenon(
            "Bouton Density",
            "Number of boutons per unit length of a cell's axon arbor",
            group="connectome")}
    Analysis={
        "cell_density"\
        : CellDensityAnalysis,
        "cell_ratio"\
        : CellRatioAnalysis,
        "synapse_density"\
        : SynapseDensityAnalysis,
        "inhibitory_synapse_density"\
        : InhibitorySynapseDensityAnalysis,
        "pair_synapse_count"\
        : PairSynapseCountAnalysis,
        "pair_connection"\
        : PairConnectionAnalysis,
        "pathway_connection_probability"\
        : PathwayConnectionProbabilityAnalysis,
        "efferent_connection_count"\
        : EfferentConnectionCountAnalysis,
        "afferent_connection_count"\
        : AfferentConnectionCountAnalysis,
        "bouton_density"\
        : CellBoutonDensityAnalysis}
    Validation={
        "cell_density"\
        : CellDensityValidation,
        "cell_ratio"\
        : CellRatioValidation,
        "synapse_density"\
        : SynapseDensityValidation,
        "inhibitory_synapse_density"\
        : InhibitorySynapseDensityValidation,
        "pair_synapse_count"\
        : PairSynapseCountValidation,
        "pair_connection"\
        : PairConnectionValidation,
        "pathway_connection_probability"\
        : PathwayConnectionProbabilityValidation,
        "bouton_density"\
        : CellBoutonDensityValidation}
    reference_data={
        "cell_density"\
        : MouseSSCxCompositionData.get_available_data(
            "cell_density"),
        "cell_ratio"\
        : MouseSSCxCompositionData.get_available_data(
            "cell_ratio"),
        "synapse_density"\
        : MouseSSCxCompositionData.get_available_data(
            "synapse_density"),
        "inhibitory_synapse_density"\
        : MouseSSCxCompositionData.get_available_data(
            "inhibitory_synapse_density"),
        "pair_synapse_count"\
        : RatSSCxConnectomeData.get_available_data(
            "pair_synapse_count"),
        "pair_connection"\
        : RatSSCxConnectomeData.get_available_data(
            "pathway_connection_probability"),
        "pathway_connection_probability"\
        : RatSSCxConnectomeData.get_available_data(
            "pathway_connection_probability"),
        "bouton_density"\
        : RatSSCxConnectomeData.get_available_data(
            "bouton_density")}

    def __init__(self,
            circuit_model,
            sampled_box_shape=50. * np.ones(3),
            region_values=["SSp-ll@left"],
            mtype_values=[],
            sample_size=20,
            output_dir_path=os.getcwd(),
            *args, **kwargs):
        """Initialize Me"""
        self._circuit_model=\
            circuit_model
        self._mtype_values=\
            mtype_values if mtype_values\
            else sorted(
                    list(circuit_model.cells.mtypes))
        self._region_parameter=\
            AtlasRegion(values=region_values)
        self._layer_parameter=\
            CorticalLayer()
        self._mtype_parameter=\
            Mtype(
                circuit=circuit_model.bluepy_circuit,
                label="mtype",
                values=self._mtype_values)
        self._pre_mtype_parameter=\
            Mtype(
                circuit=circuit_model.bluepy_circuit,
                label="pre_mtype",
                values=self._mtype_values)
        self._post_mtype_parameter=\
            Mtype(
                circuit=circuit_model.bluepy_circuit,
                label="post_mtype",
                values=self._mtype_values)
        self._adapter=\
            BlueBrainModelAdapter(
                brain_region=self._circuit_model.brain_region,
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                spatial_random_variate=RandomRegionOfInterest,
                model_label="in-silico")
        self._circuit_region_parameter=\
            AtlasRegion(
                values=region_values)
        self._output_dir_path=\
            output_dir_path
        self._measurements=\
            {}
        self._reports=\
            {}
        self._measurement_parameters={
            "cell_density":[
                self._region_parameter,
                self._layer_parameter],
            "cell_ratio":[
                self._region_parameter,
                self._layer_parameter],
            "synapse_density":[
                self._region_parameter,
                self._layer_parameter],
            "inhibitory_synapse_density":[
                self._region_parameter,
                self._layer_parameter],
            "pair_synapse_count":[
                self._region_parameter,
                self._pre_mtype_parameter,
                self._post_mtype_parameter],
            "pair_connection":[
                self._region_parameter,
                self._pre_mtype_parameter,
                self._post_mtype_parameter],
            "pathway_connection_probability":[
                self._region_parameter,
                self._pre_mtype_parameter,
                self._post_mtype_parameter],
            "efferent_connection_count":[
                self._region_parameter,
                self._pre_mtype_parameter,
                self._post_mtype_parameter],
            "afferent_connection_count":[
                self._region_parameter,
                self._pre_mtype_parameter,
                self._post_mtype_parameter],
            "bouton_density":[
                self._region_parameter,
                self._mtype_parameter]}
        self._plotted_parameters={
            "cell_density":[
                self._layer_parameter.label],
            "cell_ratio":[
                self._layer_parameter.label],
            "synapse_density":[
                self._layer_parameter.label],
            "inhibitory_synapse_density":[
                self._layer_parameter.label],
            "pair_synapse_count":[
                self._pre_mtype_parameter.label,
                self._post_mtype_parameter.label],
            "pair_connection":[
                self._pre_mtype_parameter.label,
                self._post_mtype_parameter.label],
            "pathway_connection_probability":[
                self._pre_mtype_parameter.label,
                self._post_mtype_parameter.label],
            "efferent_connection_count":[
                self._pre_mtype_parameter.label,
                self._post_mtype_parameter.label],
            "afferent_connection_count":[
                self._pre_mtype_parameter.label,
                self._post_mtype_parameter.label],
            "bouton_density":[
                self._mtype_parameter.label]}

    @staticmethod
    def _get_mtypes(
            pathways,
            end=None):
        """..."""
        if end=="pre":
            return sorted(list({
                mtype for mtype, _ in pathways}))
        if end=="post":
            return sorted(list({
                mtype for _, mtype in pathways}))
        return sorted(list({
            mtype for pre_post_mtypes in pathways
            for mtype in pre_post_mtypes}))

    def _get_mtype_parameter(self,
            end=None,
            pathways=set(),
            **kwargs):
        """..."""
        logger.info(
            logger.get_source_info(),
            """get {}-mtype parameter""".format(end))
        assert not end or end in ("pre", "post")
        if pathways:
            return\
                Mtype(
                    label="{}_mtype".format(end) if end else "mtype",
                    values=self._get_mtypes(pathways, end))
        if end == "pre":
            return\
                self._pre_mtype_parameter
        if end == "post":
            return\
                self._post_mtype_parameter
        return\
            self._mtype_parameter

    def _get_measurement_parameters(self,
            phenomenon,
            pathways=set(),
            soma_distances=None,
            **kwargs):
        """..."""
        if phenomenon in (
                "pathway_connection_probability",
                "efferent_connection_count",
                "afferent_connection_count"):
            regions=\
                self._region_parameter
            pre_mtypes=\
                self._get_mtype_parameter(
                    end="pre",
                    pathways=pathways,
                    **kwargs)
            post_mtypes=\
                self._get_mtype_parameter(
                    end="post",
                    pathways=pathways,
                    **kwargs)
            return\
                [regions, pre_mtypes, post_mtypes, soma_distances]\
                if soma_distances else\
                   [regions, pre_mtypes, post_mtypes]
        return self._measurement_parameters[phenomenon]

    def _get_cell_group_parameters(self,
            phenomenon,
            mtypes=None,
            pathways=set(),
            **kwargs):
        """..."""
        if phenomenon in (
                "pathway_connection_probability",
                "efferent_connection_count",
                "afferent_connection_count"):
            if mtypes:
                return[
                    Mtype(
                        values=mtypes)]
            if pathways:
                mtypes=\
                    self._get_mtype_parameter("pre", pathways).values\
                    + self._get_mtype_parameter("post", pathways).values
                return[
                    Mtype(
                        values=mtypes)]
        return [self._mtype_parameter]
    
    def _get_plotted_parameters(self,
            phenomenon,
            **kwargs):
        """..."""
        if phenomenon in (
                "pathway_connection_probability",
                "efferent_connection_count",
                "afferent_connection_count"):
            return\
                ["pre_mtype", "post_mtype", "soma_distance"]\
                if "soma_distances" in kwargs or "soma_distance" in kwargs\
                   else ["pre_mtype", "post_mtype"]
        return\
                self._plotted_parameters[
                    phenomenon]
    def _get_pathway_parameters(self,
            phenomenon,
            **kwargs):
        """..."""
        if phenomenon in (
                "pathway_connection_probability",
                "efferent_connection_count",
                "afferent_connection_count"):
            return[
                self._get_mtype_parameter(
                    end="pre",
                    **kwargs),
                self._get_mtype_parameter(
                    end="post",
                    **kwargs)]
        return[
            self._pre_mtype_parameter,
            self._post_mtype_parameter]

    def _get_phenomenon_kwargs(self,
            phenomenon,
            pathways=set(),
            **kwargs):
        """..."""
        if phenomenon in (
                "pathway_connection_probability",
                "efferent_connection_count",
                "afferent_connection_count"):
            # kwargs["by_distance"]=\
            #     "soma_distances" in kwargs or "soma_distance" in kwargs
            kwargs["pathways_to_analyze"] = pathways
        return kwargs

    def _get_spatial_parameters(self,
            phenomenon,
            **kwargs):
        """..."""
        return[
            self._region_parameter, 
            self._layer_parameter]

    def _get_reference_data(self,
            phenomenon,
            circuit_model,
            region,
            reference_data=None):
        """..."""
        if reference_data:
            return reference_data
        reference_data=\
            self.reference_data[phenomenon]()
        if circuit_model.brain_region.label == "somatosensory_cortex":
            return reference_data
        if phenomenon in ("cell_density", "cell_ratio"):
            try:
                atlas_path=\
                    circuit_model\
                    .atlas_path
            except AttributeError:
                atlas_path=\
                    circuit_model\
                    .bluepy_circuit\
                    .atlas\
                    .dirpath
            region=\
                region.split("@")[0]
            atlas_data=\
                AtlasBasedCellDensityData(atlas_path, region)\
                if phenomenon == "cell_density" else\
                   AtlasBasedEIRatioData(atlas_path, region)
            reference_data.add_dataset(
                dataset=atlas_data,
                dataset_label="insilico-constraint")
        return reference_data

    def get_instance(self,
            phenomenon,
            analysis_type="validation", #or "analysis"
            circuit_regions=None,
            reference_data=None,
            *args, **kwargs):
        """..."""
        logger.debug(
            logger.get_source_info(),
            "get instance with kwargs: ",
            *["{}: {}".format(key, value)
              for key, value in kwargs.items()])
        phenomenon_label=\
            getattr(
                phenomenon,
                "label",
                phenomenon)
        circuit_region_parameter=\
            circuit_regions if circuit_regions\
            else self._circuit_region_parameter
        assert len(circuit_region_parameter.values) == 1
        measurement_parameters=\
            self._get_measurement_parameters(
                phenomenon_label,
                **kwargs)
        plotted_parameters=\
            self._get_plotted_parameters(
                phenomenon_label,
                **kwargs)
        cell_group_parameters=\
            self._get_cell_group_parameters(
                phenomenon,
                **kwargs)
        pathway_parameters=\
            self._get_pathway_parameters(
                phenomenon_label,
                **kwargs)
        spatial_parameters=\
            self._get_spatial_parameters(
                phenomenon_label,
                **kwargs)
        kwargs=\
            self._get_phenomenon_kwargs(
                phenomenon,
                **kwargs)
        logger.debug(
            logger.get_source_info(),
            "phenomenon kwargs: ",
            *["{}: {}".format(key, value)
              for key, value in kwargs.items()])
        if analysis_type=="analysis":
            return\
                self.Analysis[phenomenon_label](
                    animal=self._circuit_model.animal,
                    brain_region=self._circuit_model.brain_region,
                    measurement_parameters=measurement_parameters,
                    plotted_parameters=plotted_parameters,
                    cell_group_parameters=cell_group_parameters,
                    pathway_parameters=pathway_parameters,
                    spatial_parameters=spatial_parameters,
                    output_dir_path=self._output_dir_path,
                    adapter=self._adapter,
                    *args, **kwargs)
        reference_data=\
            self._get_reference_data(
                phenomenon,
                self._circuit_model,
                circuit_region_parameter.values[0]) #assuming single region
        return\
            self.Validation[phenomenon_label](
                phenomenon=self.phenomenon[phenomenon_label],
                animal=self._circuit_model.animal,
                brain_region=self._circuit_model.brain_region,
                measurement_parameters=measurement_parameters,
                plotted_parameters=plotted_parameters,
                cell_group_parameters=cell_group_parameters,
                pathway_parameters=pathway_parameters,
                spatial_parameters=spatial_parameters,
                reference_data=reference_data,
                output_dir_path=self._output_dir_path,
                adapter=self._adapter,
                *args, **kwargs)

    def _already_measured(self,
            phenomenon,
            region):
        """..."""
        return False #disable, for now
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

    def _append_measurement(self,
            phenomenon,
            measurement):
        """..."""
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
            report,
            region,
            output_dir_path=""):
        """..."""
        logger.debug(
            logger.get_source_info(),
            "save report at {}".format(
                output_dir_path))
        report_path=\
            analysis.save_report(
                report,
                output_dir_path=output_dir_path)
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
            region,
            analysis_type="validation",
            pathways=set(),
            reference_data=None,
            save=True,
            sample_size=20,
            output_dir_path=os.getcwd(),
            *args, **kwargs):
        """..."""
        phenomenon_label=\
            getattr(
                phenomenon,
                "label",
                phenomenon)
        logger.debug(
            logger.get_source_info(),
            "get report for phenomenon {}, region {}"\
            .format(phenomenon_label,
                    region))
        analysis=\
            self.get_instance(
                phenomenon_label,
                circuit_regions=AtlasRegion(
                    values=[region]),
                analysis_type=analysis_type,
                pathways=pathways,
                reference_data=reference_data,
                *args, **kwargs)
        if not self._already_measured(phenomenon_label, region):
            logger.debug(
                logger.get_source_info(),
                "not already measured")
            analysis.adapter.sample_size=\
                sample_size
            measurement=\
                analysis.get_measurement(
                    self._circuit_model,
                    *args,
                    is_permissible=lambda condition: analysis.is_permissible(
                        condition.as_dict),
                    **kwargs)
            self._append_measurement(
                phenomenon,
                measurement)
            logger.debug(
                logger.get_source_info(),
                """appended measurement {}""".format(
                    measurement))
        else:
            logger.debug(
                logger.get_source_info(),
                "Already measured")
        logger.debug(
            logger.get_source_info(),
            "measurement after getting one for {}"\
            .format(phenomenon_label))
        for p, m in self._measurements.items():
            logger.debug(
                "{}: {}".format(p, m))
        report=\
            analysis.get_report(
                self._measurements[phenomenon_label],
                region=region,
                *args, **kwargs)
        if save:
            output_path=\
                os.path.join(
                    output_dir_path,
                    analysis._get_output_dir(
                        model_measurement=self._measurements[
                            phenomenon_label]),
                    "subregion-{}".format(region))
            logger.info(
                logger.get_source_info(),
                "NAS get report output dir path {}"\
                .format(output_dir_path))
            logger.info(
                logger.get_source_info(),
                """Save analysis report at {}""".format(output_path))
            self._save_report(
                analysis,
                report,
                region,
                output_dir_path=output_path)
        return report
