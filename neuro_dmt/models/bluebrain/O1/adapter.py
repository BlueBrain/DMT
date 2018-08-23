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
import bluepy.geometry.roi.ROI as RegionOfInterest
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


Measurement = Record #an alias for readablity....

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

    @staticmethod
    def layer_centers(circuit):
        """Center of the cortical layers."""
        com = cell_collection.center_of_mass
        return (com(circuit.cells.positions({'layer': l})) for l in range(1, 7))

    @staticmethod
    def get_sample_1(self, measurement, parameter):
        """another way of sampling...
        Here layer index will become part of the measurement.
        However, it will become harder to consider a measurement such as
        (AxonicFibreDensity,DendriticFibreDensity) by layer. How many components
        does this measurement have? And what if parameter group itself is
        vectorial?
        """
        pd.DataFrame([
            {measurement.component[0]: g,
             measurement.component[1]: v}
            for g, v in measurement.get(p)
            for p in parameter.values
        ]).sort_values(by=measurement.component[0])


   @staticmethod
    def summary_statistic(measurement_sample):
        """Summary of a measurement sample."""
        return measurement_sample.data\
                                 .groupby(parameter_constraint.label)\
                                 .agg(["mean", "std"])\
                                 [measurement_sample.name]

    @staticmethod
    def statistical_measurement(measurement, parameter):
        """Sample a measurement in a circuit, by layer, and summarize it.
        For each layer, measurement is made on each of a sample of regions,
        and the result returned as a data-frame.

        Parameters
        ------------------------------------------------------------------------
        measurement :: Record(name :: str, #name for this measurement
        ~                     get  :: ROI -> float #a function)
        roi_sampler :: Region -> Generator[RegionOfInterest] 

        Return
        ------------------------------------------------------------------------
        Record(name   :: str, #same as measurement.name
        ~      method :: str, #description of how the measurement was made
        ~      data   :: pandas.DataFrame[mean :: float, std :: float])

        For each layer, make the measurement on a sample of regions.
        """
        return self.summary_statistic(self.get_sample(measurement, parameter))

    def sample_region_of_interest(self, circuit, target='mc2_Column'):
        """Get a generator of regions of interest.

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

        def roi_sampler(layer):
            """..."""
            return (geometry.random_location(_get_region_to_explore(layer))
                    for _ in range(self._sample.size))

        return roi_sampler

    def region_cell_counts(self, circuit, roi):
        """Counts of inhibitory and excitatory cells, in a region of interest,
        as a pandas Series."""
        p0, p1 = roi.bbox
        query = {Cell.X: (p0[0], p1[0]),
                 Cell.Y: (p0[1], p1[1]),
                 Cell.Z: (p0[2], p1[2]) }
        props = [Cell.X, Cell.Y, Cell.Z, Cell.SYNAPSE_CLASS]
        cells = circuit.cells.get(query, props)
        cells_inh = cells[cells.synapse_class == "INH"]
        cells_exc = cells[cells.synapse_class == "EXC"]

        inh_in_roi = roi.contains(cells_inh[[Cell.X, Cell.Y, Cell.Z]].values)
        roi_inh_count = np.count_nonzero(inh_in_roi)

        exc_in_roi = roi.contains(cells_exc[[Cell.X, Cell.Y, Cell.Z]].values)
        roi_exc_count = np.count_nonzero(exc_in_roi)

        return pd.Series({"INH": roi_inh_count,
                          "EXC": exc_in_roi,
                          "TOT": roi_exc_count + roi_inh_count})

    def get_cell_density(self, circuit):
        """Implement this!"""
        measurement \
            = Measurement(name="cell_density", get=circuit.stats.cell_density)
        parameter \
            = Parameter(group = Record(label = "layer",
                                       values = self.region_values),
                        sample_values = self.sample_region_of_interest)
        data = 
        return Record(
            phenomenon = Phenomenon("cell density", "cell count in unit volume"),
            label = self.get_label(circuit),
            region_label = "cortical_layer",
            data = self.statistical_measurement(measurement, parameter),
            method = "random cubes were sampled and measured in each layer."
        )

    def get_cell_ratio(self, circuit_model):
        """Implement this!"""
        def region_cell_ratio(self, roi):
            """get cell ratio in a region of interest."""
            ccounts = region_cell_counts(circuit, roi)
            return (1.0 + ccounts['INH']) / (1.0 + ccounts['TOT'])

    def get_inhibitory_synapse_density(self, circuit_model):
        """Implement this!"""
        raise NotImplementedError

    def get_synapse_density(self, circuit_model):
        """Implement this!"""
        raise NotImplementedError
