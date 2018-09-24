"""Parameters that should be valid for all Blue Brain Circuit Models."""

from abc import ABC, abstractmethod
import numpy as np
from bluepy.v2.enums import Cell
from bluepy.geometry.roi import ROI
from dmt.vtk.utils.collections import *
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.measurement.parameter.random import ConditionedRandomVariate
from dmt.vtk.utils.logging import Logger, with_logging
from dmt.vtk.utils.descriptor import Field, WithFCA
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location



class NamedTarget(FiniteValuedParameter):
    """..."""
    value_type = str
    label = "$target"
    def __init__(self, *args, **kwargs):
        self.__values = ["mc{}_Column".format(n) for n in range(1, 7)]
        super(NamedTarget, self).__init__(
            value_order = dict(zip(self.__values, range(len(self.__values)))),
            value_repr = dict(zip(self.__values, self.__values)),
            *args, **kwargs
        )


#@with_logging(Logger.level.STUDY)
class BrainRegionSpecific(WithFCA, ABC):
    """Brain region specific methods.
    These methods will typcially be abstract in some other code.
    BrainRegionSpecific classes will not be useful on their known.
    They simply provide code specialized to particular brain regions."""
    region_label = Field(
        __name__="region_label",
        __type__=str,
        __doc__="""Name of the brain region that this class specifies.""",
        __examples__=["cortical", "thalamic"]
    )
    cell_group_params = Field(
        __name__="cell_group_params",
        __type__=tuple,
        __doc__="""Tuple of cell query fields that group cells, and whose values
        measurements will be (jointly) conditioned on. Use this information to
        create cell queries. You can stick in anything here that a cell
        query will accept. The entries here must be a subset of condition_type
        fields.""",
        __examples__=[("layer", "target"), ("layer", ), ("mtype", "layer",)]
    )
    def __init__(self, cell_group_params, target=None, *args, **kwargs):
        """...

        Parameters
        ------------------------------------------------------------------------
        cell_group_params :: tuple #...
        """
        self.cell_group_params = cell_group_params
        self._target = target
        try:
            super(BrainRegionSpecific, ABC).__init__(*args, **kwargs)
        except:
            pass
        
    @property
    def target(self):
        """..."""
        if not self._target:
            self.logger.alert("No target set for {} instance."\
                              .format(self.__class__.__name__))
        return self._target

    @abstractmethod
    def cell_query(self, condition, *args, **kwargs):
        """A dict that can be passed to circuit.cells.get(...).
        Concrete implementation may override """
        pass
        return {p: condition.get_value(p) for p in self.cell_group_params}

    def with_target(self, query_dict, target_label = "$target"):
        """Add target to a condition.

        Note
        ------------------------------------------------------------------------
        We need to find a more elegant solution to sticking target in queries.
        """
        self.logger.devnote(
            """{}.with_target is a hack. We stick the target in. We should look
            for a more disciplined and elegant solution."""\
            .format(self.__class__.__name__)
        )
        query_dict[target_label] = self._target
        return query_dict


class CircuitRandomVariate(ConditionedRandomVariate):
    """Generator of random values, for a (blue) brain circuit."""
    def __init__(self, circuit, brain_region,
                 condition_type=Record(), *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        brain_region :: BrainRegionSpecific #for brain region specific methods
        """
        self._circuit = circuit
        self._brain_region = brain_region
        self._helper = BlueBrainModelHelper(circuit=circuit)
        super(CircuitRandomVariate, self)\
            .__init__(condition_type=condition_type,
                      *args, **kwargs)

    def given(self, *conditioning_vars):
        """Set the condition type."""
        return super(CircuitRandomVariate, self)\
            .given(*conditioning_vars, reset_condition_type=True)

    @property
    def circuit(self):
        """..."""
        return self._circuit

    @property
    def brain_region(self):
        """..."""
        return self._brain_region


class RandomPosition(CircuitRandomVariate):
    """Generate random positions in the circuit region."""
    label = "position"
    value_type = np.ndarray #dimension 3

    def __init__(self, circuit, brain_region,
                 offset=50., *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        """
        self.offset = offset
        super(RandomPosition, self)\
            .__init__(circuit, brain_region, *args, **kwargs)

    def cell_query(self, condition, *args, **kwargs):
        """...redirect to brain region.
        This allows us to not have to subclass from RandomPosition and 
        BrainRegionSpecific mixins. We can redirect to 'self.brain_region'.
        We could """
        return self.brain_region.cell_query(condition, *args, **kwargs)

    def conditioned_values(self, condition, *args, **kwargs):
        """Generator of positions."""
        bounds\
            = self._helper\
                  .geometric_bounds(self.cell_query(condition),
                                    target=self.brain_region.target)
        if bounds is None:
            return ()
        while True:
            yield random_location(Cuboid(bounds.bbox[0] + self.offset,
                                         bounds.bbox[1] - self.offset))


class RandomRegionOfInterest(RandomPosition):
    """Random ROIs"""
    value_type = ROI
    label = "roi"

    def __init__(self, circuit, brain_region,
                 sampled_box_shape=100.*np.ones(3),
                 *args, **kwargs):
        """..."""
        self.sampled_box_shape = sampled_box_shape
        super(RandomRegionOfInterest, self)\
            .__init__(circuit, brain_region,
                      offset=sampled_box_shape/2.,
                      *args, **kwargs)

    def conditioned_values(self, condition, *args, **kwargs):
        """..."""
        half_box = self.sampled_box_shape / 2.
        positions = super(RandomRegionOfInterest, self)\
                    .conditioned_values(condition, *args, **kwargs)
        for position in positions:
            yield Cuboid(position - half_box, position + half_box)


class RandomBoxCorners(RandomRegionOfInterest):
    """..."""
    value_type = tuple #length 2
    label = "box_corners"
    def __init__(self, circuit, brain_region,
                 sampled_box_shape=50.*np.ones(3),
                 *args, **kwargs):
        """..."""
        super(RandomBoxCorners, self)\
            .__init__(circuit, brain_region,
                      sampled_box_shape=sampled_box_shape,
                      *args, **kwargs)

    def conditioned_values(self, condition, *args, **kwargs):
        """"..."""
        rois = super(RandomBoxCorners, self)\
               .conditioned_values(condition, *args, **kwargs)
        for roi in rois:
            yield roi.bbox


class Mtype(ConditionedRandomVariate):
    """Mtype groups cell gids."""
    label = "mtype"
    value_type = str
    grouped_variable = Record(__type__ = int, name="cell_gid")
                              

    def __init__(self, circuit, *args, **kwargs):
        """..."""
        self._circuit = circuit
        self._helper  = BlueBrainModelHelper(circuit=circuit)
        self._values = None #initialized when 'self.values' first called
        self._order_dict  = None #initialized when 'self.order' first called
        self._mtype_groups = None #cells GIDs for a given mtype
        super(Mtype, self).__init__(*args, **kwargs)

    @property
    def mtype_groups(self):
        """..."""
        if self._mtype_groups is None:
            self._mtype_groups = self._helper.cell_mtypes().groupby(Cell.MTYPE)
        return self._mtype_groups

    @property
    def values(self):
        """What mtypes may cells have in a circuit?
        Since this computation can be expensive, we will cache the results."""
        if not self._values:
            self._values = set(self.mtype_groups.keys())
        return self._values

    def order(self, mtype):
        """We need the values to order them."""
        if not self._order_dict:
            N = len(self.values)
            self._order_dict\
                = dict(zip(sorted(list(self.values)), range(1, N + 1)))
        return self._order_dict[mtype]

    def is_valid(self, value):
        """..."""
        return True

    def repr(self, value):
        """..."""
        return value

    def cell_gids(self, mtype):
        """Cell gids for a given mtype."""
        return self.mtype_groups[mtype]

    def random_grouped_values(self, mtype, *args, **kwargs):
        """Generator of all the values of the grouped variable"""
        target = kwargs.get("target", None)
        target_cells = self._helper.target_cells(target)

        while True:
            try:
                gids = self.cell_gids(mtype)
                assert(len(gids) > 0)
            except:
                raise ValueError("No cells of mtype {} in the circuit."\
                                 .format(mtype))
            g = np.random.choice(gids)
            if g in target_cells:
                yield g
            else:
                continue


class PreMtype(Mtype):
    """PreMtype is the same as Mtype except some labels..."""
    label = "pre_mtype"
    grouped_variable = Record(__type__=int, name="pre_gid")


class PostMtype(Mtype):
    """PostMtype is the same as Mtype except some labels..."""
    label = "post_mtype"
    grouped_variable = Record(__type__=int, name="post_gid")


class Pathway(ConditionedRandomVariate):
    """Pathway groups mtype-->mtype connections."""

    label = "pathway"
    value_type = tuple #(pre_mtype :: str, post_mtype :: str)
    grouped_variable = Record(
        __type__=tuple, #(pre_gid :: int, post_gid :: int)
        name="connection"
    )
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        self._circuit = circuit
        self._helper  = BlueBrainModelHelper(circuit=circuit)
        self._mtypes = None
        self._values = None #initialized when first needed
        self._order_dict = None #initialized when first needed
        self._connections = None #this will be a dictionary -- to cache results
        super(Pathway, self).__init__(*args, **kwargs)

    @property
    def mtypes(self):
        """..."""
        if self._mtypes is None:
            self._mtypes = self._helper.cell_mtypes()
        return self._mtypes

    @property
    def values(self):
        """All Pathway values (pre_mtype, post_mtype), that are possible."""
        if not self._values:
            self._values = set([(pre, post) for pre in self.mtypes.values
                               for post in self.mtypes.values])
        return self._values

    def order(self, connection):
        """An order on Pathway values."""
        if not self._order_dict:
            N = len(self.values)
            self._order_dict\
                = dict(zip(sorted(self.values), range(1, N + 1)))
        return self._order_dict[connection]

    def is_valid(self, value):
        """Implement this."""
        return True

    def repr(self, value):
        return "{}-->{}".format(value[0], value[1])

    def connections(self, pre_mtype, post_mtype):
        """Get connections for pathway pre_mtype --> post_mtype."""
        def __efferent(pre_gid):
            """..."""
            conn = self._circuit.connectome
            return (post_gid for post_gid in conn.efferent_gids(pre_gid)
                    if self.mtypes.loc[post_gid] == post_mtype)
                   
        if not self._connections:
            self._connections = {}
        if pre_mtype not in self._connections:
            self._connections[pre_mtype] = {}
        if post_mtype not in self._connections[pre_mtype]:
            pre_gids = self.mtypes.index[self.mtypes[Cell.MTYPE] == pre_mtype]
            self._connections[pre_mtype][post_mtype]\
                = [(pre, post) for pre in pre_gids for post in __efferent(pre)]

        return self._connections[pre_mtype][post_mtype]

    def random_grouped_values(self, pathway, *args, **kwargs):
        """..."""
        target = kwargs.get("target", None)
        target_cells = self._helper.target_cells(target)
        n = kwargs.get("sample_size", 20)

        pre_mtype = pathway[0]
        post_mtype = pathway[1]

        while True:
            try:
                cs = self.connections(pre_mtype, post_mtype)
                assert(len(cs) > 0)
            except:
                raise ValueError("{}-->{} not a valid pathway"\
                                 .format(pre_mtype, post_mtype))

            pre_gid, post_gid = np.random.choice(cs)
            if pre_gid in target_cells and post_gid in target_cells:
                yield (pre_gid, post_gid)
            else:
                continue
