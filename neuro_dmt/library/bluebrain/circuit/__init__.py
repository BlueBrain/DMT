"""Base class for Blue Brain Project Circuit Validations"""

from abc import ABC, abstractmethod
import os
import numpy as np
from bluepy.v2.circuit import Circuit
from dmt.data import ReferenceData
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field, WithFCA
from dmt.analysis.validation.test_case import ValidationTestCase
from neuro_dmt.utils import brain_regions
from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.models.bluebrain.circuit.build import CircuitBuild
from neuro_dmt.data.circuit.composition.cortex.sscx.by_layer \
    import reference_datasets
from neuro_dmt.measurement.parameter import LayerIndex


class BlueBrainValidation(WithFCA, ABC):
    """..."""
    ReferenceDataType = Field.Optional(
        __name__="ReferenceDataType",
        __typecheck__=Field.typecheck.subtype(ReferenceData),
        __doc__="If not provided, assume validation does not use ReferenceData"
    )
    ModelAdapter = Field(
        __name__ = "ModelAdapter",
        __type__ = type,
        __doc__  = """The model adapter to be used with this Blue Brain Project
        Validation."""
    )
    circuit_build = Field(
        __name__="circuit_build",
        __type__=CircuitBuild,
        __doc__="Build for this circuit. Is it atlas based? Is it an O1 microcircuit?"
    )

    brain_region = Field(
        __name__="brain_region",
        __type__=BrainRegion,
        __doc__="""A utility class object that contains some generic information
        about the brain region that this Validation is for."""
    )
    reference_data_path = Field(
        __name__="reference_data_path",
        __type__=str,
        __doc__="Location of the reference data."
    )
    Validation = Field(
        __name__="Validation",
        __typecheck__=Field.typecheck.subtype(ValidationTestCase),
        __doc__="Validation test case that needs a model adapter."
    )

    def __init__(self, 
                 model_name="Blue Brain O1 Circuit for SSCx",
                 sampled_box_shape=np.array([50., 50., 50.]),
                 sample_size=20,
                 output_report_path=".",
                 *args, **kwargs):
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
            = self.ModelAdapter(brain_region=self.brain_region,
                                circuit_build=self.circuit_build,
                                model_label=model_name,
                                sample_size=sample_size,
                                sampled_box_shape=sampled_box_shape,
                                *args, **kwargs)
        self._output_report_path = output_report_path


    @property
    @abstractmethod
    def reference_data(self):
        """..."""
        pass

    def get_validation(self):
        """Construct Validation with Data, and ModelAdapter"""
        return self.Validation(ReferenceDataType=self.ReferenceDataType,
                               data=self.reference_data_path,
                               brain_region=self.brain_region,
                               spatial_parameters=self.spatial_parameters,
                               plotter_type=self.plotter_type,
                               adapter=self._adapter)

    def __call__(self, circuit_config_path):
        """...Call Me..."""
        self.logger.info(
            self.logger.get_source_info(),
            "{} Caller called.".format(self)
        )
        circuit = Circuit(circuit_config_path)

        validation = self.get_validation()
        self.logger.info(
            self.logger.get_source_info(),
            "Blue Brain validation for {}, with plotter_type {}"\
            .format(validation.phenomenon.name, validation.plotter_type),
            "With data {}".format(validation.reference_data)
        )
        report = validation(circuit)

        self.logger.info(
            self.logger.get_source_info(),
            "report: \n{}".format(repr(report))
        )
        report.save(self._output_report_path)

        return report



class BlueBrainCompositionValidation(BlueBrainValidation):
    """..."""
    spatial_parameters = Field(
        __name__ = "spatial_parameters",
        __type__=set,
        __typecheck__ = Field.typecheck.collection(LayerIndex),
        __doc__ = """A composition phenomenon must be measured as a function
        of location in the brain --- spatial_parameters represent these
        locations. For example, you may want cell density as a function of
        'CorticalLayer'."""
    )
