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
from dmt.vtk.measurement.parameter.spatial\
    import DistanceBinner
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

    def _random_choice(self,
            condition,
            size=None):
        """..."""
        if not condition.hash_id in self.__gid_cache__:
            self.__gid_cache__[condition.hash_id]=\
                self.circuit_model\
                    .cells.ids(
                        condition.as_dict)
        cell_gids=\
            self.__gid_cache__[
                condition.hash_id]
        if len(cell_gids) == 0:
            return np.array([]) if size else None
        return\
            np.random.choice(cell_gids, size)\
            if size else\
            np.random.choice(cell_gids)

    def __call__(self,
            condition,
            *args, **kwargs):
        """...Call Me..."""
        return\
            self._random_choice(
                condition,
                *args, **kwargs)


class RandomPrePostPairs(
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
                self._binner.get_bins(
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


class RandomPairs0(
        CircuitPropertyRandomVariate):
    """Generate random pairs of cell gids...,
    for a given pre-mtype --> post-mtype pathway.
    """
    label = "pre_post_pair"
    value_type = tuple

    def __init__(self,
            circuit_model,
            upper_bound_random_draws=1000000,
            cache_size=100,
            distance_binner=DistanceBinner(
                lower_bound=0.,
                upper_bound=10000.,#um large include all possible connections.
                number=1),
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
        self.__cache__=\
            {}
        self._distance_binner=\
            distance_binner
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

        def __get_distances(
                pre_gid,
                post_gids):
            """By distance, we mean the binned distance."""
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
            distances_raw=\
                delta_positions\
                .apply(
                    np.linalg.norm,
                    axis="columns")\
                .values
            return\
                self._distance_binner\
                    .get_bin_centers(
                        distances_raw)

        def __get_one_pre_gid(
                pre_gid):
            """..."""
            post_gids=\
                self.random_cell\
                    .sample_one(
                        Condition([
                            (Cell.MTYPE, post_mtype),
                            (self.circuit_model.region_label, region)]),
                        size=self.__cache_size__)
            soma_distances=\
                __get_distances(pre_gid, post_gids)
            self.logger.debug(
                self.logger.get_source_info(),
                """Soma distances from pre cell {}: \n{}"""\
                .format(
                    pre_gid,
                    pd.Series(soma_distances)\
                      .value_counts()\
                      .sort_index()))
            return\
                pd.DataFrame(
                    {"soma_distance": soma_distances},
                    index=pd.MultiIndex.from_tuples(
                        tuples=[(pre_gid, post_gid)
                                for post_gid in post_gids],
                        names=["pre_gid", "post_gid"]))

        if pre_mtype not in self.__cache__:
            self.__cache__[pre_mtype] = {}
        if post_mtype not in self.__cache__[pre_mtype]:
            pre_gids=\
                self.random_cell.sample_one(
                    Condition([
                        ("mtype", pre_mtype),
                        (self.circuit_model.region_label, region)]),
                    size=self.__cache_size__)
            soma_distance_dataframe=\
                pd.concat([
                    __get_one_pre_gid(pre_gid)
                    for pre_gid in pre_gids])
            self.__cache__[pre_mtype][post_mtype]=\
                soma_distance_dataframe\
                .groupby(
                    "soma_distance")\
                .groups
        pairs=\
            self.__cache__[pre_mtype][post_mtype][soma_distance].values\
            if soma_distance in self.__cache__[pre_mtype][post_mtype]\
               else np.array([])
        self.logger.info(
            self.logger.get_source_info(),
            "Found {} pairs".format(len(pairs)))
        return\
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
            else pairs[indexes_random()]
        df_list=[
            self.row(condition, value)
            for value in values]
        if len(df_list) == 0:
            return\
                pd.DataFrame([], columns=self.columns)
        return pd.concat(df_list)

    def __call__(self,
            condition,
            *args, **kwargs):
        """Call Me"""
        raise NotImplementedError(
            """Need to think about sampling with or without replacement 
            for a random variate with a finite number of possible values.
            However, a method 'sample_one' is provided below.""")

class RandomPairs(
        CircuitPropertyRandomVariate):
    """Generate random pairs of cell gids...,
    for a given pre-mtype --> post-mtype pathway.
    """

    label = "pre_post_pair"
    value_type = tuple

    def __init__(self,
            circuit_model,
            upper_bound_random_draws=1000000,
            cache_size=100,
            distance_binner=DistanceBinner(
                lower_bound=0.,
                upper_bound=10000.,#um large include all possible connections.
                number=1),
            *args, **kwargs):
        """..."""
        self.__XYZ=[
            Cell.X, Cell.Y, Cell.Z]
        self.random_cell=\
            RandomCellVariate(
                circuit_model,
                *args, **kwargs)
        self._upper_bound_random_draws=\
            upper_bound_random_draws
        self.__cache_size__=\
            cache_size
        self._distance_binner=\
            distance_binner
        self._empty_dataframe=\
            pd.DataFrame(
                [],
                columns=[
                    "pre_gid", "post_gid"],
                index=pd.MultiIndex.from_tuples(
                    [],
                    names=[
                        "region", "pre_mtype", "post_mtype", "soma_distance"]))
        self._sample_cells=\
            {}
        self._has_cells=\
            {}
        self._sample_pairs=\
            {}
        self._has_pairs=\
            {}
        super().__init__(
            circuit_model,
            reset_condition_type=True,
            columns=["pre_gid", "post_gid"],
            *args, **kwargs)

    @property
    def sampling_method(self):
        """describe the method usef to generate random pairs."""
        return(
            "Pairs of cell gids were sampled for given pre and post mtypes, "
            "in the specified region and soma distance bins.")

    def _read_condition(self,
            condition):
        """get pathway out of a condition.
        Data is held in this class as a dataframe,
        indexed by pathways.
        Arguments
        -----------
        condition :: Condition

        Return
        -----------
        Index tuple
        """
        region=\
            condition.get_value(
                self.circuit_model.region_label)
        if not region:
            region=\
                "Any"
        pre_mtype=\
            condition.get_value(
                "pre_mtype")
        if not pre_mtype:
            pre_mtype=\
                slice(None)
        post_mtype=\
            condition.get_value(
                "post_mtype")
        if not post_mtype:
            post_mtype=\
                slice(None)
        soma_distance=\
            condition.get_value(
                "soma_distance")
        if not soma_distance:
            soma_distance=\
                slice(None)
        return(
            region, pre_mtype, post_mtype, soma_distance)

    def _get_distances(self,
            origin,
            cells):
        """Distance of cells from origin."""
        return\
            self._distance_binner\
              .get_bins(
                  np.linalg.norm(
                      cells[self.__XYZ].values - origin,
                      axis=1))

    def __random_sample(self, cells):
        """..."""
        if cells.shape[0] < self.__cache_size__:
            return cells
        return\
            cells.sample(self.__cache_size__)

    def _get_cell_type(self,
            mtype,
            region):
        """..."""
        if region:
            return{
                Cell.MTYPE: mtype,
                self.circuit_model.region_label: region}
        return{
            Cell.MTYPE: mtype}

    def _get_cells(self,
            mtype,
            region=None):
        """..."""
        region_mtype=\
            (region, mtype) if region else mtype
        cell_type=\
            self._get_cell_type(
                mtype, region)
        if region_mtype not in self._sample_cells:
            self._sample_cells[region_mtype]=\
                self.__random_sample(
                    self.circuit_model\
                        .cells\
                        .get(
                            group=cell_type,
                            properties=self.__XYZ))
        return\
            self._sample_cells[
                region_mtype]

    def _get_pairs(self,
            condition):
        """..."""
        query=\
            self._read_condition(condition)
        region, pre_mtype, post_mtype, soma_distance=\
            query
        pathway=\
            (pre_mtype, post_mtype)
        self.logger.debug(
            self.logger.get_source_info(),
            """get pairs for pathway {} in region {}, at distance {}"""\
            .format(
                pathway,
                region,
                soma_distance))
        try:
            dataframe=\
                self._sample_pairs[pathway]
        except KeyError as key_error:
            # self.logger.debug(
            #     self.logger.get_source_info(),
            #     "Got key error {}".format(key_error),
            #     "Pathway {} will be cached.".format(condition.value))
            pre_cells=\
                self._get_cells(
                    pre_mtype,
                    region)
            if pre_cells.shape[0] == 0:
                self.logger.debug(
                    self.logger.get_source_info(),
                    "No gids for mtype {}".format(pre_mtype))
                self._sample_pairs[pathway]=\
                    self._empty_dataframe
                return self._empty_dataframe
            post_cells=\
                self._get_cells(
                    post_mtype,
                    region)
            if post_cells.shape[0] == 0:
                self.logger.debug(
                    self.logger.get_source_info(),
                    "No gids for mtype {}".format(post_mtype))
                self._sample_pairs[pathway]=\
                    self._empty_dataframe
                return self._empty_dataframe
            pairs=[
                [pre_gid, post_gid]
                for pre_gid in pre_cells.index.values
                for post_gid in post_cells.index.values]
            index=\
                pd.MultiIndex\
                  .from_tuples(
                      tuples=[
                          (region, pre_mtype, post_mtype, dis)
                          for origin in pre_cells[self.__XYZ].values
                          for dis in self._get_distances(origin, post_cells)],
                      names=[
                          "region","pre_mtype","post_mtype","soma_distance"])
            dataframe=\
                pd.DataFrame(
                    pairs,
                    columns=["pre_gid", "post_gid"],
                    index=index)
            # self.logger.debug(
            #     self.logger.get_source_info(),
            #     "will cache dataframe {}".format(dataframe))
            self._sample_pairs[pathway]=\
                dataframe
        if dataframe.empty:
            return dataframe
        try:
            query_dataframe=\
                dataframe.loc[query]
            return\
                dataframe\
                if isinstance(query_dataframe, pd.Series)\
                   else query_dataframe
        except KeyError as key_error:
            self.logger.alert(
                self.logger.get_source_info(),
                "no pairs for pathway {}".format(query))
        return\
            self._empty_dataframe

    def sample_one(self,
            condition,
            size=20,
            *args, **kwargs):
        """Override"""
        self.logger.info(
            self.logger.get_source_info(),
            "Sample condition {}.".format(condition.value))
        pairs=\
            self._get_pairs(
                condition)
        if pairs.shape[0] == 0:
            self.logger.alert(
                self.logger.get_source_info(),
                "no pairs found for pathway {}".format(
                    condition.value))
            return self._empty_dataframe
        # self.logger.debug(
        #     self.logger.get_source_info(),
        #     "found {} pairs for pathway".format(
        #         pairs.shape,
        #         condition.value))
        return\
            pairs.sample(size, replace=False)\
            if pairs.shape[0] > size\
               else pairs

    def __call__(self,
            condition,
            *args, **kwargs):
        """Call Me"""
        raise NotImplementedError(
            """Need to think about sampling with or without replacement 
            for a random variate with a finite number of possible values.
            However, a method 'sample_one' is provided below.""")

class RandomConnectionVariate(
        CircuitPropertyRandomVariate):
    """Generate random pair of connected cell gids...,
    given pre and post mtypes."""
    label = "connection"
    value_type = tuple

    def __init__(self,
            circuit_model,
            cache_size=None,
            *args, **kwargs):
        """Initialize Me"""
        self.__cache__=\
            pd.DataFrame(
                [],
                columns=["pre_gid", "post_gid"])
        self.__cache_size__=\
            cache_size
        self._empty_dataframe=\
            pd.DataFrame(
                [],
                columns=["pre_gid", "post_gid"],
                index=pd.MultiIndex.from_tuples(
                    tuples=[],
                    names=["pre_mtype", "post_mtype"]))
        self.__pathways_without_connections=\
            set()
        self.__pre_mtypes_cached=\
            set()
        super().__init__(
            circuit_model,
            reset_condition_type=True,
            columns=["region", "pre_gid", "post_gid"],
            *args, **kwargs)

    @property
    def sampling_method(self):
        """describe the method used to generate random positions."""
        return\
            "connected cell pairs were sampled for given pre, post mtypes."\

    def __random_sample(self,
            gids):
        """..."""
        if len(gids) == 0:
            return np.array([])
        if not self.__cache_size__:
            return gids
        self.logger.debug(
            self.logger.get_source_info(),
            "sample {} gids out of {}"\
            .format(
                self.__cache_size__,
                len(gids)))
        return\
            np.random.choice(
                gids,
                self.__cache_size__)

    def __random_post_gids(self,
            pre_gid):
        """..."""
        return\
            self.__random_sample(
                self.circuit_model\
                    .connectome\
                    .efferent_gids(
                        pre_gid))

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
            "RandomConnectionVariate instance {}".format(self),
            "Get connections from {} --> {} in region {} "\
            .format(
                pre_mtype,
                post_mtype,
                region))
        pathway=\
            (pre_mtype, post_mtype)
        if pathway in self.__pathways_without_connections:
            self.logger.debug(
                self.logger.get_source_info(),
                "pathway {} is without connections".format(pathway))
            return self._empty_dataframe
        def __get_cell_type(mtype):
            if region:
                return{
                    Cell.MTYPE: mtype,
                    Cell.REGION: region}
            return{
                Cell.MTYPE: mtype}
        if pre_mtype not in self.__pre_mtypes_cached:
            pre_gids=\
                self.__random_sample(
                    self.circuit_model.cells.ids(
                        __get_cell_type(
                            pre_mtype)))
            if len(pre_gids) == 0:
                self.logger.debug(
                    self.logger.get_source_info(),
                    "No pre gids for {}".format(pre_mtype))
                return self._empty_dataframe
            def __get_post_gids(gid):
                return\
                    self.__random_sample(
                        self.circuit_model\
                            .connectome\
                            .efferent_gids(gid))
            pre_post_pairs=[
                [pre_gid, post_gid]
                for pre_gid in pre_gids
                for post_gid in __get_post_gids(pre_gid)]
            number_connections=\
                len(pre_post_pairs)
            if number_connections == 0:
                self.__pathways_without_connections\
                    .add(pathway)
                return self._empty_dataframe
            self.logger.info(
                self.logger.get_source_info(),
                "Number of efferent connections for {}: {}"\
                .format(
                    pre_mtype,
                    number_connections))
            dataframe=\
                pd.DataFrame(
                    np.vstack(pre_post_pairs).astype(int),
                    columns=["pre_gid", "post_gid"])
            dataframe_with_index=\
                dataframe.set_index(
                    pd.MultiIndex.from_tuples(
                        tuples=[(region, pre_mtype, mtype)
                                for mtype in self.circuit_model.cells.get(
                                        dataframe["post_gid"].values,
                                        Cell.MTYPE)],
                        names=["region", "pre_mtype", "post_mtype"]))
            self.logger.debug(
                self.logger.get_source_info(),
                "dataframe computed for pre mtype {}".format(pre_mtype),
                "{}".format(dataframe_with_index.head()))
            if self.__cache__.empty:
                self.__cache__=\
                    dataframe_with_index
            else:
                self.__cache__=\
                    pd.concat([
                        self.__cache__,
                        dataframe_with_index])
            self.__pre_mtypes_cached.add(pre_mtype)
        try:
            return\
                self.__cache__\
                    .loc[
                        (region, pre_mtype, post_mtype)]
        except KeyError:
            return self._empty_dataframe

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
            """Sample condition {}"""\
            .format(condition.value))
        connections=\
            self.__get_connections(
                condition)
        if connections.shape[0] == 0:
            self.logger.debug(
                self.logger.get_source_info(),
                "no connections found for condition".format(
                    condition.value))
            return self._empty_dataframe
        self.logger.debug(
            self.logger.get_source_info(),
            "found {} connections for condition".format(
                connections.shape,
                condition.value))
        return connections.sample(size, replace=True)
            

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
