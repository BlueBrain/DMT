"""Test develop connectome analysis."""

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
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import PairSynapseCountAnalysis
from neuro_dmt.analysis.comparison.validation.circuit.connectome.by_mtype\
    import PairSynapseCountValidation

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
sscx_circuit=\
    sscx_circuit_model.bluepy_circuit
mtype_values=[
    "L4_TPC", "L2_TPC:A", "L3_TPC:A", "FOO"]
mtype=\
    Mtype(
         sscx_circuit,
         values=mtype_values)
for m in mtype_values:
    if m in sscx_circuit.cells.mtypes:
        assert m in mtype.values
    else:
        assert m not in mtype.values

mtype_unvalidated=\
    Mtype(
        values=mtype_values)
assert all(
    m in mtype_unvalidated.values for m in mtype_values)

mtype_validated=\
    mtype_unvalidated.for_circuit(
        sscx_circuit)
for m in mtype_values:
    if m in sscx_circuit.cells.mtypes:
        assert m in mtype_validated.values
    else:
        assert m not in mtype_validated.values

pre_mtype=\
    Mtype(
        circuit=sscx_circuit,
        label="pre_mtype",
        values=mtype.values)
post_mtype=\
    Mtype(
        circuit=sscx_circuit,
        label="post_mtype",
        values=mtype.values)
pathway=\
    MtypePathway(
        circuit=sscx_circuit,
        pre_mtypes=mtype.values,
        post_mtypes=mtype.values)

class TestAdapterMethods:
    """Test values of adapter methods"""
    def __init__(self,
            circuit_model=sscx_circuit_model):
        """Initialize Me"""
        self._circuit_model=\
            circuit_model
        self.syn_count=\
            bbadapter.get_pathway_synapse_count(
                self._circuit_model,
                parameters=[pre_mtype, post_mtype],
                sample_size=5,
            debug=True)
        self.cnxn_strength=\
            bbadapter.get_pathway_connection_strength(
                self._circuit_model,
                parameters=[pre_mtype, post_mtype],
                sample_size=5,
                debug=True)
        self.cnxn_count=\
            bbadapter.get_pathway_connection_count(
                self._circuit_model,
                parameters=[pre_mtype, post_mtype],
                sample_size=5,
                debug=True)
        self.soma_distance=\
            bbadapter.get_pathway_soma_distance(
                self._circuit_model,
                parameters=[pre_mtype, post_mtype],
                sample_size=5,
                debug=True)

logger.info(
    logger.get_source_info(),
    "test (Analysis) class SynapseCount")


layer_mtypes=\
    {l: [m for m in sscx_circuit.cells.mtypes
         if l in m]
     for l in ["L{}".format(i) for i in range(1, 7)]}

class TestConnectomeAnalysis:
    """Test values of Connectome Analysis sub-classes."""
    def __init__(self,
            circuit_model,
            mtype_values=[],
            sample_size=20):
        """..."""
        self._circuit_model=\
            circuit_model
        self._adapter=\
            BlueBrainModelAdapter(
                brain_region=brain_regions.sscx,
                spatial_random_variate=RandomRegionOfInterest,
                model_label="in-silico",
                sample_size=sample_size)
        pre_mtype_parameter=\
            Mtype(
                circuit=sscx_circuit,
                label="pre_mtype",
                values=mtype_values)\
                if mtype_values else\
                   Mtype(
                       circuit=sscx_circuit,
                       label="pre_mtype")
        post_mtype_parameter=\
            Mtype(
                circuit=sscx_circuit,
                label="post_mtype",
                values=mtype_values)\
                if mtype_values else\
                   Mtype(
                       circuit=sscx_circuit,
                       label="post_mtype")
        hypercolumn=\
            HyperColumn(values=[2])
        logger.info(
            logger.get_source_info(),
            """Analyzing pathways from {} pre mtypes
            to {} post mtypes""".format(
                len(pre_mtype_parameter.values),
                len(post_mtype_parameter.values)))
        self.syn_count_analysis=\
            PairSynapseCountAnalysis(
                animal=circuit_model.animal,
                brain_region=circuit_model.brain_region,
                pathway_parameters=[
                    pre_mtype_parameter,
                    post_mtype_parameter],
                measurement_parameters=[
                    hypercolumn,
                    pre_mtype_parameter,
                    post_mtype_parameter],
                plotted_parameters=[
                    hypercolumn.label,
                    pre_mtype_parameter.label,
                    post_mtype_parameter.label],
                adapter=self._adapter)
        self.syn_count_validation=\
            PairSynapseCountValidation(
                phenomenon=Phenomenon(
                    "Pair Synapse Count",
                    "Number of cells in an mtype --> mtype pathway",
                    group="connectome"),
                animal=circuit_model.animal,
                brain_region=circuit_model.brain_region,
                pathway_parameters=[
                    pre_mtype_parameter,
                    post_mtype_parameter],
                measurement_parameters=[
                    hypercolumn,
                    pre_mtype_parameter,
                    post_mtype_parameter],
                reference_data=RatSSCxPairSynapseCountData(),
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
