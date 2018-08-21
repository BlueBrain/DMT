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
import pandas as pd
from bluepy.v2.circuit import Circuit
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
from neuro_dmt.models.bluebrain.geometry import Cuboid, collect_sample

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

    @staticmethod
    def layer_centers(circuit):
        """Center of the cortical layers."""
        com = cell_collection.center_of_mass
        return (com(circuit.cells.positions({'layer': l})) for l in range(1, 7))

    def get_measurement(self, measurement, circuit, target='mc2_Column'):
        helper = BlueBrainModelHelper(circuit)
        layers = range(1,7)

        def region_to_explore(layer):
            """region to explore for layer."""
            layer_bounds = helper.geometric_bounds({'layer': layer})
            p0, p1 = layer_bounds.bbox
            return Cuboid(p0 + self.sampled_box_shape,
                          p1 - self.sampled_box_shape)

        def layer_measurement(layer):
            """layer measurements for layer"""
            ms =  collect_sample(measurement,
                                 region_to_explore(l),
                                 sampled_bbox_shape=self._sampled_bbox_shape,
                                 sample_size=self._sample_size)
            return pd.Series({
                'mean': np.mean(ms),
                'std':  np.std(ms)
            })

        df = pd.DataFrame(layer_measurement(layer) for layer in layers)
        df.index = ["L{}".format(layer) for layer in layers]
        return df

    def get_cell_density(self, circuit):
        """Implement this!"""
        df = self.get_measurement(circuit.stats.cell_density, circuit)
        return Record(
            phenomenon = Phenomenon("cell density", "cell count in unit volume"),
            region_label = "cortical_layer",
            data = df,
            method = "random cubes were sampled and measured in each layer."
        )

    def get_cell_ratio(self, circuit_model):
        """Implement this!"""
        raise NotImplementedError

    def get_inhibitory_synapse_density(self, circuit_model):
        """Implement this!"""
        raise NotImplementedError

    def get_synapse_density(self, circuit_model):
        """Implement this!"""
        raise NotImplementedError
