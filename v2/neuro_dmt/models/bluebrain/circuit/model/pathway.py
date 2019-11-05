"""
Abstraction of a pathway and its properties.
"""
from abc import ABC, abstractmethod
from collections.abc import Mapping
from collections import OrderedDict, namedtuple
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
    max_length_cell_type_specifier = Field(
        """
        Max length of the cell type specifier that can be stored.
        """,
        __default_value__=2)
    memoize = Field(
        """
        Set to true if measured values should be cached, when possible to do so.
        """,
        __default_value__=True)

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
            cell_type=None,
            sampling_methodology=SamplingMethodology.random,
            resample=False,
            number=100):
        """

        Returns
        ---------
        pandas.DataFrame containing cells.
        """
        # if cell_group is None:
        #     assert cell_type, cell_type
        #     cell_group = 
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
            cells = self.circuit_model.cells if self.memoize\
                else self.circuit_model.get_cells(**cell_group)
            return self._resolve_cell_group(
                cells,
                sampling_methodology=sampling_methodology,
                resample=False,
                number=number)

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
            pre_synaptic_cell_type_specifier, pre_synaptic_cells,
            post_synaptic_cell_type_specifier, post_synaptic_cells):
        """
        Check if pathway property value can be cached...
        """
        if not pre_synaptic_cell_type_specifier:
            return None
        if not post_synaptic_cell_type_specifier:
            return None
        # pre_synaptic_cell_types =\
        #     self._get_cell_types(
        #         pre_synaptic_cells,
        #         pre_synaptic_cell_type_specifier)
        # if len(pre_synaptic_cell_types) != 1:
        #     return None
        # post_synaptic_cell_types =\
        #     self._get_cell_types(
        #         post_synaptic_cells,
        #         post_synaptic_cell_type_specifier)
        # if len(post_synaptic_cell_types) != 1:
        #     return None

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
        Cache when possible.

        Arguments
        ---------------
        ...
        """
        key_cache =\
            self._get_key_to_cache_with(
                pre_synaptic_cell_type_specifier, pre_synaptic_cells,
                post_synaptic_cell_type_specifier, post_synaptic_cells)

        measurement_values = self.get(
            pre_synaptic_cells.rename(
                columns=self._at("pre_synaptic")),
            post_synaptic_cells.rename(
                columns=self._at("post_synaptic")))

        if key_cache:
            if (key_cache not in self.store
                or (sampling_methodology == SamplingMethodology.random
                    and resample)):
                pre_synaptic_columns =[
                    "pre_synaptic_{}".format(variable)
                    for variable in pre_synaptic_cell_type_specifier]
                post_synaptic_columns =[
                    "post_synaptic_{}".format(variable)
                    for variable in post_synaptic_cell_type_specifier]
                measurement = pd\
                    .concat([
                        pairs[self.measurement_variables
                              + pre_synaptic_columns
                              + post_synaptic_columns]\
                        .groupby(
                            pre_synaptic_columns
                            + post_synaptic_columns)\
                        .agg(
                            self.aggregators)\
                        .rename(
                            columns=self.columns)
                        for pairs in measurement_values])\
                    .groupby(
                            pre_synaptic_columns
                            + post_synaptic_columns)\
                    .agg("sum")\
                    .assign(**{
                        self.phenomenon: self.definition})
                self.store[key_cache] = measurement
            return self.store[key_cache]

        return pd\
            .concat([
                pairs[self.measurement_variables].agg(self.aggregators).transpose()
                for pairs in measurement_values])\
            .reset_index(drop=True)\
            .rename(columns=self.columns)\
            .agg("sum")
                

    def _get_cell_type_specifier(self, cell):
        """
        Get cell type specifier for a `cell`,
        but only if the specifier is less than a maximum allowed length.
        This specifier will be used as part of a key to cache pathway property
        values.

        Arguments
        --------------
        cell : pandas.Series containing cells...

        Returns
        ---------------
        tuple
        """
        try:
            cell_type = CellType(value=cell)
            return cell_type.specifier\
                if len(cell_type.value) <= self.max_length_cell_type_specifier\
                   else tuple()
        except TypeError:
            pass
        return tuple()

    GroupByVariables = namedtuple(
        "GroupByVariables",
        ["pre_synaptic_cell_type",
         "post_synaptic_cell_type"])

    def __call__(self,
            pre_synaptic_cell_group=None,
            post_synaptic_cell_group=None,
            groupby=GroupByVariables(
                pre_synaptic_cell_type=None,
                post_synaptic_cell_type=None),
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
        if pre_synaptic_cell_group is None:
            assert groupby.pre_synaptic_cell_type
        pre_synaptic_cell_type_specifier =\
            groupby.pre_synaptic_cell_type\
            if groupby.pre_synaptic_cell_type else\
               self._get_cell_type_specifier(pre_synaptic_cell_group)
        print("pre_synaptic_cell_type_specifier", pre_synaptic_cell_type_specifier)
        pre_synaptic_cells =\
            self._resolve_cell_group(
                pre_synaptic_cell_group,
                sampling_methodology=sampling_methodology,
                resample=resample,
                number=number)
                   
        if post_synaptic_cell_group is None:
            assert groupby.post_synaptic_cell_type
        post_synaptic_cell_type_specifier =\
            groupby.post_synaptic_cell_type\
            if groupby.post_synaptic_cell_type else\
               self._get_cell_type_specifier(post_synaptic_cell_group)
        print("post_synaptic_cell_type_specifier", post_synaptic_cell_type_specifier)
        post_synaptic_cells =\
            self._resolve_cell_group(
                post_synaptic_cell_group,
                sampling_methodology=sampling_methodology,
                resample=resample,
                number=number)

        return self._cached(
            pre_synaptic_cell_type_specifier, pre_synaptic_cells,
            post_synaptic_cell_type_specifier, post_synaptic_cells,
            by=by,
            resample=resample,
            sampling_methodology=sampling_methodology,
            number=100)


class ConnectionProbability(PathwayProperty):
    phenomenon = "connection_probability"
    aggregators = ["size", "sum"]
    measurement_variables = ["pairs"]
    columns = {"size": "total", "sum": "connected"}

    @staticmethod
    def definition(summary_measurement):
        return summary_measurement.pairs.connected / summary_measurement.pairs.total

    def get(self,
            pre_synaptic_cells,
            post_synaptic_cells,
            *args, **kwargs):
        """

        Arguments
        --------------
        pre_synaptic_cells : pandas.DataFrame
        post_synaptic_cells : pandas.DataFrame
        *args, **kwargs : Accommodate super's call to `get`.

        Returns
        --------------
        A generator of data-frames that provides values for individual
        pairs `(pre_synaptic_cell, post_synaptic_cell)`.
        """
        for _, post_cell in post_synaptic_cells.iterrows():
            pairs = pre_synaptic_cells\
                .drop(
                    columns="gid"
                ).reset_index(
                    drop=True
                ).assign(
                    pairs=np.in1d(
                        pre_synaptic_cells.gid.values,
                        self.circuit_model.connectome.afferent_gids(post_cell.gid)))
            post_cell_info = pd.DataFrame(
                pre_synaptic_cells.shape[0] * [post_cell.drop("gid")]
            ).reset_index(
                drop=True)
            yield pd.concat(
                [pairs, post_cell_info],
                axis=1)

            


    # def get(self,
    #         pre_synaptic_cell_type_specifier, pre_synaptic_cells,
    #         post_synaptic_cell_type_specifier, post_synaptic_cells):
    #     """
    #     Arguments
    #     ------------
    #     pre_synaptic_cells : pandas.DataFrame, with `pre_synaptic` in column names
    #     post_synaptic_cells : pandas.DataFrame, with 'post_synaptic' in column names

    #     Returns
    #     -----------
    #     pandas.DataFrame 
    #     """
    #     def _get_summary_pairs(post_cell):
    #         if not pre_synaptic_cell_type_specifier:
    #             return pd.Series({
    #                 ("number_pairs", "total"): pre_synaptic_cells.shape[0],
    #                 ("number_pairs", "connected"): np.sum(np.in1d(
    #                     pre_synaptic_cells.gid.values,
    #                     self.circuit_model.connectome.afferent_gids(post_cell.gid)))})
    #         return pre_synaptic_cells[
    #                 list(pre_synaptic_cell_type_specifier)
    #             ].assign(
    #                 number_pairs=np.in1d(
    #                     pre_synaptic_cells.gid.values,
    #                     self.circuit_model.connectome.afferent_gids(post_cell.gid))
    #             ).groupby(
    #                 pre_synaptic_cell_type_specifier
    #             ).agg(
    #                 ["size", "sum"]
    #             ).rename(
    #                 columns={"size": "total", "sum": "connected"}
    #             ).assign(**{
    #                 p: post_cell[p]
    #                 for p in post_synaptic_cell_type_specifier
    #                 if p != "gid"}
    #             ).reset_index(
    #             ).set_index(list(
    #                 pre_synaptic_cell_type_specifier
    #                 + post_synaptic_cell_type_specifier))

    #     def _value(summary):
    #         """
    #         Compute connection probability between pairs
    #         """
    #         return summary.number_pairs.connected / summary.number_pairs.total

    #     if not post_synaptic_cell_type_specifier:
    #         if not pre_synaptic_cell_type_specifier:
    #             pairs = pd\
    #                 .DataFrame(
    #                     [_get_summary_pairs(post_cell)
    #                      for _, post_cell in post_synaptic_cells.iterrows()])\
    #                 .apply(np.sum)
    #             return pairs.append(pd.Series({
    #                 "connection_probability": _value(pairs)}))
    #         return pd\
    #             .concat(
    #                 [_get_summary_pairs(post_cell)
    #                  for _, post_cell in post_synaptic_cells.iterrows()],
    #                 axis=0)\
    #             .groupby(
    #                 pre_synaptic_cell_type_specifier)\
    #             .agg(
    #                 "sum")\
    #             .reset_index()\
    #             .assign(
    #                 connection_probability=_value)

    #     if not pre_synaptic_cell_type_specifier:
    #         return pd\
    #             .DataFrame(
    #                 [_get_summary_pairs(post_cell)
    #                  for _, post_cell in post_synaptic_cells.iterrows()])\
    #             .groupby(
    #                 post_synaptic_cell_type_specifier)\
    #             .agg(
    #                 "sum")\
    #             .assign(
    #                 connection_probability=_value)
    #     return pd\
    #         .concat(
    #             [_get_summary_pairs(post_cell)
    #              for _, post_cell in post_synaptic_cells.iterrows()],
    #             axis=0)\
    #         .groupby(list(
    #             pre_synaptic_cell_type_specifier
    #             + post_synaptic_cell_type_specifier))\
    #         .agg(
    #             "sum")\
    #         .assign(
    #             connection_probability=_value)

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
