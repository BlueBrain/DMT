"""Provide a method that plugs our Adapter for Blue Brain Circuits into
circuit composition validations, and runs them."""
import os
from dmt.vtk.utils.collections import Record
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.data.reference import MultiReferenceData
from dmt.vtk.utils.exceptions import MissingRequiredKeywordArgument
from neuro_dmt.validations.circuit.composition.by_layer import \
    CellDensityValidation, \
    CellRatioValidation, \
    InhibitorySynapseDensityValidation, \
    SynapseDensityValidation
from neuro_dmt.data.circuit.composition.cortex.sscx.by_layer \
    import reference_datasets
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.library.bluebrain.circuit import BlueBrainCompositionValidation
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.O1.build import O1Circuit


class BlueBrainCellDensityData(MultiReferenceData):
    """..."""
    def _load_from_location(self, data_location):
        """Load data from a location
        We provide a default implementation that makes a trivial check.
        The concrete implementation needs to complete this implementation only
        if data will be loaded from a location.
        """
        if not self._is_location(data_location):
            self.logger.alert(
                self.logger.get_source_info(),
                "Cannot load data from argument 'data_location' {}"
                .format(data_location)
            )
            return None

        self.logger.alert(
            self.logger.get_source_info(),
            "Load data from location {}.".format(data_location)
        )
        return reference_datasets.cell_density(data_location)

    def _get_data(self, data, *args, **kwargs):
        """..."""
        #if "data" not in kwargs:
        #    raise MissingRequiredKeywordArgument("data")

        if not self._is_location(data):
            if isinstance(data, Record):
                try:
                    return (data.datasets, data.primary)
                except AttributeError:
                    pass
        else:
            return self._get_data(self._load_from_location(data))

        primary = kwargs.get("primary", None)
        return (data, primary)


    @property
    def description(self):
        """..."""
        try:
            return self._description
        except AttributeError:
            try:
                return self.primary.what
            except AttributeError as e:
                return "Not Available."
        return None




class BlueBrainCellDensityValidation(BlueBrainCompositionValidation):
    """..."""
    circuit_build = O1Circuit
    plotter_type = BarPlotComparison
    ModelAdapter = BlueBrainModelAdapter
    ReferenceDataType = BlueBrainCellDensityData
    brain_region = brain_regions.cortex
    spatial_parameters = {CorticalLayer()}
    Validation = CellDensityValidation
    reference_data_path = os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                                       "work/validations/dmt",
                                       "examples/datasets/cortex/sscx/rat",
                                       Validation.phenomenon.label)

    @property
    def reference_data(self):
        """..."""
        return reference_datasets.cell_density(self.reference_data_path)

                                       
validation = dict(cell_density=BlueBrainCellDensityValidation)
