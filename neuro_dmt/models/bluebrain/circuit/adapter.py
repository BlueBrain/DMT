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
from dmt.vtk.author import\
    Author
from dmt.vtk.measurement import\
    StatisticalMeasurement
from dmt.vtk.utils.descriptor import\
    Field, WithFCA
from dmt.vtk.measurement.parameter.random import\
    get_conditioned_random_variate
from dmt.vtk.utils.logging import Logger, with_logging
from neuro_dmt.utils.cell_type import CellType
from neuro_dmt.analysis.comparison.validation.circuit.composition.by_layer\
    import CellDensityValidation,\
    CellRatioValidation,\
    InhibitorySynapseDensityValidation,\
    SynapseDensityValidation
from neuro_dmt.utils.brain_regions import\
    BrainRegion
from neuro_dmt.models.bluebrain.circuit import\
    geometry, cell_collection, utils, BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import BlueBrainCircuitModel
from neuro_dmt.models.bluebrain.circuit.random_variate import\
    RandomSpatialVariate,\
    RandomRegionOfInterest,\
    RandomSpanningColumnOfInterest
from neuro_dmt.models.bluebrain.circuit.geometry\
    import Cuboid, collect_sample, random_location
from neuro_dmt.models.bluebrain.circuit.measurements\
    import composition


@interface.implementation(CellDensityValidation.AdapterInterface)
@interface.implementation(CellRatioValidation.AdapterInterface)
@interface.implementation(InhibitorySynapseDensityValidation.AdapterInterface)
@interface.implementation(SynapseDensityValidation.AdapterInterface)
@adapter.adapter(BlueBrainCircuitModel) #circuit model type this can adapt
class BlueBrainModelAdapter(
        WithFCA):
    """Adapt a circuit from the Blue Brain Project (BBP).
    This adapter was developed for the O1.v6a models developed at BBP in 2017-
    2018. The brain (micro-)circuit models are not atlas based, but are
    organized as hexagonal columns, while respecting the connectivity patterns
    observed in real brain circuits.
    """
    author = Author.zero

    label = "adapter"

    brain_region = Field.Optional(
        __name__="brain_region",
        __type__=BrainRegion,
        __doc__="Provides a model independent tag for the brain region.")

    sample_size = Field(
        __name__="sample_size",
        __type__=int,
        __default__=20,
        __doc__="""Number of samples to be drawn for each
        statistical measurement.""")
    
    model_label = Field(
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
        random_variate\
            = get_random_variate(
                circuit_model.geometry,
                *args, **kwargs
            ).given(parameters)
        get_measurement\
            = StatisticalMeasurement(
                random_variate=random_variate,
                sample_size=self.sample_size)
        return\
            self.filled(
                get_measurement(
                    method,
                    *args, **kwargs),
                by=parameters)

    def spatial_measurement(self,
            method,
            circuit_model,
            parameters={},
            *args, **kwargs):
        """..."""
        if not parameters: #special case, sensible for specific area circuits (sscx, CA1)
            return\
                self.statistical_measurement(
                    circuit_model,
                    method,
                    get_random_variate=RandomSpanningColumnOfInterest,
                    parameters={circuit_model.geometry\
                                .spanning_column_parameter()},
                    *args, **kwargs)
        return\
            self.statistical_measurement(
                circuit_model,
                method,
                get_random_variate=RandomRegionOfInterest,
                parameters=parameters,
                sampled_box_shape=self._sampled_box_shape,
                *args, **kwargs)
    
    def get_cell_density(self,
            circuit_model,
            spatial_parameters={},
            by_property=None,
            for_cell_type=CellType.Any,
            *args, **kwargs):
        """..."""
        return self.spatial_measurement(
            method=composition.CellDensity(
                circuit_model.bluepy_circuit,
                by_property=by_property,
                for_cell_type=for_cell_type,
                *args, **kwargs),
            circuit_model=circuit_model,
            parameters=spatial_parameters,
            *args, **kwargs)

    def get_cell_ratio(self,
            circuit_model,
            spatial_parameters={},
            *args, **kwargs):
        """..."""
        return self.spatial_measurement(
            method=composition.CellRatio(
                circuit_model.bluepy_circuit),
            circuit_model=circuit_model,
            parameters=spatial_parameters,
            *args, **kwargs)

    def get_inhibitory_synapse_density(self,
            circuit_model,
            spatial_parameters={},
            *args, **kwargs):
        """..."""
        return self.spatial_measurement(
            method=composition.InhibitorySynapseDensity(
                circuit_model.bluepy_circuit),
            circuit_model=circuit_model,
            parameters=spatial_parameters,
            *args, **kwargs)

    def get_synapse_density(self,
            circuit_model,
            spatial_parameters={},
            *args, **kwargs):
        """..."""
        return self.spatial_measurement(
            method=composition.ExtrinsicIntrinsicSynapseDensity(
                circuit_model.bluepy_circuit),
            circuit_model=circuit_model,
            parameters=spatial_parameters,
            *args, **kwargs)
