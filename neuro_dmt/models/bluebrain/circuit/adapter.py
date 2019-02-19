"""Adapters for O1 (v5 and v6a) circuits from the Blue Brain Project.
These adapters leverage the bluepy API.

Guidelines
--------------------------------------------------------------------------------
As a first proof-of-principle we will implement assuming an O1.v6a circuit.
However, we may want to add another level of indirection to abstract away this
detail.
The Circuit type has changed drastically over past years, however if we 
use 'bluepy.v2.circuit.Circuit' as a type for all of them, we will rely on 
manual book-keeping to organize all the different adapters.
"""
from dmt.model import\
    interface, adapter
import numpy as np
import pandas as pd
from bluepy.v2.circuit\
    import Circuit
from bluepy.v2.enums\
    import Cell
#from bluepy.geometry.roi import ROI as RegionOfInterest
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.author\
     import Author
from dmt.vtk.measurement\
     import StatisticalMeasurement
from dmt.vtk.utils.descriptor\
     import Field\
     ,      WithFCA
from dmt.vtk.measurement.parameter.random\
     import get_conditioned_random_variate
from dmt.vtk.utils.logging\
    import Logger\
    ,      with_logging
from neuro_dmt.utils.enums\
    import Direction
from neuro_dmt.utils.cell_type\
    import CellType
from neuro_dmt.analysis.comparison.validation.circuit.composition.by_layer\
    import CellDensityValidation\
    ,      CellRatioValidation\
    ,      InhibitorySynapseDensityValidation\
    ,      SynapseDensityValidation
from neuro_dmt.utils.brain_regions\
    import BrainRegion
from neuro_dmt.models.bluebrain.circuit\
     import geometry\
     ,      cell_collection\
     ,      utils\
     ,      BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import BlueBrainCircuitModel
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomSpatialVariate\
    ,      RandomRegionOfInterest\
    ,      RandomSpanningColumnOfInterest\
    ,      RandomCellVariate\
    ,      RandomConnectionVariate\
    ,      RandomPathwayConnectionVariate
from neuro_dmt.models.bluebrain.circuit.geometry\
    import Cuboid, collect_sample, random_location
from neuro_dmt.models.bluebrain.circuit.measurements\
    import composition as composition_measurements
from neuro_dmt.models.bluebrain.circuit.measurements\
    import connectome as connectome_measurements
from neuro_dmt.models.bluebrain.circuit.parameters\
    import Mtype\
    ,      MtypePathway


@interface.implementation(CellDensityValidation.AdapterInterface)
@interface.implementation(CellRatioValidation.AdapterInterface)
@interface.implementation(InhibitorySynapseDensityValidation.AdapterInterface)
@interface.implementation(SynapseDensityValidation.AdapterInterface)
@adapter.adapter(BlueBrainCircuitModel) #circuit model type adapted
class BlueBrainModelAdapter(
        WithFCA):
    """Adapt a circuit from the Blue Brain Project (BBP).
    This adapter was developed for the O1.v6a models developed at BBP in 2017-
    2018. The brain (micro-)circuit models are not atlas based, but are
    organized as hexagonal columns, while respecting the connectivity patterns
    observed in real brain circuits.
    """
    author=\
        Author.zero
    label=\
        "adapter"
    brain_region=\
        Field.Optional(
            __name__="brain_region",
            __type__=BrainRegion,
            __doc__="Provides a model independent tag for the brain region.")
    sample_size=\
        Field(
            __name__="sample_size",
            __type__=int,
            __default__=20,
            __doc__="""Number of samples to be drawn for each
            statistical measurement.""")
    model_label=\
        Field(
            __name__="model_label",
            __type__=str,
            __default__="BlueBrainCircuitAdapter.",
            __doc__="""Label to be used in reporting.""")
    
    def __init__(self,
            sampled_box_shape=100.*np.ones(3), 
            *args, **kwargs):
        """..."""
        self._sampled_box_shape\
            = sampled_box_shape
        super().__init__(
            *args, **kwargs)

    def get_label(self, circuit):
        """method required by adapter interface."""
        return self.model_label

    def filled(self, measurement, by):
        """...

        Parameters
        ------------------------------------------------------------------------
        measurement :: pandas.DataFrame,  #with an index and columns 'mean' and 'std'
        by :: List[FiniteValuedParameter] #the parameters conditioning
        ~                                 #self.spatial_random_variate
        """
        for p in by:
            measurement.data\
                = p.filled(
                    measurement.data)
        return measurement

    def statistical_measurement(self,
            circuit_model,
            method,
            get_random_variate,
            parameters={},
            *args, **kwargs):
        """..."""
        self.logger.debug(
            self.logger.get_source_info(),
            """get statitistical measurement from adapter with parameters {}"""\
            .format(parameters))
        return\
            self.filled(
                StatisticalMeasurement(
                    random_variate=get_random_variate(
                        circuit_model,
                        *args, **kwargs
                    ).given(
                        parameters),
                    sample_size=self.sample_size
                ).get(
                    method,
                    *args, **kwargs),
                by=parameters)

    def spatial_measurement(self,
            method,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """..."""
        if not parameters: #special case, sensible for specific area circuits (sscx, CA1)
            measurment=\
                self.statistical_measurement(
                    circuit_model,
                    method,
                    get_random_variate=RandomSpanningColumnOfInterest,
                    parameters={circuit_model\
                                .geometry\
                                .spanning_column_parameter()},
                    *args, **kwargs)
        measurement=\
            self.statistical_measurement(
                circuit_model,
                method,
                get_random_variate=RandomRegionOfInterest,
                parameters=parameters,
                sampled_box_shape=self._sampled_box_shape,
                *args, **kwargs)
        return Record(
            brain_region=circuit_model.brain_region,
            **measurement.as_dict)
        return measurement
    
    def get_cell_density(self,
            circuit_model,
            spatial_parameters=[],
            by_property=None,
            for_cell_type=CellType.Any,
            *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                method=composition_measurements.CellDensity(
                    circuit_model.bluepy_circuit,
                    by_property=by_property,
                    for_cell_type=for_cell_type,
                    *args, **kwargs),
                circuit_model=circuit_model,
                parameters=spatial_parameters,
                *args, **kwargs)

    def get_mtype_cell_density(self,
                circuit_model,
                spatial_parameters=[],
                *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                method=composition_measurements.MtypeCellDensity(
                    circuit_model.bluepy_circuit,
                    *args, **kwargs),
                circuit_model=circuit_model,
                parameters=spatial_parameters,
                *args, **kwargs)

    def get_cell_ratio(self,
            circuit_model,
            spatial_parameters=[],
            *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                method=composition_measurements.CellRatio(
                    circuit_model.bluepy_circuit),
                circuit_model=circuit_model,
                parameters=spatial_parameters,
                *args, **kwargs)

    def get_inhibitory_synapse_density(self,
            circuit_model,
            spatial_parameters=[],
            *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                method=composition_measurements.InhibitorySynapseDensity(
                    circuit_model.bluepy_circuit),
                circuit_model=circuit_model,
                parameters=spatial_parameters,
                *args, **kwargs)

    def get_excitatory_synapse_density(self,
            circuit_model,
            spatial_parameters=[],
            *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                method=composition.ExcitatorySynapseDensity(
                    circuit_model.bluepy_circuit),
                circuit_model=circuit_model,
                parameters=spatial_parameters,
                *args, **kwargs)

    def get_synapse_density(self,
            circuit_model,
            spatial_parameters=[],
            *args, **kwargs):
        """..."""
        return\
            self.spatial_measurement(
                method=composition_measurements.ExtrinsicIntrinsicSynapseDensity(
                    circuit_model.bluepy_circuit),
                circuit_model=circuit_model,
                parameters=spatial_parameters,
                *args, **kwargs)

    def pathway_measurement(self,
            get_measurement_method,
            circuit_model,
            parameters={},
            *args, **kwargs):
        """Meassure (mtype --> mtype) pathways."""
        if not parameters:
             parameters=[
                 Mtype(
                     circuit=circuit_model.bluepy_circuit,
                     label="pre_mtype"),
                 Mtype(
                     circuit=circuit_model.bluepy_circuit,
                     label="post_mtype")]
        return\
            self.statistical_measurement(
                circuit_model,
                method=get_measurement_method(
                    circuit=circuit_model.bluepy_circuit,
                    *args, **kwargs),
                get_random_variate=RandomConnectionVariate,
                parameters=parameters,
                *args, **kwargs)

    def get_pathway_synapse_count(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Count synapses in a circuit. The type of the connection
        is specified by the arguments in the method call."""
        return\
            self.pathway_measurement(
                connectome_measurements.PairSynapseCount,
                circuit_model,
                parameters=parameters,
                *args, **kwargs)

    def get_pathway_connection_strength(self,
            circuit_model,
            parameters={},
            *args, **kwargs):
        """Measure the strength of connections in a (mtype->mtype) pathway."""
        return\
            self.pathway_measurement(
                connectome_measurements.ConnectionStrength,
                circuit_model,
                parameters=parameters,
                *args, **kwargs)

    def get_pathway_connection_count(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Get statistical summary of the number of connections in a
        (mtype --> mtype) pathway."""
        return\
            self.pathway_measurement(
                connectome_measurements.PairConnection,
                circuit_model,
                parameters=parameters,
                *args, **kwargs)

    def get_pathway_soma_distance(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Get a statistical summary of the distance between cell somas."""
        return\
            self.pathway_measurement(
                connectome_measurements.SomaDistance,
                circuit_model,
                parameters=parameters,
                *args, **kwargs)

    def get_pathway_interbouton_interval(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Get a statistical summary of interbouton intervals"""
        return\
            self.pathway_measurement(
                connectome_measurements.InterboutonInterval,
                circuit_model,
                parameters=parameters,
                *args, **kwargs)

    def cell_group_measurement(self,
            get_measurement_method,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Make (statistical) measurements of cell groups in a circuit."""
        if not parameters:
            parameters = [
                Mtype(circuit_model.bluepy_circuit)]
        return\
            self.statistical_measurement(
                circuit_model,
                method=get_measurement_method(
                    circuit=circuit_model.bluepy_circuit,
                    *args, **kwargs),
                get_random_variate=RandomCellVariate,
                parameters=parameters,
                *args, **kwargs)

    def get_cell_connection_count(
            circuit_model,
            connection_type=Direction.IN,
            parameters=[],
            *args, **kwargs):
        """Statistical summary of Afferent or Efferent connection count
        of cells in a group, specified by 'parameters'"""
        if connection_type not in {Direction.IN, Direction.OUT}:
            raise ValueError(
                "Unknown connection type {}".format(connection_type),
                "Please set connection_type to one of:\n\t 1.{}\n\t 2.{}"\
                .format(Direction.IN, Direction.OUT))
        method=\
            connectome_measurements.AfferentConnectionCount\
            if connection_type == Direction.IN else\
               connectome_measurements.EfferentConnectionCount
        return\
            self.cell_group_measurement(
                method,
                circuit_model,
                parameters=parameters,
                *args, **kwargs)

    def get_cell_synapse_count(
            circuit_model,
            connection_type=Direction.IN,
            parameters=[]):
        """..."""
        if connection_type not in {Direction.IN, Direction.OUT}:
            raise ValueError(
                "Unknown connection type {}".format(connection_type),
                "Please set connection_type to one of:\n\t 1.{}\n\t 2.{}"\
                .format(Direction.IN, Direction.OUT))
        method=\
            connectome_measurements.AfferentSynapseCount\
            if connection_type == Direction.IN else\
               connectome_measurements.EfferentSynapseCount
        return\
            self.cell_group_measurement(
                method,
                cirucit_model,
                parameters=parameters,
                *args, **kwargs)

