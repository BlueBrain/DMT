"""Base class for Blue Brain Project Circuit Validations"""

from abc import ABC, abstractmethod
import numpy as np
from bluepy.v2.circuit import Circuit
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import ClassAttribute
import neuro_dmt
from neuro_dmt.validations.circuit.composition.by_layer import \
    CellDensityValidation, \
    CellRatioValidation, \
    InhibitorySynapseDensityValidation, \
    SynapseDensityValidation
from neuro_dmt.data.circuit.composition.cortex.sscx.by_layer \
    import reference_datasets


class BlueBrainValidation(ABC):
    """..."""
    model_adapter = ClassAttribute(
        __name__ = "model_adapter",
        __type__ = type,
        __doc__  = """The model adapter to be used with this Blue Brain Project
        Validation."""
    )
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
            = self.model_adapter(sampled_box_shape, sample_size,
                                 model_label=model_name)
        self._output_report_path = output_report_path

    @abstractmethod
    def get_validation(self, reference_data_path):
        """..."""
        pass

    def __call__(self, reference_data_path, circuit_config_path,
                 plotter_type=None):
        """...Call Me..."""
        print("{} called".format(self))
        circuit = Circuit(circuit_config_path)

        validation = self.get_validation(reference_data_path)
        print("""Blue Brain validation for {},
        with plotter_type {}""".format(validation.validated_phenomenon.name,
                                       validation.plotter_type.__name__))

        report = validation(circuit)

        print(report)

        report.save(self._output_report_path)

        return report

