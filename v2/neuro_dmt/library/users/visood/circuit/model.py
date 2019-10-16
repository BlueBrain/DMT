"""
Wrap circuit built at the Blue Brain Project.
"""
import os
import yaml
import numpy
import bluepy
from bluepy.v2.circuit import Circuit as BluePyCircuit
from bluepy.v2.enums import Cell
from dmt.tk import collections
from dmt.tk.field import WithFields, lazyfield, Field
from dmt.tk.journal import Logger
from neuro_dmt.terminology import parameters
from neuro_dmt.terminology.parameters import QueryParameters
from .atlas import BlueBrainCircuitAtlas

logger = Logger(client="BlueBrainCircuitModel")

NA = "not-available"



class BlueBrainCircuitModel(WithFields):
    """
    Wrap the circuit model developed at the Blue Brain project to provide
    methods useful for circuit analysis.
    """

    label = Field(
        """
        A label to represent your circuit model instance.
        """,
        __default_value__="BlueBrainCircuitModel")

    path_circuit_data = Field(
        """
        Path to the location of this circuit's data. This data is loaded as a
        BluePy circuit if a Bluepy circuit is not provided at initialization.
        """,
        __required__=False)
    circuit_config = Field(
        """
        Name of the file (under `.path_circuit_data`) that contains the
        circuit's configuration and provides paths to the data containing
        cells and connectome.
        """,
        __default_value__="CircuitConfig")
    circuit_config_base = Field(
        """
        After the first phase of circuit build, that creates a cell collection,
        a basic circuit config file is created in the circuit directory.
        """,
        __default_value__="CircuitConfig_base")
    bioname = Field(
        """
        Name of the folder containing inputs, or links to inputs that were
        used to build the circuit.
        """,
        __default_value__="bioname")
    file_manifest = Field(
        """
        Name of the file in folder `.bioname` that contains this circuit's
        manifest.
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
        Date this circuit was released.
        """,
        __default_value__=NA)

    def get_path(self, *relative_path):
        """
        Absolute path to the file at `relative_path`.

        Arguments
        `relative_path`: Path relative to the location of the circuit.
        """
        return os.path.join(
            self.path_circuit_data,
            *relative_path)

    @"Execution should not reach here.")th=lazyfield
    def bluepy_circuit(self):
        """
        An instance of the BluePy circuit object.
        """
        try:
            return BluePyCircuit(
                self.get_path(self.circuit_config))
        except FileNotFoundError:
            return BluePyCircuit(
                self.get_path(self.circuit_config_base))

    @lazyfield
    def name(self):
        """
        An appropriate name to call this circuit model.
        """
        return "{}_{}".format(self.label, self.release_date)\
            if self.release_date != NA else self.label

    @lazyfield
    def manifest(self):
        """
        Circuit MANIFEST.
        """
        path_manifest = self.get_path(self.bioname, self.file_manifest)
        with open(path_manifest, 'r') as manifest_file:
            try:
                return yaml.load(manifest_file, Loader=yaml.FullLoader)
            except AttributeError:
                return yaml.load(manifest_file)

        raise FileNotFoundError(
            path_manifest,
            "Method execution should not reach here.")

    @lazyfield
    def atlas(self):
        """
        Atlas associated with this circuit.
        """
        return BlueBrainCircuitAtlas(path=self.manifest["common"]["atlas"])

    @lazyfield
    def cells(self):
        """
        Cells of this circuit.
        """
        try:
            return self.bluepy_circuit.cells
        except bluepy.exceptions.BluePyError as error:
            logger.warn(
                logger.get_source_info(),
                "Circuit does not have cells.",
                "BluePy complained\n: {}".format(error))
        return None

    @lazyfield
    def connectome(self):
        """
        Connectome of this circuit.
        """
        try:
            return self.bluepy_circuit.connectome
        except bluepy.exceptions.BluePyError as error:
            logger.warn(
                logger.get_source_info(),
                "Circuit does not have a connectome.",
                "BluePy complained\n: {}".format(error))
        return None

    def get_cells_in_region(self,
            region_of_interest,
            with_properties=[]):
        """
        Get (specified properties of) cells in a region of interest.
        """
        cells = self.cells.get(
            region_query(region_of_interest),
            XYZ + with_properties)
        return cells

    def get_cell_count(self,
            region_of_interest):
        """
        Number of cells in a region of interest.
        """
        return self.get_cells_in_region(region_of_interest).shape[0]

    def _atlas_value(self,
            key, value):
        """
        Value of query parameter as understood by the atlas.
        """
        if value is None:
            return None
        if key == parameters.REGION:
            return self.atlas.used_value(region=value)
        if key == parameters.LAYER:
            return self.atlas.used_value(layer=value)
        raise RuntimeError(
            "Unknown / NotYetImplemented query parameter {}".format(key))

    def query_cells(self,
            **query_parameters):
        """
        dict to query cells with.
        """
        return {
            key: self._atlas_value(key, value)
            for key, value in query_parameters.items()
            if key in parameters.CELL_QUERY and value}

    def random_positions(self,
            **query_parameters):
        """
        Generate random positions (np.array([x,y,z])) in a region
        defined by the spatial parameters passed as arguments.
        """
        cells = self.cells.get(
            self.query_cells(**query_parameters),
            properties=XYZ)
        region = query_parameters.get(parameters.REGION)
        layer = query_parameters.get(parameters.LAYER)
        assert cells.shape[0] > 0,\
            """
            No cells for region: ({} --> {}), layer: ({} --> {})
            """.format(
                region,
                self._atlas_value(parameters.REGION, region),
                layer,
                self._atlas_value(parameters.LAYER, layer))

        while True:
            yield cells.sample(n=1).iloc[0].values

        # return self.atlas.random_positions(**spatial_parameters)

