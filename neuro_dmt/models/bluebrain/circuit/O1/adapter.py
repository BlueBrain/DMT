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
from dmt.vtk.measurement.parameters import GroupParameter
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
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid, collect_sample, random_location

from neuro_dmt.models.bluebrain.circuit.measurements import composition
from neuro_dmt.models.bluebrain.circuit.O1.parameters import CorticalLayer



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
    region_label = 'layer'
    region_values = [1, 2, 3, 4, 5, 6]

    def __init__(self, sampled_box_shape, sample_size,
                 *args, **kwargs):
        """
        Parameters
        ------------------------------------------------------------------------
        spatial_parameter :: Callable #should return a GroupParameter
        sampled_box_shape :: np.ndarray[3D]#shape of the regions to sample
        """
        self._sampled_box_shape = sampled_box_shape
        self._sample_size = sample_size
        self._model_label = kwargs.get('model_label', 'blue_brain_model')
        self._spatial_parameter = kwargs.get("spatial_parameter", None)
        try:
            super(BlueBrainModelAdapter, self).__init__(*args, **kwargs)
        except:
            pass

    def get_label(self, circuit):
        """method required by adapter interface."""
        return self._model_label

    @property
    def spatial_parameter(self):
        """..."""
        return self._spatial_parameter

    @spatial_parameter.setter
    def spatial_parameter(self, value):
        """..."""
        if not isinstance(value, GroupParameter):
            raise ValueError("{} not a {}".format(value, "GroupParameter"))
        self._spatial_parameter = value

    def statistical_measurement(self, method, by, *args, **kwargs):
        """..."""
        return StatisticalMeasurement(method, by)(*args, **kwargs)

    def spatial_measurement(self, method, circuit, target=None):
        """..."""
        spatial_parameter = self._spatial_parameter(circuit)
        measurement\
            = self.statistical_measurement(method,
                                           by=spatial_parameter,
                                           target=target,
                                           sampled_box_shape=self._sampled_box_shape,
                                           sample_size=self._sample_size)

        missing = list(spatial_parameter.values - set(measurement.data.index))
        missingdf = pd.DataFrame({'mean': len(missing) * [0, ],
                                  'std': len(missing) * [0, ]})
        missingdf.index = missing
        measurement.data = pd.concat((measurement.data, missingdf))

        #we may want to use GroupParameter.order at this point...
        old_index = measurement.data.index
        measurement.data.index = [spatial_parameter.repr(i) for i in old_index]
        measurement.data.index.name = old_index.name

        return measurement

    def get_cell_density(self, circuit, target="mc2_Column"):
        method = composition.CellDensity(circuit)
        return self.spatial_measurement(method, circuit, target=target)
                                        
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
