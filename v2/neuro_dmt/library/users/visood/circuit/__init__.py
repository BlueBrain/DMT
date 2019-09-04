"""
Blue brain circuit model.
"""
import os
import yaml
import numpy
import bluepy
import bluepy.v2.circuit as BluePyCircuit
from dmt.tk import collections
from dmt.tk.field import WithFields, lazyfield, Field
from dmt.tk.journal import Logger
from .atlas import BlueBrainCircuitAtlas

logger = Logger(client="{}-instance".format(__file__))

NA = "not-available"


class BlueBrainCircuitModel(WithFields):
    """
    Circuit model developed at the Blue Brain Project.
    """
    label = Field(
        """
        A label to represent your circuit model instance.
        """,
        __default_value__="BlueBrainCircuitModel")
    path_circuit_data = Field(
        """
        Path to the directory where the circuit's data is located. This data is
        loaded as a BluePy circuit.
        """)
    circuit_config = Field(
        """
        Name of the file (that must sit under `.path_circuit_data`)that
        contains the circuit's configuration.
        """,
        __default_value__="CircuitConfig")
    bioname = Field(
        """
        Name of the folder containing inputs, or links to inputs using which
        the circuit was built.
        """,
        __default_value__="bioname")
    file_manifest = Field(
        """
        Name of the file containing the circuit's input MANIFEST.
        """,
        __default_value__="MANIFEST.yaml")
    animal = Field(
        """
        Animal whose brain this circuit models.
        """,
        __default_value__=NA)
    brain_area = Field(
        """
        The brain area modeled.
        """,
        __default_value__=NA,
        __examples__=["Isocortex", "SSCx"])
    release_date = Field(
        """
        Date when this circuit was released.
        """,
        __default_value__=NA)


    @lazyfield
    def path_file_manifest(self):
        """
        Absolute path to the file containing the circuit's (input) manifest.
        """
        return os.path.join(
            self.path_circuit_data,
            self.bioname,
            self.file_manifest)

    @lazyfield
    def bluepy_circuit(self):
        """
        An instance of the BluePy circuit object.
        """
        return BluePyCircuit(
            os.path.join(
                self.path_circuit_data,
                self.circuit_config))

    @lazyfield
    def name(self):
        """
        An appropriate name to call this 
        """
        return "{}_{}".format(self.label, self.release_date)\
            if self.release_date != NA else self.label

    @lazyfield
    def manifest(self):
        """
        Circuit MANIFEST
        """
        with open(self.path_file_manifest, 'r') as manifest_file:
            return yaml.load(
                manifest_file,
                Loader=yaml.FullLoader)
        raise FileNotFoundError(
            self.path_file_manifest,
            "Method execution should not reach here")

    @lazyfield
    def atlas(self):
        """
        Atlas associated with this circuit.
        We assume that the circuit, as well as it's atlas are on a
        local disk.
        """
        return BlueBrainCircuitAtlas(
            path_atlas=self.manifest.common.atlas)

    @lazyfield
    def cells(self):
        """
        Cells associated with the circuit.
        """
        return self.bluepy_circuit.cells

    @lazyfield
    def connectome(self):
        """
        The connectome associated with the circuit.
        """
        try:
            return self.bluepy_circuit.connectome
        except bluepy.exceptions.BluePyError as error:
            logger.warn(
                logger.get_source_info(),
                "Circuit does not have a connectome.",
                "BluePy complained\n: {}".format(error))
        return None
