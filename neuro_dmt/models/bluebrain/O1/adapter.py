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
from neuro_dmt.validations.circuit.composition.by_layer.\
    cell_density import CellDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    cell_ratio import CellRatioValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    inhibitory_synapse_density import InhibitorySynapseDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    synapse_density import SynapseDensityValidation
from neuro_dmt.models.bluebrain \
    import geometry, cell_collection, utils, BlueBrainModelHelper
from neuro_dmt.models.bluebrain.geometry import \
    Cuboid, collect_sample, random_location
from neuro_dmt.models.bluebrain.measurements.circuit.composition import \
    CellDensityMeasurement, \
    CellRatioMeasurement, \
    InhibitorySynapseDensityMeasurement, \
    ExtrinsicIntrinsicSynapseDensityMeasurement



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

    def __init__(self, sampled_box_shape, sample_size, *args, **kwargs):
        """
        Parameters
        ------------------------------------------------------------------------
        sampled_box_shape :: np.ndarray[3D]#shape of the regions to sample
        """

        self._sampled_box_shape = sampled_box_shape
        self._sample_size = sample_size
        self._model_label = kwargs.get('model_label', 'blue_brain_model')
        try:
            super(BlueBrainModelAdapter, self).__init__(*args, **kwargs)
        except:
            pass

    def get_label(self, circuit):
        """method required by adapter interface."""
        return self._model_label

    def layer_roi_sampler(self, circuit, target='mc2_Column'):
        """sampler ROIs for a given layer.

        Return
        ------------------------------------------------------------------------
        Layer -> Generator[RegionOfInterest] #Layer == int
        """
        helper = BlueBrainModelHelper(circuit=circuit, target=target)
        def _get_region_to_explore(layer):
            """..."""
            layer_bounds = helper.geometric_bounds({'layer': layer})
            p0, p1 = layer_bounds.bbox
            return Cuboid(p0 + self._sampled_box_shape,
                          p1 - self._sampled_box_shape)
            
        def get_roi(loc):
            """ROI at location loc."""
            half_box = self._sampled_box_shape / 2.
            return Cuboid(loc - half_box, loc + half_box)

        def roi_sampler(layer):
            """..."""
            return (get_roi(random_location(_get_region_to_explore(layer)))
                    for _ in range(self._sample_size))

        return Record(group = Record(label = "layer", values = [1,2,3,4,5,6]),
                      sample = roi_sampler)


    def get_cell_density(self, circuit):
        """..."""
        cd = CellDensityMeasurement(circuit)
        return cd.statistical_measurement(self.layer_roi_sampler(circuit))

    def get_cell_ratio(self, circuit):
        """..."""
        cr = CellRatioMeasurement(circuit)
        return cr.statistical_measurement(self.layer_roi_sampler(circuit))

    def get_inhibitory_synapse_density(self, circuit):
        """Implement this!"""
        isd = InhibitorySynapseDensityMeasurement(circuit)
        return isd.statistical_measurement(self.layer_roi_sampler(circuit))

    def get_synapse_density(self, circuit):
        """Implement this!"""
        sd = ExtrinsicIntrinsicSynapseDensityMeasurement(circuit)
        return sd.statistical_measurement(self.layer_roi_sampler(circuit))
