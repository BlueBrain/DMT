"""Circuit models from the Blue Brain Project"""
import sys
import numpy as np
import bluepy
from bluepy.v2.circuit\
    import Circuit
from dmt.vtk.utils\
    import collections
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.utils.descriptor\
    import Field\
    ,      WithFCA
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry


class BlueBrainCircuitModel(
        WithFCA):
    """Wrap a bluepy circuit to provide its associated geometry,
    along with other information such as it's release data..."""

    label=\
        "BlueBrainCircuitModel"
    circuit_config=\
        Field(
            __name__ = "circuit_config",
            __type__ = str,
            __doc__ = """Path tot he circuit config that can be loaded as a
            bluepy circuit.""")
    geometry_type=\
        Field(
            __name__ = "geometry_type",
            __type__ = type,
            __typecheck__ = Field.typecheck.subtype(CircuitGeometry),
            __doc__ = """A plugin that provides methods for a circuit's
            geometry. A subtype of 'class CircuitGeometry' is expected.""")
    animal=\
        Field(
            __name__="animal",
            __type__=str,
            __doc__="Animal for which this circuit was built.")
    brain_region=\
        Field(
            __name__ = "brain_region",
            __type__ = brain_regions.BrainRegion,
            __doc__ = "The brain region modeled.")
    release_date=\
        Field.Optional(
            __name__="release_date",
            __type__=str,
            __doc__="date when this circuit was released.")
    
    def __init__(self,
            *args, **kwargs):
        super().__init__(
            *args, **kwargs)
        self._implied_circuit = None #the implied bluepy circuit
        self._geometry = None

    def get_release_date(self,
            *args, **kwargs):
        """..."""
        try:
            return self.release_date
        except AttributeError:
            pass
        return None

    def get_label(self,
            *args, **kwargs):
        """Get a label that can be used to name files."""
        label=\
            "{}_{}".format(
                self.label,
                self.brain_region.label)
        date=\
            self.get_release_date(
                *args, **kwargs)
        return "{}_{}".format(label, date) if date else label

    def get_uri(self,
            *args, **kwargs):
        """Location of this circuit."""
        return self.circuit_config

    @property
    def bluepy_circuit(self):
        """..."""
        if not self._implied_circuit:
            self._implied_circuit=\
                Circuit(self.circuit_config)
        return self._implied_circuit
                    
    @property
    def circuit(self):
        """..."""
        return self.bluepy_circuit

    @property
    def geometry(self):
        """..."""
        if not self._geometry:
            self._geometry=\
                self.geometry_type(
                    self.circuit)
        return\
            self._geometry

    @property
    def region_label(self):
        """..."""
        try:
            return self.region_label
        except AttributeError:
            return\
                self.geometry.region_label
        return "region" 

    @property
    def cells(self):
        """..."""
        return self.bluepy_circuit.cells

    @property
    def connectome(self):
        """..."""
        try:
            return self.bluepy_circuit.connectome
        except bluepy.exceptions.BluePyError as e:
            self.logger.alert(
                self.logger.get_source_info(), 
                "circuit does not have a connectome",
                "Caught Exception :\n  {}".format(e))
            return None

    def filter_condition(self,
            cell_gids,
            condition):
        """filter cell gids that satisfy a Condition."""
        cell_gids=\
            cell_gids.astype(np.uint32)
        cell_query=\
            condition.as_dict
        if "region" in cell_query:
            cell_query[self.region_label]=\
                cell_query.pop("region")
        conditioned_gids=\
            self.cells.ids(
                cell_query)
        mask=\
            np.in1d(
                cell_gids,
                conditioned_gids,
                assume_unique=True)
        return cell_gids[mask]

    def filter_region(self,
            cell_gids,
            condition):
        """filter cells (by gid) that fall in a given region.
        region value None will be handled as Any"""
        region=\
            condition.get_value(
                self.region_label)
        if not region:
            return cell_gids
        return\
            self.filter_condition(
                cell_gids,
                Condition([
                    (self.region_label, region)]))
        # cell_regions=\
        #     self.cells\
        #         .get(
        #             cell_gids,
        #             properties=self.region_label)
        # return\
        #    cell_regions[cell_regions == region].index.values

from neuro_dmt.models.bluebrain.circuit.circuit_model.o1_circuit_model\
    import O1CircuitModel
from neuro_dmt.models.bluebrain.circuit.circuit_model.atlas_based_circuit_model\
    import AtlasBasedCircuitModel\
    ,      FakeAtlasBasedCircuitModel


