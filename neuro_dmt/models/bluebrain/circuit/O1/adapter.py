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
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.measurement.parameter.random import get_conditioned_random_variate
from dmt.vtk.utils.logging import Logger
from neuro_dmt.validations.circuit.composition.by_layer.\
    cell_density import CellDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    cell_ratio import CellRatioValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    inhibitory_synapse_density import InhibitorySynapseDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    synapse_density import SynapseDensityValidation
from neuro_dmt.models.bluebrain.circuit \
    import geometry, cell_collection, utils, BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.parameters import \
    CircuitRandomVariate
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid, collect_sample, random_location

from neuro_dmt.models.bluebrain.circuit.measurements import composition


@adapter.adapter(Circuit)
@interface.implementation(CellDensityValidation.AdapterInterface)
@interface.implementation(CellRatioValidation.AdapterInterface)
@interface.implementation(InhibitorySynapseDensityValidation.AdapterInterface)
@interface.implementation(SynapseDensityValidation.AdapterInterface)
class BlueBrainModelAdapter:
    """Adapt a circuit from the Blue Brain Project (BBP).
    This adapter was developed for the O1.v6a models developed at BBP in 2017-
    2018. The brain (micro-)circuit models are not atlas based, but are
    organized as hexagonal columns, while respecting the connectivity patterns
    observed in real brain circuits.
    """
    author = Author.zero
    label = 'layer'

    spatial_random_variate = Field(
        __name__="spatial_parameter",
        __type__=CircuitRandomVariate, #define this
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

    #def __init__(self, sampled_box_shape, sample_size,
    #             *args, **kwargs):
    def __init__(self, *args, **kwargs):
                 
        """
        Parameters
        ------------------------------------------------------------------------
        sampled_box_shape :: np.ndarray[3D]#shape of the regions to sample
        """
        self._logger = Logger("{}Logger".format(self.__class__.__name__),
                              level=kwargs.get("logger_level", Logger.level.PROD))
        #self._sampled_box_shape = sampled_box_shape
        self.sample_size = kwargs.get("sample_size", 20)
        self.model_label = kwargs.get('model_label', 'in-silico')
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

    def statistical_measurement(self, method, by, *args, **kwargs):
        """..."""
        random_variate\
            = self.spatial_random_variate.given(conditioning_variables)
        return self.filled(
            StatisticalMeasurement(
                random_variate=random_variate
                sample_size=self.sample_size
            )(method, *args, **kwargs),
            by=by
        )

    def spatial_measurement(self, method, circuit, by,
                            target=None):
        """..."""
        measurement= self.statistical_measurement(
            method,
            by=by,
            target=target, #track this kwarg --- how is it propagate?
            sampled_box_shape=self._sampled_box_shape,
            sample_size=self._sample_size
        )
        return measurement

    def get_cell_density(self, circuit, spatial_parameter=None,
                         target="mc2_Column"):
        method = composition.CellDensity(circuit)
        return self.spatial_measurement(method, by=spatial_parameter,
                                        circuit, target=target)
                                        
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
