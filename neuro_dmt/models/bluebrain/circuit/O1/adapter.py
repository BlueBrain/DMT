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
from dmt.aii import interface, adapter
import numpy as np
import pandas as pd
from bluepy.v2.circuit import Circuit
from bluepy.v2.enums import Cell
#from bluepy.geometry.roi import ROI as RegionOfInterest
from dmt.vtk.utils.collections import Record
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.author import Author
from dmt.vtk.measurement import StatisticalMeasurement
from dmt.vtk.utils.descriptor import Field, WithFCA
from dmt.vtk.measurement.parameter.random import get_conditioned_random_variate
from dmt.vtk.utils.logging import Logger, with_logging
from neuro_dmt.validations.circuit.composition.by_layer.\
    cell_density import CellDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    cell_ratio import CellRatioValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    inhibitory_synapse_density import InhibitorySynapseDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    synapse_density import SynapseDensityValidation
from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.models.bluebrain.circuit \
    import geometry, cell_collection, utils, BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.random_variate import \
    CircuitRandomVariate, RandomRegionOfInterest
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid, collect_sample, random_location


from neuro_dmt.models.bluebrain.circuit.measurements import composition


@adapter.adapter(Circuit)
@interface.implementation(CellDensityValidation.AdapterInterface)
@interface.implementation(CellRatioValidation.AdapterInterface)
@interface.implementation(InhibitorySynapseDensityValidation.AdapterInterface)
@interface.implementation(SynapseDensityValidation.AdapterInterface)
class BlueBrainModelAdapter(WithFCA):
    """Adapt a circuit from the Blue Brain Project (BBP).
    This adapter was developed for the O1.v6a models developed at BBP in 2017-
    2018. The brain (micro-)circuit models are not atlas based, but are
    organized as hexagonal columns, while respecting the connectivity patterns
    observed in real brain circuits.
    """
    author = Author.zero
    label = 'layer'

    brain_region = Field(
        __name__="brain_region",
        __type__=BrainRegion,
        __doc__="Provides a model independent tag for the brain region."
    )
    spatial_random_variate = Field(
        __name__="spatial_random_variate",
        __type__=type,
        __is_valid_value__=lambda instance, t: issubclass(t, CircuitRandomVariate),
        __doc__="""A slot to set this adapter's spatial parameter --- with
        respect to which a circuit's spatial phenomena can be measured. """
    )
    sample_size = Field(
        __name__="sample_size",
        __type__=int,
        __doc__="""Number of samples to be drawn for each statistical measurement."""
    )
    model_label = Field(
        __name__="model_label",
        __type__=str,
        __doc__="""Label to be used in reporting."""
    )
    def __init__(self, brain_region,
                 circuit_build,
                 spatial_random_variate = None,
                 model_label="in-silico",
                 sample_size=20,
                 sampled_box_shape=50.*np.ones(3), 
                 *args, **kwargs):
                 
        """
        Parameters
        ------------------------------------------------------------------------
        """
        self.brain_region = brain_region
        self.circuit_build = circuit_build
        if spatial_random_variate:
            self.spatial_random_variate = spatial_random_variate
        else:
            self.spatial_random_variate = RandomRegionOfInterest
        self.model_label = model_label
        self.sample_size = sample_size
        self._sampled_box_shape = sampled_box_shape
        try:
            super(BlueBrainModelAdapter, self).__init__(*args, **kwargs)
        except:
            pass

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
            measurement.data = p.filled(measurement.data)
        return measurement

    def statistical_measurement(self, circuit, method, by, *args, **kwargs):
        """..."""
        random_variate\
            = self.spatial_random_variate(circuit,
                                          self.circuit_build,
                                          self.brain_region)\
                  .given(by)
        return self.filled(
            StatisticalMeasurement(
                random_variate=random_variate,
                sample_size=self.sample_size
            )(method, *args, **kwargs),
            by=by
        )

    def spatial_measurement(self, method, circuit, by, *args, **kwargs):
        """..."""
        return self.statistical_measurement(
            circuit, method, by,
            sampled_box_shape=self._sampled_box_shape,
        )

    def get_cell_density(self, circuit, by):
        return self.spatial_measurement(method=composition.CellDensity(circuit),
                                        circuit=circuit,
                                        by=by)
                                        
    def get_cell_ratio(self, circuit):
        """..."""
        method = composition.CellRatio(circuit)
        return self.spatial_measurement(method , circuit, target=target)

    def get_inhibitory_synapse_density(self, circuit, target="mc2_Column"):
        """Implement this!"""
        method = composition.InhibitorySynapseDensity(circuit),
        return self.spatial_measurement(method, circuit, target=target)

    def get_synapse_density(self, circuit, target="mc2_Column"):
        """Implement this!"""
        method = composition.ExtrinsicIntrinsicSynapseDensity(circuit),
        return self.spatial_measurement(method, circuit, target=target)
