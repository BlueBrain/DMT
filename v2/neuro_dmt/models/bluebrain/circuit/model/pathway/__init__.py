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
from neuro_dmt import terminology
from ..cell_type import CellType


logger = Logger(client=__file__)

class Pathway:
    """
    Organize what we mean by a pathway.
    """
    @staticmethod
    def pre_fixed(role_synaptic):
        def _renamed(variable):
            return variable if variable == "gid"\
                else "{}_{}".format(role_synaptic, variable)
        return _renamed

    @staticmethod
    def _as(cell_group, role_synaptic):
        """
        Arguments
        ------------
        `pos`: pre/post
        """
        if isinstance(cell_group, pd.DataFrame):
            return cell_group.rename(
                columns=Pathway.pre_fixed(role_synaptic))
        raise NotImplementedError(
            """
            for `cell_group` type
            """.format(
                type(cell_group)))

    @staticmethod
    def as_pre_synaptic(cell_group):
        return Pathway._as(cell_group, "pre_synaptic")

    @staticmethod
    def as_post_synaptic(cell_group):
        return Pathway._as(cell_group, "post_synaptic")


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

    
class ConnectomeSummary(WithFields):
    """
    Define a connectome summary.
    """
    value = Field(
        """
        A `pandas.Series` containing keys that fully define a connectome
        summary.
        Required variables
        -----------------------
        1. variables that define the pre-synaptic cell type.
        2. variables that define the post-synaptic cell type.
        2. `number_cells_pre_synaptic`
        """)

    @lazyfield
    def pre_synaptic_cell_type_specifier(self):
        """
        Set of cell properties that specify the cell type on the pre-synaptic
        side.
        """
        return{
            variable
            for variable in summary.index.names
            if variable.startswith("pre_synaptic")}

    @lazyfield
    def post_synaptic_cell_type_specifier(self):
        """
        Set of cell properties that specify the cell type on the post-synaptic
        side.
        """
        return{
            variable
            for variable in summary.index.names
            if variable.startswith("post_synaptic")}
    
    @lazyfield
    def number_cells_pre_synaptic(self):
        """
        Number of cells on the pre-synaptic side of the pathway.
        """
        return self.value.number_cells_pre_synaptic

    @lazyfield
    def number_cells_post_synaptic(self):
        """
        Number of cells on the post-synaptic side of the pathway.
        """
        return self.value.number_cells_post_synaptic

    @lazyfield
    def number_pairs_connected(self):
        """
        Number of pairs in the pathway that are connected,
        """
        return self.value.number_pairs_connected

    @lazyfield
    def number_pairs_total(self):
        """
        Total number of `(pre_synaptic_cell, post_synaptic_cell)` pairs in the
        pathway used to make this statistical summary.
        """
        return self.number_cells_pre_synaptic * self.number_cells_post_synaptic

    @lazyfield
    def probability_connection(self):
        """
        Probability that any cell in the pre-synaptic group is connected to any
        cell in the post-synaptic group.
        """
        return self.number_pairs_connected / self.number_pairs_total

    @lazyfield
    def number_connections_afferent(self):
        """
        The number of pre-synaptic cells that a randomly sampled post-synaptic
        cell in connected to in a given pathway.
        """
        return\
            self.number_pairs_connected / self.number_cells_post_synaptic

    @lazyfield
    def number_connections_efferent(self):
        """
        The number of post-synaptic cells that a randomly sampled pre-synaptic
        cell is connected to in a given pathway.
        """
        return\
            self.number_pairs_connected / self.number_cells_pre_synaptic

    def __init__(self, summary):
        """
        Initialize from a pandas.Series, assuming that it contains all the
        required keys.

        Arguments
        ----------
        `summary` : A pandas.Series or a mapping that will be converted to one.
        """
        super().__init__(value=summary)
            
    @lazyfield
    def pandas_series(self):
        """..."""
        return pd.Series(dict(
            number_cells_pre_synaptic = self.number_cells_pre_synaptic,
            number_cells_post_synaptic = self.number_cells_post_synaptic,
            number_pairs_total = self.number_pairs_total,
            number_pairs_connected=self.number_pairs_connected,
            probability_connection=self.probability_connection,
            number_connections_afferent=self.number_connections_afferent,
            number_connections_efferent=self.number_connections_efferent))


def connectome_summary(
        summary_with_numbers,
        type_summary=pd.Series):
    """
    Get a connectome summary,
    as a `pandas.Series` by default.

    Arugments
    -------------
    summary_with_numbers : pandas.Series
    """
    summary =\
        ConnectomeSummary(
            summary_with_numbers)
    return summary.pandas_series\
        if type_summary==pd.Series\
           else summary


GroupByVariables = namedtuple(
    "GroupByVariables",
    ["pre_synaptic_cell_type_specifier",
     "post_synaptic_cell_type_specifier"])


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
            sampling_methodology=terminology.sampling_methodology.random,
            resample=False,
            number=100):
        """

        Returns
        ---------
        pandas.DataFrame containing cells.
        """
        other_args = dict(
            sampling_methodology=sampling_methodology,
            resample=resample,
            number=number)
        logger.study(
            logger.get_source_info(),
            """
            resolve cell group {}
            given that {}
            """.format(
                cell_group,
                other_args))
        if cell_group is None:
            return self._resolve_cell_group(
                self.circuit_model.cells,
                **other_args)
        if isinstance(cell_group, np.ndarray):
            return self._resolve_cell_group(
                self.circuit_model.cells.loc[cell_group],
                **other_args)
        if isinstance(cell_group, pd.Series):
            return self._resolve_cell_group(
                cell_group.to_dict(),
                **other_args)
        if isinstance(cell_group, Mapping):
            return self._resolve_cell_group(
                self.circuit_model.get_cells(**cell_group))

        if isinstance(cell_group, pd.DataFrame):
            result = cell_group\
                if (sampling_methodology!=terminology.sampling_methodology.random
                    or cell_group.shape[1] > number - 1
                ) else (
                    cell_group.sample(n=number)\
                    if number < cell_group.shape[0]\
                    else cell_group)
            logger.study(
                logger.get_source_info(),
                """
                Final result for cell group, dataframe with shape {}
                """.format(
                    result.shape))
            return result
                    
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
        excluded_variables = ["gid", "x", "y", "z"]
        def _rename_column(variable):
            return variable if variable in excluded_variables\
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

    def _cached(self,
            pre_synaptic_cell_type_specifier, pre_synaptic_cells,
            post_synaptic_cell_type_specifier, post_synaptic_cells,
            upper_bound_soma_distance=None,
            by=None,
            resample=False,
            sampling_methodology=terminology.sampling_methodology.random,
            number=100):

        """
        Get pathway property value, with caching...
        Cache when possible.

        Arguments
        ---------------
        ...
        """
        max_specifier_length = self.max_length_cell_type_specifier
        assert (
            isinstance(pre_synaptic_cell_type_specifier, frozenset)
            and len(pre_synaptic_cell_type_specifier) > 0
            and len(pre_synaptic_cell_type_specifier) < max_specifier_length
        ), pre_synaptic_cell_type_specifier
        assert (
            isinstance(post_synaptic_cell_type_specifier, frozenset)
            and len(post_synaptic_cell_type_specifier) > 0
            and len(post_synaptic_cell_type_specifier) < max_specifier_length
        ), post_synaptic_cell_type_specifier

        logger.study(
            logger.get_source_info(),
            """
            cache result for specifiers:
            \tpre_synaptic: {}
            \tpost_synaptic: {}
            """.format(
                pre_synaptic_cell_type_specifier,
                post_synaptic_cell_type_specifier))

        key_cache =\
            (pre_synaptic_cell_type_specifier,
             post_synaptic_cell_type_specifier)

        measurement_pairs = self.get_pairs(
            pre_synaptic_cells.rename(
                columns=self._at("pre_synaptic")),
            post_synaptic_cells.rename(
                columns=self._at("post_synaptic")),
            upper_bound_soma_distance=upper_bound_soma_distance)

        if (key_cache not in self.store
            or (sampling_methodology == terminology.sampling_methodology.random
                and resample)):
            self.store[key_cache] =\
                self._grouped_summary(
                    measurement_pairs,
                    pre_synaptic_cell_type_specifier,
                    post_synaptic_cell_type_specifier)

        return self.store[key_cache]

    def _full_summary(self,
            measurement_pairs):
        """..."""
        summary =\
            pd.concat([
                pairs[
                    self.measured_variables
                ].reset_index(
                    drop=True
                ).assign(
                    dummy_variable=0
                ).groupby(
                    ["dummy_variable"] + self.other_grouping_variables
                ).agg(
                    ["size", "sum"]#self.aggregators_inner
                ).pairs.rename(
                    columns={
                        "size": "number_pairs_total",
                        "sum": "number_pairs_connected"}
                ) for pairs in measurement_pairs]
            ).groupby(
                ["dummy_variable"] + self.other_grouping_variables
            ).agg(
                "sum"#self.aggregators_outer
            )
        return self.empty if summary.empty else summary.loc[0]

    def _grouped_summary(self,
            measurement_pairs,
            pre_synaptic_cell_type_specifier,
            post_synaptic_cell_type_specifier):
        """..."""
        pre_synaptic_columns =[
            "pre_synaptic_{}".format(variable)
            for variable in pre_synaptic_cell_type_specifier]
        post_synaptic_columns =[
            "post_synaptic_{}".format(variable)
            for variable in post_synaptic_cell_type_specifier]
        return pd\
            .concat([
                pairs[
                    self.measured_variables
                    + pre_synaptic_columns
                    + post_synaptic_columns
                    + self.other_variables]\
                .groupby(
                    pre_synaptic_columns
                    + post_synaptic_columns
                    + self.other_grouping_variables)\
                .agg(
                    self.aggregators)\
                .pairs\
                .rename(
                    columns=self.columns)
                for pairs in measurement_pairs])\
            .groupby(
                pre_synaptic_columns
                + post_synaptic_columns
                + self.other_grouping_variables)\
            .agg("sum")\
            .assign(**{
                self.phenomenon: self.definition})

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
                   else None
        except TypeError:
            pass
        return None

    @property
    def empty_summary(self):
        """..."""
        return\
            pd.Series({
                key: 0.
                for key in self.columns.values()})\
              .append(
                  pd.Series({self.measurement_label: np.nan}))

    def get_summary(self,
            pre_synaptic_cell_group,
            post_synaptic_cell_group,
            **kwargs):
        """
        Get a full summary for the pathway property for all (cell, cell) pairs.
        """
        return self.__call__(
            pre_synaptic_cell_group=pre_synaptic_cell_group,
            post_synaptic_cell_group=post_synaptic_cell_group,
            with_summary_statistics=True,
            **kwargs)

    def __call__(self,
            pathway=None,
            pre_synaptic_cell_group=None,
            post_synaptic_cell_group=None,
            groupby=GroupByVariables(
                pre_synaptic_cell_type_specifier=None,
                post_synaptic_cell_type_specifier=None),
            upper_bound_soma_distance=None,
            by=None,
            given=None,
            resample=False,
            sampling_methodology=terminology.sampling_methodology.random,
            number=100,
            with_summary_statistics=False):
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
               the pathway property will be returned. """
        logger.study(
            logger.get_source_info(),
            """
            Call to connection probability.
            pathway:
            \t{}
            pre_synaptic_cell_group:
            \t{}
            post_synaptic_cell_group:
            \t{}
            to be group by:
            \t{}
            methodology:
            \t{}
            """.format(
                str(pathway).replace('\n', "\n\t\t"),
                pre_synaptic_cell_group,
                post_synaptic_cell_group,
                groupby,
                sampling_methodology))
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

        def _type_error(what):
            return TypeError(
                """
                {}.
                __call__ may be called either without any parameters about 
                which cell pairs to compute for, or a value for argument 
                `pathway`, or values for arguments `pre_synaptic_cell_group`
                and `post_synaptic_cell_group`, but not both.
                """.format(what))

        memoize = (
            self.memoize
            and pathway is None
            and pre_synaptic_cell_group is None
            and post_synaptic_cell_group is None
            and groupby.pre_synaptic_cell_type_specifier is not None
            and groupby.post_synaptic_cell_type_specifier is not None)

        if pathway is not None:
            if (pre_synaptic_cell_group is not None
                or post_synaptic_cell_group is not None):
                raise _type_error(
                    """
                    __call__ called with values for both pathway and
                    pre / post synaptic cell groups.
                    """)
            pre_synaptic_cell_group = pathway.pre_synaptic
            post_synaptic_cell_group = pathway.post_synaptic

        if (pre_synaptic_cell_group is not None
            and post_synaptic_cell_group is None):
            raise _type_error(
                """
                __call__ called with a value {} for `pre_synaptic_cell_group` 
                in the arguments, but no value for `post_synaptic_cell_group`.
                """.format(
                    pre_synaptic_cell_group))

        if (post_synaptic_cell_group is not None
            and pre_synaptic_cell_group is None):
            raise _type_error(
                """
                __call__called with a value {} for `post_synaptic_cell_group` 
                in the arguments, but no value for `pre_synaptic_cell_group`.
                """.format(
                    post_synaptic_cell_group))

        if pathway is None:
            if (isinstance(pre_synaptic_cell_group, pd.Series)
                and isinstance(post_synaptic_cell_group, pd.Series)):
                pathway =\
                    CellType.pathway(
                        pre_synaptic_cell_group,
                        post_synaptic_cell_group)

        logger.study(
            logger.get_source_info(),
            """
            After processing arguments,
            compute pathway property for:
            pre_synaptic_cell_group: {}
            post_synaptic_cell_group: {}
            """.format(
                pre_synaptic_cell_group,
                post_synaptic_cell_group))

        pre_synaptic_cells =\
            self._resolve_cell_group(
                pre_synaptic_cell_group,
                sampling_methodology=sampling_methodology,
                resample=resample,
                number=number)
        post_synaptic_cells =\
            self._resolve_cell_group(
                post_synaptic_cell_group,
                sampling_methodology=sampling_methodology,
                resample=resample,
                number=number)

        if not memoize:
            measurement_pairs =\
                self.get_pairs(
                    pre_synaptic_cells.rename(
                        columns=self._at("pre_synaptic")),
                    post_synaptic_cells.rename(
                        columns=self._at("post_synaptic")),
                    upper_bound_soma_distance=upper_bound_soma_distance)
            if (groupby.pre_synaptic_cell_type_specifier is not None
                and groupby.post_synaptic_cell_type_specifier is not None):
                return self._grouped_summary(
                    measurement_pairs,
                    groupby.pre_synaptic_cell_type_specifier,
                    groupby.post_synaptic_cell_type_specifier)

            summary = self._full_summary(measurement_pairs)
            summary.at["number_cells_pre_synaptic"] =\
                pre_synaptic_cells.shape[0]
            summary.at["number_cells_post_synaptic"] =\
                post_synaptic_cells.shape[0]
            return summary
            #return summary if with_summary_statistics\
        #        else summary[self.measurement_label]

        pre_synaptic_cell_type_specifier =\
            frozenset(groupby.pre_synaptic_cell_type_specifier)\
            if groupby.pre_synaptic_cell_type_specifier is not None else\
               self._get_cell_type_specifier(pre_synaptic_cell_group)
        post_synaptic_cell_type_specifier =\
            frozenset(groupby.post_synaptic_cell_type_specifier)\
            if groupby.post_synaptic_cell_type_specifier is not None else\
               self._get_cell_type_specifier(post_synaptic_cell_group)

        return self._cached(
            pre_synaptic_cell_type_specifier, pre_synaptic_cells,
            post_synaptic_cell_type_specifier, post_synaptic_cells,
            upper_bound_soma_distance=upper_bound_soma_distance,
            by=by,
            resample=resample,
            sampling_methodology=sampling_methodology,
            number=100)


    def get_pairs(self,
            pre_synaptic_cells,
            post_synaptic_cells,
            upper_bound_soma_distance=None,
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
        logger.study(
            logger.get_source_info(),
            """
            Get connection probability for
            {} pre synaptic cells
            {} post synaptic cells
            """.format(
                pre_synaptic_cells.shape[0],
                post_synaptic_cells.shape[0]))
        for count, (_, post_cell) in enumerate(post_synaptic_cells.iterrows()):
            logger.info(
                logger.get_source_info(),
                """
                Get all pairs for post cell {} / {} ({})
                """.format(
                    post_cell,
                    post_synaptic_cells.shape[0],
                  count / post_synaptic_cells.shape[0]))
            pairs = pre_synaptic_cells\
                .drop(
                    columns="gid"
                ).reset_index(
                    drop=True
                ).assign(
                    pairs=np.in1d(
                        pre_synaptic_cells.gid.values,
                        self.circuit_model.connectome.afferent_gids(
                            post_cell.gid)))
            if upper_bound_soma_distance is not None:
                soma_distance = self\
                    .soma_distance(
                        pre_synaptic_cells,
                        post_cell)
                pairs = pairs[
                    soma_distance < upper_bound_soma_distance
                ].reset_index(
                    drop=True)
            post_cell_info = pd.DataFrame(
                pairs.shape[0] * [post_cell.drop("gid")]
            ).reset_index(
                drop=True)
            yield pd.concat(
                [pairs, post_cell_info],
                axis=1
            ).reset_index(
                drop=True)






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


from .connection_probability import\
    ConnectionProbability,\
    ConnectionProbabilityBySomaDistance
