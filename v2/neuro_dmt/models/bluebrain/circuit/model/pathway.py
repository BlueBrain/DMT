"""
Abstraction of a pathway and its properties.
"""
from abc import ABC, abstractmethod
from collections.abc import Mapping
from collections import OrderedDict
import functools
from enum import Enum
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
from .cell_type import CellType


logger = Logger(client=__file__)

class Pathway:
    """
    Organize what we mean by a pathway.
    """
    @staticmethod
    def _at(pos, cell_type):
        """
        Arguments
        ------------
        `pos`: pre/post
        `cell_type`: pandas.Series ...
        """
        assert pos in ("pre", "post"), pos
        return pd.DataFrame(
            cell_type.values,
            columns=pd.MultIndex.from_tuples(
                [(pos, value) for value in cell_types.columns]))


class Pathways(pd.Series):
    """
    Organize what we mean by a pathway.
    """
    def __init__(self, cell_type_specifier):
        """
        Pathways between cells specified by a tuple of
        cell properties.

        Arguments
        cell_type_specifier: a tuple of cell properties 
        """
        self._cell_type_specifier = cell_type_specifier


    def __repr_post__(self):
        """
        Represent `post` as a string
        """
        raise NotImplementedError


class SamplingMethodology(Enum):
    """
    How should cells be sampled for measuring pathway properties?
    """
    random = 1
    exhaustive = 2


class PathwayProperty(WithFields):
    """
    Compute and store a circuit's pathway properties.
    """
    phenomenon = Field(
        """
        A label to go with the pathway property.
        """)
    circuit_model = Field(
        """
        The circuit model for which this `PathwayProperty` has been defined.
        """)
    max_length_cell_type_specification = Field(
        """
        Max length of the cell type specifier that can be stored.
        """,
        __default_value__=2) 

    @lazyfield
    def store(self):
        """..."""
        return {}

    def _get_cell_types(self,
            cell_group,
            cell_type_specifier):
        """
        Get cell types.
        """
        if isinstance(cell_group, np.array):
            return self._get_cell_types(
                self.circuit_model.cells.loc[cell_group])

        return set([tuple(cell_type)
                    for cell_type in cell_group[cell_type_specifier]])

    def _resolve_cell_group(self,
            cell_group,
            cell_type_specifier,
            role_synaptic,
            sampling_methodology=SamplingMethodology.random,
            number=100):
        """

        Returns
        ---------
        pandas.DataFrame containing cells.
        """
        if isinstance(cell_group, np.array):
            gids = cell_group\
                if sampling_methodology != SamplingMethodology.random\
                   else np.random.choice(cell_group, number)
            return self._resolve_cell_group(
                self.circuit_model.cells.loc[gids],
                role_synaptic,
                resample=resample,
                sampling_methodology=sampling_methodology,
                number=number)
        if isinstance(cell_group, pd.Series):
            return self._resolve_cell_group(
                cell_group.to_dict(),
                role_synaptic,
                resample=resample,
                sampling_methodology=sampling_methodology,
                number=number)
        if isinstance(cell_group, Mapping):
            cells = self.circuit_model.get_cells(cell_group)
            return self._resolve_cell_group(
                cells.sample(number)\
                if sampling_methodology == Sampling_Methodology.random\
                else cells)

        if isinstance(cell_group, pd.DataFrame):
            return cell_group.rename(
                columns=lambda variable: "{}_{}".format(variable))

        raise NotImplementedError(
            """
            '_resolve_cell_group' not implemented for argument `cell_group`
            value {} of type {}.
            """.format(
                cell_group,
                type(cell_group)))

    @abstractmethod
    def get(self,
            pre_synaptic_cells,
            post_synaptic_cells):
        """
        Get the pathway property value.

        Arguments
        -------------
        pre_synaptic_cells : pandas.DataFrame containing cells on
                             pre-synaptic side.
        post_synaptic_cells : pandas.DataFrame containing cells on
                             post-synaptic side.
        """
        raise NotImplementedError

    def _get_key_to_cache_with(self,
            pre_synaptic_cell_specifier, pre_synaptic_cells,
            post_synaptic_cell_specifier, spost_synaptic_cells):
        """
        Check if pathway property value can be cached...
        """
        if pre_synaptic_cell_specifier is None:
            return None
        if post_synaptic_cell_specifier is None:
            return None
        pre_synaptic_cell_types =\
            self._get_cell_types(
                pre_synaptic_cells,
                pre_synaptic_cell_type_specifier)
        if len(pre_synaptic_cell_types) != 1:
            return None
        post_synaptic_cell_types =\
            self._get_cell_types(
                post_synaptic_cells,
                post_synaptic_cell_type_specifier)
        if len(post_synaptic_cell_types) != 1:
            return None

        return (
            pre_synaptic_cell_specifier,
            ppre_synaptic_cell_specifier)

    def _cached(self,
            pre_synaptic_cell_specifier, pre_synaptic_cells,
            post_synaptic_cell_specifier, post_synaptic_cells,
            by=None,
            resample=None,
            sampling_methodology=None,
            number=100):

        """
        Get pathway property value, with caching...

        Arguments
        ---------------
        ...
        """
        key_cache =\
            self._get_key_to_cache_with(
                pre_synaptic_cell_specifier, pre_synaptic_cells,
                post_synaptic_cell_specifier, post_synaptic_cells))
        if key_cache:
            if key_cache not in self.store:
                self.store[key_cache] =\
                    self.get_dataframe(
                        pre_synaptic_cell_specifier,
                        post_synaptic_cell_specifier)
            return self.store[key_cache]

        return self.get(pre_synaptic_cells, post_synaptic_cells)

    def _get_cell_type_specifier(cell):
        """

        Arguments
        --------------
        cell : pandas.Series containing cells...
        """
        if not isinstance(cell, pd.Series):
            return None
        if  cell.shape[0] > self.max_length_cell_type_specification:
            return None

        return cell.index.values


    def __call__(self,
            pre_synaptic_cell_group,
            post_synaptic_cell_group,
            by=None,
            given=None,
            resample=False,
            sampling_methodology=SamplingMethodology.random,
            number=100):
        """
        Compute, or retrieve from the store...

        Arguments
        -------------
        pre_synaptic_cell_group : Group of cells on the pre-synaptic side.
        post_synaptic_cell_group : Group of cells on the post-synaptic side.
        by : A property of a connection ((pre_synaptic_cell, post_synaptic_cell).
             Pathway property will be computed for given values of this variable.
             If a list of variables, the computation will be conditioned on all
             the variables.
        given: A dict providing variables and their values for which the
               the pathway property will be returned.
        """
        if by is not None:
            raise NotImplementedError(
                """
                Computation of {} pathway property by {}.
                """.format(
                    self.phenomenon,
                    by))
        if given is not None:
            raise NotImplementedError(
                """
                Computation of {} pathway property given {}.
                """.format(
                    self.phenomenon,
                    given))
        pre_synaptic_cell_type_specifier =\
            self._get_cell_type_specifier(
                pre_synaptic_cell_group)
        pre_synaptic_cells =\
            self._resolve_cell_group(
                pre_synaptic_cell_group,
                role_synaptic="pre_synaptic")
        post_synaptic_cell_type_specifier =\
            self._get_cell_type_specifier(
                post_synaptic_cell_group)
        post_synaptic_cells =\
            self._resolve_cell_group(
                post_synaptic_cell_group,
                role_synaptic="post_synaptic")

        return self._cached(
            pre_synaptic_cell_type_specifier, pre_synaptic_cells,
            post_synaptic_cell_type_specifier, post_synaptic_cells,
            by=by,
            resample=resample,
            sampling_methodology=sampling_methodology,
            number=100)


class ConnectionProbability(PathwayProperty):
    phenomenon = "connection_probability"

    def get(self,
            pre_synaptic_cell_specifier, pre_synaptic_cells,
            post_synaptic_cell_specifier, post_synaptic_cells):
        """
        Arguments
        ------------
        pre_synaptic_cells : pandas.DataFrame, with `pre_synaptic` in column names
        post_synaptic_cells : pandas.DataFrame, with 'post_synaptic' in column names

        Returns
        -----------
        pandas.DataFrame 
        """
        def _get_summary_pairs(post_gid):
            if pre_synaptic_cell_specifier is None:
                return pd.Series({
                    "number_pairs_total": pre_synaptic_cells.shape[0],
                    "number_pairs_connected": np.sum(np.in1d(
                        pre_synaptic_cells.index.values,
                        self.circuit_model.connectome.afferent_gids(post_gid))))})
            return pre_synaptic_cells\
                .assign(
                    number_pairs=np.in1d(
                        pre_synaptic_cells.gid.values,
                        post_gid))\
                .groupby(
                    pre_synaptic_cell_specifier)\
                .agg(
                    ["size", "sum"])\
                .rename(
                    columns={"size": "total", "sum": "connected"})\
                .reset_index()\
                .set_index(list(
                    pre_synaptic_cell_specifier
                    + post_synaptic_cell_specifier))

        def _connection_probability(summary):
            """
            Compute connection probability between pairs
            """
            return summary.number_pairs.connected / summary.number_pairs.total

        if post_synaptic_cell_specifier is None:
            if pre_synaptic_cell_specifier is None:
                return pd\
                    .DataFrame(
                        [_get_summary_pairs(post_gid)
                         for post_gid in post_synaptic_cells.gid.values])\
                    .apply(np.sum)\
                    .assign(
                        connection_probability=_connection_probability)
            return pd\
                .concat(
                    [_get_summary_pairs(post_gid)
                     for post_gid in post_synaptic_cells.gid.values],
                    axis=0)\
                .groupby(
                    pre_synaptic_cell_specifier)\
                .agg(
                    "sum")\
                .assign(
                    connection_probability=_connection_probability)

        if pre_synaptic_cell_specifier is None:
            return pd\
                .DataFrame(
                    [_get_summary_pairs(post_gid)
                     for post_gid in post_synaptic_cells.gid.values])\
                .groupby(
                    post_synaptic_cell_specifier)\
                .agg(
                    "sum")\
                .assign(
                    connection_probability=_connection_probability)
        return pd\
            .concat(
                [_get_summary_pairs(post_gid)
                 for post_gid in post_synaptic_cells.gid.values],
                axis=0)\
            .groupby(list(
                pre_synaptic_cell_specifier
                + post_synaptic_cell_specifier)\
            .agg(
                "sum")\
            .assign(
                connection_probability=_connection_probability)

def pathway_property(instance_method):
    """
    Decorate an `instance_method` as a PathwayProperty.

    Arguments
    -------------
    `instance_method`: Method of an class instance.

    Note
    --------------
    This has been kept for documentation purpose.
    For practical purposes, it's essence has been absorbed into
    `class PathwayPropert`.
    """
    instance_cache_attribute =\
        "_cache_{}".format(instance_method.__name__)

    @functools.wraps(instance_method)
    def effective(instance, pathway):
        """
        The effective method.

        Arguments
        -----------
        `instance`: Instance of the class where the member method
        has been defined.
        `pathway`: a pandas.Series like object that has attributes,
        `pre` and `post`.
        """
        if not hasattr(instance, instance_cache_attribute):
            setattr(
                instance,
                instance_cache_attribute,
                {})
        instance_cache =\
            getattr(instance, instance_cache_attribute)
        cell_type_specifier =\
            CellType(pathway.pre_synaptic).specifier
        assert\
            CellType(pathway.post_synaptic).specifier == cell_type_specifier,\
            """
            Post cell type:
            {}.
            """.format(
                ".\n".join(
                    "{}: {}".join(key, value)
                    for key, value in pathway.post_synaptic.items()))

        pre_cell_type = tuple(pathway.pre_synaptic.values)
        post_cell_type = tuple(pathway.post_synaptic.values)

        if cell_type_specifier not in instance_cache:
            instance_cache[cell_type_specifier] = {}
        
        cache = instance_cache[cell_type_specifier]
        if pre_cell_type not in cache:
            cache[pre_cell_type] = {}

        if post_cell_type not in cache[pre_cell_type]:
            cache[pre_cell_type][post_cell_type] =\
                instance_method(instance, pathway)

        return\
            instance_cache[
                cell_type_specifier][
                    pre_cell_type][
                        post_cell_type]

    return effective
