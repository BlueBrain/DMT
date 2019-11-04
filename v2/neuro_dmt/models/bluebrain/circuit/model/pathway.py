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
        if isinstance(cell_group, np.ndarray):
            return self._get_cell_types(
                self.circuit_model.cells.loc[cell_group])

        return set([tuple(cell_type)
                    for cell_type in cell_group[list(
                            cell_type_specifier
                    )].values])

    def _resolve_cell_group(self,
            cell_group,
            sampling_methodology=SamplingMethodology.random,
            resample=False,
            number=100):
        """

        Returns
        ---------
        pandas.DataFrame containing cells.
        """
        if isinstance(cell_group, np.ndarray):
            gids = cell_group\
                if (sampling_methodology != SamplingMethodology.random
                    or len(cell_group) < number
                ) else np.random.choice(cell_group, number)
            return self._resolve_cell_group(
                self.circuit_model.cells.loc[gids],
                resample=resample,
                sampling_methodology=sampling_methodology,
                number=number)
        if isinstance(cell_group, pd.Series):
            return self._resolve_cell_group(
                cell_group.to_dict(),
                resample=resample,
                sampling_methodology=sampling_methodology,
                number=number)
        if isinstance(cell_group, Mapping):
            return self._resolve_cell_group(
                self.circuit_model.get_cells(cell_group),
                sampling_methodology=sampling_methodology,
                resample=False,
                number=100)

        if isinstance(cell_group, pd.DataFrame):
            return cell_group\
                if (sampling_methodology != SamplingMethodology.random
                    or cell_group.shape[0] < number
                ) else cell_group.sample(n=number)
                    
        raise NotImplementedError(
            """
            '_resolve_cell_group' not implemented for argument `cell_group`
            value {} of type {}.
            """.format(
                cell_group,
                type(cell_group)))

    @staticmethod
    def _at(role_synaptic):
        """..."""
        def _rename_column(variable):
            return variable if variable == "gid"\
                else  "{}_{}".format(role_synaptic, variable)
        return _rename_column

    @abstractmethod
    def get(self,
            pre_synaptic_cell_type_specifier,
            pre_synaptic_cells,
            post_synaptic_cell_type_specifier,
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
            pre_synaptic_cell_type_specifier, pre_synaptic_cells,
            post_synaptic_cell_type_specifier, post_synaptic_cells):
        """
        Check if pathway property value can be cached...
        """
        if not pre_synaptic_cell_type_specifier:
            return None
        if not post_synaptic_cell_type_specifier:
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
            pre_synaptic_cell_type_specifier,
            post_synaptic_cell_type_specifier)

    def _cached(self,
            pre_synaptic_cell_type_specifier, pre_synaptic_cells,
            post_synaptic_cell_type_specifier, post_synaptic_cells,
            by=None,
            resample=False,
            sampling_methodology=SamplingMethodology.random,
            number=100):

        """
        Get pathway property value, with caching...

        Arguments
        ---------------
        ...
        """
        key_cache =\
            self._get_key_to_cache_with(
                pre_synaptic_cell_type_specifier, pre_synaptic_cells,
                post_synaptic_cell_type_specifier, post_synaptic_cells)

        def _value():
            return self.get(
                tuple(self._at("pre_synaptic")(variable)
                      for variable in pre_synaptic_cell_type_specifier),
                pre_synaptic_cells.rename(
                    columns=self._at("pre_synaptic")),
                tuple(self._at("post_synaptic")(variable)
                      for variable in post_synaptic_cell_type_specifier),
                post_synaptic_cells.rename(
                    columns=self._at("post_synaptic")))

        if key_cache:
            if (key_cache not in self.store
                or (sampling_methodology == SamplingMethodology.random
                    and resample)):
                self.store[key_cache] = _value()
            return self.store[key_cache]

        return _value()

    def _get_cell_type_specifier(self, cell):
        """

        Arguments
        --------------
        cell : pandas.Series containing cells...
        """
        if not isinstance(cell, pd.Series):
            return tuple()
        if  cell.shape[0] > self.max_length_cell_type_specification:
            return tuple()

        return CellType(value=cell).specifier

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
                pre_synaptic_cell_group)
        post_synaptic_cell_type_specifier =\
            self._get_cell_type_specifier(
                post_synaptic_cell_group)
        post_synaptic_cells =\
            self._resolve_cell_group(
                post_synaptic_cell_group)

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
            pre_synaptic_cell_type_specifier, pre_synaptic_cells,
            post_synaptic_cell_type_specifier, post_synaptic_cells):
        """
        Arguments
        ------------
        pre_synaptic_cells : pandas.DataFrame, with `pre_synaptic` in column names
        post_synaptic_cells : pandas.DataFrame, with 'post_synaptic' in column names

        Returns
        -----------
        pandas.DataFrame 
        """
        def _get_summary_pairs(post_cell):
            if not pre_synaptic_cell_type_specifier:
                return pd.Series({
                    ("number_pairs", "total"): pre_synaptic_cells.shape[0],
                    ("number_pairs", "connected"): np.sum(np.in1d(
                        pre_synaptic_cells.gid.values,
                        self.circuit_model.connectome.afferent_gids(post_cell.gid)))})
            return pre_synaptic_cells[list(pre_synaptic_cell_type_specifier)]\
                .assign(
                    number_pairs=np.in1d(
                        pre_synaptic_cells.gid.values,
                        post_cell.gid))\
                .groupby(
                    pre_synaptic_cell_type_specifier)\
                .agg(
                    ["size", "sum"])\
                .rename(
                    columns={"size": "total", "sum": "connected"})\
                .assign(**{
                    p: post_cell[p]
                    for p in post_synaptic_cell_type_specifier
                    if p != "gid"})\
                .reset_index()\
                .set_index(list(
                    pre_synaptic_cell_type_specifier
                    + post_synaptic_cell_type_specifier))

        def _value(summary):
            """
            Compute connection probability between pairs
            """
            return summary.number_pairs.connected / summary.number_pairs.total

        if not post_synaptic_cell_type_specifier:
            if not pre_synaptic_cell_type_specifier:
                pairs = pd\
                    .DataFrame(
                        [_get_summary_pairs(post_cell)
                         for _, post_cell in post_synaptic_cells.iterrows()])\
                    .apply(np.sum)
                return pairs.append(pd.Series({
                    "connection_probability": _value(pairs)}))
            return pd\
                .concat(
                    [_get_summary_pairs(post_cell)
                     for _, post_cell in post_synaptic_cells.iterrows()],
                    axis=0)\
                .groupby(
                    pre_synaptic_cell_type_specifier)\
                .agg(
                    "sum")\
                .reset_index()\
                .assign(
                    connection_probability=_value)

        if not pre_synaptic_cell_type_specifier:
            return pd\
                .DataFrame(
                    [_get_summary_pairs(post_cell)
                     for _, post_cell in post_synaptic_cells.iterrows()])\
                .groupby(
                    post_synaptic_cell_type_specifier)\
                .agg(
                    "sum")\
                .assign(
                    connection_probability=_value)
        return pd\
            .concat(
                [_get_summary_pairs(post_cell)
                 for _, post_cell in post_synaptic_cells.iterrows()],
                axis=0)\
            .groupby(list(
                pre_synaptic_cell_type_specifier
                + post_synaptic_cell_type_specifier))\
            .agg(
                "sum")\
            .assign(
                connection_probability=_value)

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
