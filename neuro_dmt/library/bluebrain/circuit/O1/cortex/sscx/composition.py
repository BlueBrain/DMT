"""Provide a method that plugs our Adapter for Blue Brain Circuits into
circuit composition validations, and runs them."""

from abc import ABC, abstractmethod
import numpy as np
from bluepy.v2.circuit import Circuit
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import ClassAttribute
import neuro_dmt
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.validations.circuit.composition.by_layer import \
    CellDensityValidation, \
    CellRatioValidation, \
    InhibitorySynapseDensityValidation, \
    SynapseDensityValidation
from neuro_dmt.data.circuit.composition.cortex.sscx.by_layer \
    import reference_datasets


class BlueBrainValidation(ABC):
    """..."""

    @property
    @abstractmethod
    def get_validation(self):
        """Get validation..."""
        pass

    def __init__(self, 
                 model_name="Blue Brain O1 Circuit for SSCx",
                 sampled_box_shape=np.array([50., 50., 50.]),
                 sample_size=20,
                 output_report_path="."):
        """Validate phenomenon.
        
        Parameters
        ----------------------------------------------------------------------------
        reference_data_path :: str #path to the reference data.
        circuit_config_path :: str #path to the CircuitConfig
        model_name :: str #name for the model
        sampled_box_shape :: RegionOfInterest # to be sampled for measurements
        sample_size :: int #number of boxes to be measured for each layer
        """
        self._adapter \
            = BlueBrainModelAdapter(sampled_box_shape, sample_size,
                                    model_label=model_name)
        self._output_report_path = output_report_path

    @abstractmethod
    def get_validation(self, reference_data_path):
        """..."""
        pass

    def __call__(self, reference_data_path, circuit_config_path):
        """...Call Me..."""
        circuit = Circuit(circuit_config_path)

        validation = self.get_validation(reference_data_path)

        report = validation(circuit)

        report.save(self._output_report_path)

        return report


class BlueBrainCellDensityValidation(BlueBrainValidation):
    """..."""

    def get_validation(self, reference_data_path):
        """..."""
        from neuro_dmt.validations.circuit.composition.by_layer \
            import CellDensityValidation
        validation_data = reference_datasets.cell_density(reference_data_path)
        return CellDensityValidation(validation_data, adapter=self._adapter)
                                     
                                       
