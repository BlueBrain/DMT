"""Test develop sonata-connectome analysis."""

import os
from dmt.vtk.measurement\
     import StatisticalMeasurement
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.utils.logging\
    import Logger
from dmt.vtk.utils.collections\
    import Record\
    ,      take
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.plotting\
    import HeatMap
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.measurement.parameter\
    import AtlasRegion\
    ,      CorticalLayer\
    ,      CorticalDepth
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.sscx\
   import get_sscx_atlas_circuit_model\
   ,      get_sscx_fake_atlas_circuit_model
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest
from neuro_dmt.models.bluebrain.circuit.adapter\
     import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.parameters\
     import Mtype\
     ,      MtypePathway
from neuro_dmt.models.bluebrain.circuit.O1.parameters\
    import HyperColumn
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.connectome.\
    pair_synapse_count import RatSSCxPairSynapseCountData
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.connectome.\
    connecton_proabability import RatSSCxConnectionProbability
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.connectome.\
    bouton_density import RatSSCxBoutonDensity
from neuro_dmt.analysis.comparison.validation.circuit.connectome.by_mtype\
    import PairSynapseCountAnalysis\
    ,      PairSynapseCountValidation\
    ,      PathwayConnectionCountAnalysis\
    ,      PathwayConnectionCountValidation\
    ,      PathwayConnectionProbabilityAnalysis\
    ,      PathwayConnectionProbabilityValidation\
    ,      CellBoutonDensityAnalysis\
    ,      CellBoutonDensityValidation

logger=\
    Logger(
        "Test develop random variates",
        level=Logger.level.DEVELOP)
bbadapter=\
    BlueBrainModelAdapter(
        brain_region=brain_regions.sscx,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=20)
iso_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj68/circuits",
        "dev-large/20180904/",
        "CircuitConfig")
iso_circuit_model=\
    get_iso_cortex_circuit_model(
        iso_circuit_config,
        "mouse")
iso_circuit=\
     iso_circuit_model.bluepy_circuit
rat_sscx_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64", "circuits",
        "O1.v6a/20171212",
        "CircuitConfig")
rat_sscx_circuit_model=\
    get_sscx_atlas_circuit_model(
        rat_sscx_circuit_config,
        animal="rat",
        region_label="hypercolumn",
        atlas_path=os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj64", "entities",
            "dev", "atlas",
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018"))
#SSCx circuits are the O1 circuits to be released along with the iso-cortex.
def get_sscx_circuit_config(
        build_date,
        eff_aff_label="",
        from_connectome=True):
    """..."""
    build_date_path=\
        os.path.join(
            "/gpfs/bbp.cscs.ch/project/proj68",
            "circuits/O1",
            build_date)
    circuit_config=\
        "CircuitConfig" if not eff_aff_label\
        else "CircuitConfig-{}".format(eff_aff_label.lower())
    if not from_connectome:
        return\
            os.path.join(
                build_date_path,
                circuit_config)
    return os.path.join(
        build_date_path,
        "connectome",
        "functional",
        "All",
        circuit_config)

def get_sscx_circuit_model(
        build_date,
        from_connectome=True,
        eff_aff_label="",
        animal="mouse",
        region_label ="region"):
    """..."""
    return\
        get_sscx_atlas_circuit_model(
            get_sscx_circuit_config(
                build_date,
                from_connectome=from_connectome,
                eff_aff_label=eff_aff_label),
            animal=animal,
            region_label=region_label)
mtype_values=[
    "L4_TPC", "L2_TPC:A", "L3_TPC:A", "FOO"]

class TestConnectomeAnalysis:
    """Test values of Connectome Analysis sub-classes."""
    def __init__(self,
            circuit_model,
            RegionType,
            region_values=[],
            mtype_values=[],
            sample_size=20):
        """..."""
        self._circuit_model=\
            circuit_model
        self._region_parameter=\
            RegionType(values=region_values)
        self._adapter=\
            BlueBrainModelAdapter(
                brain_region=brain_regions.sscx,
                spatial_random_variate=RandomRegionOfInterest,
                model_label="in-silico",
                sample_size=sample_size)
        self._mtype_values=\
            mtype_values if mtype_values\
            else list(circuit_model.bluepy_circuit.cells.mtypes)
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
        logger.info(
            logger.get_source_info(),
            """Analyzing pathways from {} pre mtypes
            to {} post mtypes""".format(
                len(self._pre_mtype_parameter.values),
                len(self._post_mtype_parameter.values)))
        self.phenomenon={
            "pair_synapse_count"\
            : Phenomenon(
                "Pair Synapse Count",
                "Number of synapses connecting mtype-->mtype \
                pathway cell pairs",
                group="connectome"),
            "pathway_connection_count"\
            : Phenomenon(
                "Pathway Connection Count",
                "Number of connections between an mtype-->mtype \
                pathway cell pairs",
                group="connectome"),
            "pathway_connection_probability"\
            : Phenomenon(
                "Pathway Connection Probability",
                "Proabability that a mtype-->mtype pathway cell pair \
                is connected",
                group="connectome"),
            "bouton_density"\
            : Phenomenon(
                "Bouton Density",
                "Number of boutons per unit length of a cell's axon arbor",
                group="connectome")}
        self.AnalysisType={
            "pair_synapse_count"\
            : PairSynapseCountAnalysis,
            "pathway_connection_count"\
            : PathwayConnectionCountAnalysis,
            "pathway_connection_probability"\
            : PathwayConnectionProbabilityAnalysis,
            "bouton_density"\
            : CellBoutonDensityAnalysis}
        self.ValidationType={
            "pair_synapse_count"\
            : PairSynapseCountValidation,
            "pathway_connection_count"\
            : PathwayConnectionCountValidation,
            "pathway_connection_probability"\
            : PathwayConnectionProbabilityValidation,
            "bouton_density"\
            : CellBoutonDensityValidation}
        self.reference_data={
            "pair_synapse_count"\
            : RatSSCxPairSynapseCountData(),
            "pathway_connection_count"\
            : RatSSCxConnectionProbability(),
            "pathway_connection_probability"\
            : RatSSCxConnectionProbability(),
            "bouton_density"\
            : RatSSCxBoutonDensity()}
        self.measurement_parameters={
            "pair_synapse_count":[
                self._region_parameter,
                self._pre_mtype_parameter,
                self._post_mtype_parameter],
            "pathway_connection_count":[
                self._region_parameter,
                self._pre_mtype_parameter,
                self._post_mtype_parameter],
            "pathway_connection_probability":[
                self._region_parameter,
                self._pre_mtype_parameter,
                self._post_mtype_parameter],
            "bouton_density":[
                self._region_parameter,
                self._mtype_parameter]}
    def get_analysis(self,
            phenomenon_label):
        """..."""
        AnalysisType=\
            self.AnalysisType[
                phenomenon_label]
        return AnalysisType(
            animal=self._circuit_model.animal,
            brain_region=self._circuit_model.brain_region,
            pathway_parameters=[
                self._pre_mtype_parameter,
                self._post_mtype_parameter],
            measurement_parameters=self.measurement_parameters[
                phenomenon_label],
            plotted_parameters=[
                self._pre_mtype_parameter.label,
                self._post_mtype_parameter.label],
            adapter=self._adapter)

    def get_validation(self,
            phenomenon_label):
        ValidationType=\
            self.ValidationType[
                phenomenon_label]
        return ValidationType(
            phenomenon=self.phenomenon[phenomenon_label],
            animal=self._circuit_model.animal,
            brain_region=self._circuit_model.brain_region,
            cell_group_parameters=[
                self._mtype_parameter],
            pathway_parameters=[
                self._pre_mtype_parameter,
                self._post_mtype_parameter],
            measurement_parameters=self.measurement_parameters[
                phenomenon_label],
            plotted_parameters=[
                self._pre_mtype_parameter.label,
                self._post_mtype_parameter.label],
            reference_data=self.reference_data[phenomenon_label],
            adapter=self._adapter)

    def run(self,
        *args, **kwargs):
        """..."""
        syn_count_measurement=\
            self.syn_count_analysis\
                .get_measurement(
                    self._circuit_model,
                    *args, **kwargs)
        syn_count_measurement.data.to_pickle(
            "synapse_count.pickle")
        heatmap=\
            HeatMap(
                Record(
                    data=syn_count_measurement.data,
                    label=syn_count_measurement.label))
        heatmap.save(
            heatmap.plot(),
            file_name="syn_count_heatmap.png")


logger.success(
    logger.get_source_info(),
    "All tests passed!")
