"""
Adapters for circuits from the Blue Brain Project.
"""

import numpy
from dmt.model.interface import implements
from dmt.model.adapter import adapts
from dmt.tk.field import Field, WithFields 
from dmt.tk.collections import take
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from neuro_dmt.models.bluebrain.circuit.model import\
    BlueBrainCircuitModel
from neuro_dmt import terminology
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid


@implements(CellDensityAdapterInterface)
@adapts(BlueBrainCircuitModel)
class BlueBrainCircuitAdapter(WithFields):
    """
    Adapt a circuit from the Blue Brain Project.
    """
    circuit_model = Field(
        """
        The circuit model instance adapted by this `Adapter` instance.
        While not required, attaching a circuit model instance to this
        `Adapter` instance allows us to define an instance of an adapted
        circuit model.
        """,
        __required__=False)
    sample_size = Field(
        """
        Number of samples to make measure a circuit phenomenon.
        """,
        __default_value__=20)
    bounding_box_size = Field(
        """
        Dimensions of the bounding box to sample spatial regions inside
        the circuit.
        """,
        __default_value__=50. * numpy.ones(3))
    random_position_generator = Field(
        """
        A (nested) dict mapping circuit, and a spatial query to their
        random position generator. 
        """,
        __default_value__={})

    @classmethod
    def for_circuit_model(cls, circuit_model, **kwargs):
        """
        Instance of this BlueBrainModelAdapter prepared for a circuit model.
        """
        pass

    def _resolve(self, circuit_model):
        """
        Result the circuit model to adapt.
        """
        if circuit_model:
            return circuit_model

        try:
            return self.circuit_model
        except AttributeError:
            raise AttributeError(
            """
            Attribute `circuit_model` was not set for this `Adapter` instance.
            You may still use this `Adapter` by explicitly passing a
            `circuit_model` instance as an argument to the `AdapterInterface`
            methods it adapts.
            """)

    def _query_hash(self, **kwargs):
        """
        Hash for a query.
        Keep only keyword arguments with non-None values.
        """
        def __hashable(xs):
            """
            Convert xs to a hashable type.
            """
            try:
                h = hash(xs)
                return xs
            except TypeError:
                return ','.join(str(x) for x in xs)

        return hash(tuple(sorted(
           ((key, __hashable(value))
             for key, value in kwargs.items()
             if value is not None),
            key=lambda xy: xy[0])))

    def random_position(self,
            circuit_model,
            **spatial_parameters):
        """
        Get a generator for random positions for given spatial parameters.
        """
        if circuit_model not in self.random_position_generator:
            self.random_position_generator[circuit_model] = {}

        query_hash =\
            self._query_hash(**spatial_parameters)
        if query_hash not in self.random_position_generator[circuit_model]:
            self.random_position_generator[circuit_model][query_hash] =\
                circuit_model.random_positions(**spatial_parameters)

        return self.random_position_generator[circuit_model][query_hash]

    def random_region_of_interest(self,
            circuit_model,
            **spatial_parameters):
        """
        Get a generator for random regions of interest for given spatial
        parameters.
        """
        return (
            Cuboid(
                position - self.bounding_box_size / 2.,
                position + self.bounding_box_size / 2.)
            for position in self.random_position(
                    circuit_model,
                    **spatial_parameters))

    def get_label(self,
            circuit_model):
        """..."""
        return self._resolve(circuit_model).label

    def _get_cell_density_overall(self,
            circuit_model=None,
            **query_parameters):
        """
        Get cell density over the entire relevant volume.

        Pass only keyword arguments that are accepted for cell queries by
        the circuit model.
        """
        query_spatial = {
            key: query_parameters[key]
            for key in ["region", "layer", "depth", "height"]
            if key in query_parameters}
        circuit_model = self._resolve(circuit_model)
        count_cells = circuit_model.get_cell_count(**query_spatial)
        count_voxels = circuit_model.atlas.get_voxel_count(**query_spatial)
        return count_cells/(count_voxels*1.e-9*circuit_model.atlas.volume_voxel)

    @terminology.use(*(terminology.circuit.terms + terminology.cell.terms))
    def get_cell_density(self,
            circuit_model=None,
            mtype=None,
            etype=None,
            region=None,
            layer=None,
            depth=None,
            height=None,
            mesocolumn=None,
            hypercolumn=None,
            synapse_class=None,
            postsynaptic=None,
            presynaptic=None,
            measurement_method=terminology.measurement_method.random_sampling):
        """
        Get cell type density for either the `circuit_model` passes as a
        parameter or `self.circuit_model`.
        """
        circuit_model = self._resolve(circuit_model)
        query = terminology.cell.filter(
            **terminology.circuit.filter(
                mtype=mtype,
                etype=etype,
                region=region,
                layer=layer,
                depth=depth,
                height=height))
        if measurement_method != terminology.measurement_method.random_sampling:
            return self._get_cell_density_overall(
                circuit_model,
                **query)
        region_of_interest = next(
            self.random_region_of_interest(
                circuit_model,
                **query))
        number_cells = circuit_model\
            .get_cell_count(
                region=region_of_interest)
        return number_cells / (1.e-9 * region_of_interest.volume)
