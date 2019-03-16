"""BBP specific random variates, and related utilities."""
from abc import ABC, abstractmethod
import random
import numpy as np
import pandas as pd
from bluepy.v2.enums\
    import Cell\
    ,      Synapse
from bluepy.geometry.roi\
    import ROI as RegionOfInterest
from dmt.vtk.utils\
    import collections
from dmt.vtk.utils.collections\
    import *
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.measurement.parameter\
    import Parameter
from dmt.vtk.measurement.parameter.finite\
    import FiniteValuedParameter
from dmt.vtk.measurement.parameter.random\
    import ConditionedRandomVariate
from dmt.vtk.utils.logging\
    import Logger, with_logging
from dmt.vtk.utils.descriptor\
    import Field, WithFCA
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import BlueBrainCircuitModel
from neuro_dmt.utils.brain_regions\
    import BrainRegion
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.geometry\
    import  Cuboid,  random_location


@with_logging(Logger.level.STUDY)
class CircuitPropertyRandomVariate(
        ConditionedRandomVariate):
    """A random variate that returns values for a circuit property,
    such as it's cell's gids, or positions in the circuit's physical space.
    """
    circuit_model=\
        Field(
            __name__="circuit_model",
            __type__=BlueBrainCircuitModel,
            __doc__="Blue brain circuit model to compute random variates for.")
    def __init__(self,
            circuit_model,
            *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        """
        self.circuit_model\
            = circuit_model
        super().__init__(
            *args, **kwargs)

    def _with_region(self,
            cell_group,
            region):
        """Add region to cell group"""
        if region is not None:
            cell_group[self.circuit_model.region_label]=\
                region
        return cell_group


class RandomSpatialVariate(
        CircuitPropertyRandomVariate):
    """Generator of random values, for a (blue) brain circuit."""

    def __init__(self,
            circuit_model,
            *args, **kwargs):
        """Initialize Me
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        """
        super().__init__(
            circuit_model,
            reset_condition_type=True,
            *args, **kwargs)

    @property
    def circuit_geometry(self):
        """Provides circuit build geometry specific attribute
            specializations. Ideally we should be able to get this
            information from  'circuit'.
        """
        return self.circuit_model.geometry

class RandomPosition(
        RandomSpatialVariate):
    """Generate random positions in the circuit region."""
    label = "position"
    value_type = np.ndarray #dimension 3

    def __init__(self,
            circuit_model,
            offset=50.,
            *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        circuit_geometry :: type #<: CircuitGeometry
        """
        self.offset = offset
        super().__init__(
            circuit_model,
            columns=pd.Index(
                ["X", "Y", "Z"],
                name="axis"),
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """..."""
        self.logger.ignore(
            self.logger.get_source_info(),
            """generate RandomPosition with condition {}"""\
            .format(condition.value))
        return\
            self.circuit_geometry\
                .random_position(
                    condition,
                    *args, **kwargs)

    @property
    def sampling_method(self):
        """describe the method used to generate random positions."""
        return\
            "random positions generated in a circuit, for a given {}"\
            .format(
                ", ".join(self.condition_type.fields))

class RandomCrossectionalPoint(
        RandomPosition):
    """..."""
    def __init__(self,
            circuit_model,
            offset=50.,
            *args, **kwargs):
        """..."""
        super().__init__(
            circuit_model,
            offset=offset,
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """..."""
        return self.circuit_model\
                   .midplane_projection(
                       super().__call__(
                           condition,
                           *args, **kwargs) )


class RandomRegionOfInterest(
        RandomSpatialVariate):
    """Random regions of interest"""

    value_type = RegionOfInterest
    label = "region_of_interest"

    def __init__(self,
            circuit_model,
            sampled_box_shape=100.*np.ones(3),
            *args, **kwargs):
        """..."""
        self.sampled_box_shape = sampled_box_shape
        self.random_position\
            = RandomPosition(
                circuit_model,
                offset=sampled_box_shape/2.,
                *args, **kwargs)
        super().__init__(
            circuit_model,
            columns=[self.label],
            *args, **kwargs)

    def __call__(self,
            condition,
            sampled_box_shape=None,
            *args, **kwargs):
        """..."""
        half_box\
            = (sampled_box_shape if sampled_box_shape
               else self.sampled_box_shape / 2.)
        position\
            = self.random_position(
                condition,
                *args, **kwargs)
        if position is None:
            return None
        return Cuboid(
            position - half_box,
            position + half_box)
    
    @property
    def sampling_method(self):
        """describe the method used to generate random regions of interest"""
        self.logger.debug(
            self.logger.get_source_info(),
            """Describe sampling method for a random variate
            with condition fields: {}"""\
            .format(
                self.condition_type.fields))
        return\
            """Cuboids of shape {} were generated around a position
            sampled randomly inside a circuit for specified {}.
            """.format(
                " X ".join( str(x) for x in self.sampled_box_shape),
                ", ".join(self.condition_type.fields))


class RandomSpanningColumnOfInterest(
        RandomSpatialVariate):
    """A random column of interest is a random region of interest
    that spans the entire columnar dimension of the circuit.
    While well defined for O1 micro-circuits, we will have to be creative
    to define an equivalent definition for atlas based circuits."""

    value_type = RegionOfInterest
    label = "region_of_interest" 

    def __init__(self,
            circuit_model,
            crossection=50.,
            *args, **kwargs):
        """..."""
        self.__crossection\
            = crossection
        super().__init__(
            circuit_model,
            columns=[self.label],
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """Call Me"""
        return\
            self.circuit_model\
                .random_spanning_column(
                    condition,
                    crossection=self.__crossection)


class RandomBoxCorners(
        RandomSpatialVariate):
    """..."""
    value_type = tuple #length 2
    label = "box_corners"

    def __init__(self,
            circuit_model,
            sampled_box_shape=50.*np.ones(3),
            *args, **kwargs):
        """..."""
        self.random_region_of_interest\
            = RandomRegionOfInterest(
                circuit_model,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs)
        super().__init__(
            circuit_model,
            columns=pd.MultiIndex.from_tuples(
                [("lower_corner", "X"),
                 ("lower_corner", "Y"),
                 ("lower_corner", "Z"),
                 ("upper_corner", "X"),
                 ("upper_corner", "Y"),
                 ("upper_corner", "Z")],
                names=["box_corners", "axis"]),
            sampled_box_shape=sampled_box_shape,
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """"..."""
        region_of_interest=\
            self.random_region_of_interest(
                condition,
                *args, **kwargs)
        if region_of_interest is None:
            return None
        lower_corner, upper_corner=\
            region_of_interest.bbox
        return list(lower_corner) + list(upper_corner)


@with_logging(Logger.level.STUDY)
class RandomCellVariate(
        CircuitPropertyRandomVariate):
    """Generates random cell gids..."""
    value_type = int
    label = "gid"
    circuit_model=\
        Field(
            __name__="circuit_model",
            __type__=BlueBrainCircuitModel,
            __doc__="The circuit model in which to generate random cells.")

    def __init__(self,
            circuit_model,
            *args, **kwargs):
        """..."""

        self.__gid_cache__ = {}
        super().__init__(
            circuit_model=circuit_model,
            reset_condition_type=True,
            columns=["gid"],
            *args, **kwargs)

    @property
    def sampling_method(self):
        """..."""
        return\
            "random cell gids were sampled for given {}".format(
               ", ".join( self.condition_type.fields))

    def __get_cells(self,
            condition):
        """..."""
        if not condition.hash_id in self.__gid_cache__:
            self.__gid_cache__[condition.hash_id]=\
                self.circuit_model\
                    .cells.ids(
                        condition.as_dict)
        return\
            self.__gid_cache__[condition.hash_id]

    def sample_one(
            condition,
            size=20,
            *args, **kwargs):
        """Override"""
        cell_gids=\
            self.__get_cells(
                condition)
        if len(cell_gids) == 0:
            return None
        return\
            np.random.choice(
                cell_gids,
                size)

    def __call__(self,
            condition,
            *args, **kwargs):
        """...Call Me..."""
        return\
            self.sample_one(
                condition,
                *args, **kwargs)


class RandomPrePostPairs0(
        CircuitPropertyRandomVariate):
    """Generate random pairs of cell gids...,
    for a given pre-mtype --> post-mtype pathway.
    """
    label = "pre_post_pair"
    value_type = tuple

    def __init__(self,
            circuit_model,
            upper_bound_random_draws=1000000,
            binner=None,
            *args, **kwargs):
        """Initialize Me"""
        self.random_cell=\
            RandomCellVariate(
                circuit_model,
                *args, **kwargs)
        self._upper_bound_random_draws=\
            upper_bound_random_draws
        self.__distance_cache__=\
            {}
        self.__pair_cache__=\
            {}
        self._binner=\
            binner
        super().__init__(
            circuit_model,
            reset_condition_type=True,
            columns=["pre_gid", "post_gid"],
            *args, **kwargs)

    @property
    def sampling_method(self):
        """describe the method used to generate random positions."""
        return\
            "pairs of cell gids were sampled for given pre, post mtypes."\

    def __pair_by_distance(self,
            pre_cell_type,
            post_cell_type,
            distance_bin):
        """..."""
        if distance_bin not in self.__pair_cache__:
            self.__pair_cache__[distance_bin]=\
                []
        number_random_draws=\
            0
        while number_random_draws < self._upper_bound_random_draws:
            if self.__pair_cache__[distance_bin]:
                return self__pair_cache__.pop()
            pre_cell=\
                self.random_cell(
                    pre_cell_type)
            post_cell=\
                self.random_cell(
                    post_cell_type)
            number_random_draws+=\
                1
            soma_distance=\
                self._get_distance(
                    pre_cell,
                    post_cell)
            self.__pair_cache__[
                binnner.get_bin(
                    soma_distance)]=\
                (pre_cell, post_cell)
        return None

    def _get_distance(self,
            pre_cell,
            post_cell):
        """..."""
        if (pre_cell not in self._distance or
            post_cell not in self._distance[pre_cell]):
            postions=\
                self.circuit_model\
                    .cells\
                    .positions(
                        [pre_cell, post_cell])
            self._distance[pre_cell][post_cell]=\
                np.linalg.norm(
                    positions[0] - positions[1])
        return self._distance[pre_cell][post_cell]

    def __call__(self,
            condition,
            *args, **kwargs):
        """Call Me"""
        pre_mtype=\
            condition.get_value(
                "pre_mtype")
        post_mtype=\
            condition.get_value(
                "post_mtype")
        distance_interval=\
            condition.get_value(
                "soma_distance")
        if distance_interval:
            return\
                self.__pair_by_distance(
                    pre_mtype,
                    post_mtype,
                    distance_interval)
        
class RandomPrePostPairs(
        CircuitPropertyRandomVariate):
    """Generate random pairs of cell gids...,
    for a given pre-mtype --> post-mtype pathway.
    """
    def __init__(self,
            circuit_model,
            upper_bound_random_draws=1000000,
            cache_size=100,
            distance_bins=[(0., 500.)], #default bin
            *args, **kwargs):
        """..."""
        self.random_cell=\
            RandomCellVariate(
                circuit_model,
                *args, **kwargs)
        self._upper_bound_random_draws=\
            upper_bound_random_draws
        self.__cache_size__=\
            cache_size
        self.__distance__cache__=\
            {}
        self.__pair_cache__=\
            {}
        self._distance_bins=\
            distance_bins
        super().__init__(
            circuit_model,
            reset_condition_type=True,
            columns=["pre_gid", "post_gid"],
            *args, **kwargs)

    @property
    def sampling_method(self):
        """describe the method used to generate random positions."""
        return\
            "pairs of cell gids were sampled for given pre, post mtypes."\

    def __get_pairs(self,
            condition):
        """Lets assume that pairs have to generated by distance.
        """
        pre_mtype=\
            condition.get_value(
                "pre_mtype")
        post_mtype=\
            condition.get_value(
                "post_mtype")
        region=\
            condition.get_value(
                self.circuit_model.region_label)
        soma_distance=\
            condition.get_value(
                "soma_distance")
        if soma_distance not in self.__pair_cache__:
            self.__pair_cache__[soma_distance]=\
                {}
        if pre_mtype not in self.__pair_cache__[soma_distance]:
            self.__pair_cache__[soma_distance][pre_mtype]=\
                {}
        def __get_distances(
                pre_gid,
                post_gids):
            """..."""
            position_pre_gid=\
                self.circuit_model\
                    .cells\
                    .positions(
                        pre_gid)
            positions_post_gids=\
                self.circuit_model\
                    .cells\
                    .positions(
                        post_gids)
            delta_positions=\
                positions_post_gids - position_pre_gid
            return\
                positions_post_gids.apply(
                    np.linalg.norm,
                    axis=1
                ).values

        def __get_one_pre_gid(
                pre_gid):
            """..."""
            post_gids=\
                self.random_cell(
                    Condition([
                        ("mtype", pre_mtype),
                        (self.circuit_model.region_label, region)]),
                    size=self.__cache_size__)
            return\
                pd.DataFrame(
                    {"soma_distance": __get_distances(pre_gid, post_gids)},
                    index=pd.MultiIndex.from_tuples(
                        tuples=[(pre_gid, post_gid)
                                for post_gid in post_gids],
                        names=["pre_gid", "post_gid"]))

        if post_mtype not in self.__pair_cache__[soma_distance][pre_mtype]:
            pre_gids=\
                self.random_cell(
                    Condition([
                        ("mtype", pre_mtype),
                        (self.circuit_model.region_label, region)]),
                    size=self.__cache_size__)
            dataframe=\
                pd.concat([
                    __get_one_pre_gid(pre_gid)
                    for pre_gid in pre_gids])
            self.__pair_cache__[soma_distance][pre_mtype][post_mtype]=\
                pairs

    def sample_one(self,
            condition,
            size=20,
            *args, **kwargs):
        """Override"""
        self.logger.info(
            self.logger.get_source_info(),
            "Sample condition {}".format(condition.value))
        pairs=\
            self.__get_pairs(
                condition)
        number_pairs=\
            len(pairs)
        indexes_random=lambda:\
            np.random.randint(
                0, number_pairs, size)
        values=\
            pairs if number_pairs <= size\
            else pairs[indexes_random(), :]
        df_list=[
            self.row(condition, value)
            for value in values]
        if len(df_list) == 0:
            return\
                pd.DataFrame([], columns=self.columns)
        return pd.concat(df_list)





class RandomConnectionVariate(
        CircuitPropertyRandomVariate):
    """Generate random pair of connected cell gids...,
    given pre and post mtypes."""
    label = "connection"
    value_type = tuple

    def __init__(self,
            circuit_model,
            cache_size=1000,
            *args, **kwargs):
        """Initialize Me"""
        self._connections=\
            {}
        self.__cache_size__=\
            cache_size
        super().__init__(
            circuit_model,
            reset_condition_type=True,
            columns=["pre_gid", "post_gid"],
            *args, **kwargs)
        
    @property
    def sampling_method(self):
        """describe the method used to generate random positions."""
        return\
            "connected cell pairs were sampled for given pre, post mtypes."\

    def __get_connections(self,
            condition):
        """..."""
        pre_mtype=\
            condition.get_value(
                "pre_mtype")
        post_mtype=\
            condition.get_value(
                "post_mtype")
        region=\
            condition.get_value(
                self.circuit_model.region_label)
        self.logger.info(
            self.logger.get_source_info(),
            "Get connections from {} --> {} in region {} "\
            .format(
                pre_mtype,
                post_mtype,
                region))

        if not pre_mtype in self._connections:
            connections={}
            self.logger.info(
                self.logger.get_source_info(),
                "Get pre-synaptic cell gids ")
            pre_gids_all=\
                self.circuit_model\
                    .cells.ids(
                        self._with_region({
                            Cell.MTYPE: pre_mtype}))
            pre_gids=\
                np.random.choice(
                    pre_gids_all,
                    self.__cache_size__)\
                if len(pre_gids_all) >= self.__cache_size__\
                   else pre_gids_all
            self.logger.info(
                self.logger.get_source_info(),
                "Get connections for {} pre-gids of mtype {} in region {} "\
                .format(
                    len(pre_gids),
                    pre_mtype,
                    region if region is not None else "any"))
            for i, pre_gid in enumerate(pre_gids):
                post_gids=\
                    self.circuit_model\
                        .filter_region(
                            self.circuit_model\
                                .connectome\
                                .efferent_gids(
                                    pre_gid),
                            condition)
                self.logger.info(
                    self.logger.get_source_info(),
                    "For circuit at {}".format(
                        self.circuit_model.circuit_config),
                    "Get connections from {} --> {} in region {} ".format(
                        pre_mtype,
                        post_mtype,
                        region),
                    "{}-th pre_gid {} of total {}".format(
                        i, pre_gid, len(pre_gids)),
                    "Found {} post gids for {}".format(
                        len(post_gids),
                        pre_gid))
                post_gid_mtypes=\
                    self.circuit_model\
                        .cells.get(
                            post_gids,
                            properties=[Cell.MTYPE])
                post_mtype_gids=\
                    post_gid_mtypes.groupby(
                        Cell.MTYPE)
                for post_mtype, post_gids in post_mtype_gids.groups.items():
                    if post_mtype not in connections:
                        connections[post_mtype]=\
                            np.array([])
                    if len(post_gids) > 0:
                        random_post_gids=\
                            np.random.choice(
                                post_gids.values,
                                self.__cache_size__)
                        post_mtype_connections=\
                            np.array([
                                [pre_gid, post_gid]
                                for post_gid in random_post_gids])
                        connections[post_mtype]=\
                            np.vstack([
                                connections[post_mtype],
                                post_mtype_connections])\
                            if len(connections[post_mtype]) > 0\
                               else post_mtype_connections

            self._connections[pre_mtype]=\
                connections

        connections=\
            self._connections[pre_mtype][post_mtype]
        self.logger.info(
            self.logger.get_source_info(),
            """Found {} connections."""\
            .format(
                len(connections)))
        return connections

    def __call__(self,
            condition,
            *args, **kwargs):
        """Call Me"""
        raise NotImplementedError(
            """Need to think about sampling with or without replacement 
            for a random variate with a finite number of possible values.
            However, a method 'sample_one' is provided below.""")

    def sample_one(self,
            condition,
            size=20,
            *args, **kwargs):
        """Override"""
        self.logger.info(
            self.logger.get_source_info(),
            """Sample condition {}""".format(condition.value))
        # pre_mtype=\
        #     condition.get_value(
        #         "pre_mtype")
        # post_mtype=\
        #     condition.get_value(
        #         "post_mtype")
        # region=\
        #     condition.get_value(
        #         self.circuit_model.region_label)
        # pre_cell_type={
        #     Cell.MTYPE: pre_mtype,
        #     self.circuit_model.region_label: region}
        # post_cell_type={
        #     Cell.MTYPE: post_mtype,
        #     self.circuit_model.region_label: region}
        # connections=\
        #     list(self\
        #          .circuit_model\
        #          .connectome\
        #          .iter_connections(
        #              pre_cell_type,
        #              post_cell_type))
        # self.logger.info(
        #     self.logger.get_source_info(),
        #     """found {} connections."""\
        #     .format(len(connections)))
        connections=\
             self.__get_connections(
                 condition)
        number_connections=\
            len(connections)
        indexes_random=lambda:\
            np.random.randint(
                0, number_connections, size)
        values=\
            connections\
            if number_connections <= size else\
               connections[indexes_random(), :]
        df_list=[
            self.row(condition, value)
            for value in values]
        if len(df_list) == 0:
            return\
                pd.DataFrame([], columns=self.columns)
        return pd.concat(df_list)
            

class RandomPathwayConnectionVariate(
        CircuitPropertyRandomVariate):
    """Generate random pair of cell gids..."""
    label = "connection"
    value_type = tuple
    condition_type=\
        Record(mtype_pathway=tuple) #(int, int)

    def __init__(self,
            circuit_model,
            *args, **kwargs):
        """..."""
        self.random_pre_cell=\
            RandomCellVariate(
                circuit_model,
                *args, **kwargs)
        self.random_post_cell=\
            RandomCellVariate(
                circuit_model,
                *args, **kwargs)
        #self.__conn_cache__ = {}
        super().__init__(
            circuit_model=circuit_model,
            reset_condition_type=False,
            columns=["pre_gid", "post_gid"],
            *args, **kwargs)

    @property
    def sampling_method(self):
        """describe the method used to generate random positions."""
        return\
            "pairs of cell gids were sampled for given pre, post mtypes."\

    def __call__(self,
            condition,
            *args, **kwargs):
        """...Call Me..."""
        pathway=\
            condition.get_value(
                "mtype_pathway")
        return (
            self.random_pre_cell(
                Condition([
                    ("mtype", pathway[0])])),
            self.random_post_cell(
                 Condition([
                    ("mtype", pathway[1])])))


class RandomEfferentGid(
        CircuitPropertyRandomVariate):
    """Sample random gids from the set of gids efferent from a given
    group of cells."""
    pass
