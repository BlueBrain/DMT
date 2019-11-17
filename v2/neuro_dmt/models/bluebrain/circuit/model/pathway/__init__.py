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

def afferent_summary(pairs):
    """..."""
    pairs.at["number_pairs_total"] =\
        pairs.number_cells_pre_synaptic * pairs.number_cells_post_synaptic
    pairs.at["probabilty_connection"] =\
        pairs.number_pairs_connected / pairs.number_pairs_total
    pairs.at["number_connections_afferent"] =\
        pairs.number_pairs_connected / pairs.number_cells_post_synaptic
    return pairs

def efferent_summary(pairs):
    """..."""
    pairs.at["number_pairs_total"] =\
        pairs.number_cells_pre_synaptic * pairs.number_cells_post_synaptic
    pairs.at["probabilty_connection"] =\
        pairs.number_pairs_connected / pairs.number_pairs_total
    pairs.at["number_connections_efferent"] =\
        pairs.number_pairs_connected / pairs.number_cells_pre_synaptic
    return pairs

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


class PathwaySummary(WithFields):
    """
    Compute and store a circuit's pathway properties.
    """
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

    @staticmethod
    def _at(role_synaptic):
        """..."""
        excluded_variables = ["gid", "x", "y", "z"]
        def _rename_column(variable):
            return variable if variable in excluded_variables\
                else  "{}_{}".format(role_synaptic, variable)
        return _rename_column

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
            measurement_pairs,
            with_soma_distance=False):
        """..."""
        variables_groupby=\
            ["dummy_variable", "soma_distance"]\
            if with_soma_distance else\
               ["dummy_variable"]
        measured_variables =\
            ["number_pairs_connected", "soma_distance", "number_cells_pre_synaptic"]\
            if with_soma_distance else\
               ["pairs"]
        def _pre_summary(pairs):
            pairs_summary =\
                pairs[
                    measured_variables
                ].reset_index(
                    drop=True
                ).assign(
                    dummy_variable=0
                ).groupby(
                    variables_groupby
                ).agg(
                    "sum"
                ).assign(
                    number_cells_post=1.
                )
            return\
                pairs_summary.pairs.rename(
                    columns={
                        "size": "number_pairs_total",
                        "sum": "number_pairs_connected"}
                ).assign(
                    number_cells_post_synaptic=1.
                ).join(
                    pairs_summary.number_cells_pre_synaptic)
        
        summary =\
            pd.concat([
                _pre_summary(pairs)
                for pairs in measurement_pairs]
            ).groupby(
               variables_groupby 
            ).agg(
                "sum"
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

    def probability_connection(self,
            pre_synaptic_cells,
            post_synaptic_cells,
            upper_bound_soma_distance=None,
            with_soma_distance=False):
        """
        Summarized connection probability.

        Arguments
        -------------
        pre_synaptic_cells : pandas.DataFrame of cells on the pre-synaptic side.
        post_synaptic_cells: pandas.DataFrame of cells on the post-synaptic side.
        """
        pairs_measured = self.get_pairs(
            pre_synaptic_cells.rename(
                columns=self._at("pre_synaptic")
            ),
            post_synaptic_cells.rename(
                columns=self._at("post_synaptic")
            ),
            upper_bound_soma_distance=upper_bound_soma_distance,
            with_soma_distance=with_soma_distance
        )
        variables_measured =\
            ["number_pairs_total", "number_pairs_connected", "soma_distance"]\
            if with_soma_distance else\
               ["number_pairs_total", "number_pairs_connected"]
        variables_groupby =\
            ["dummy_variable", "soma_distance"]\
            if with_soma_distance else\
               ["dummy_variable"]

        def _probability_connection(summary):
            return summary.number_pairs_connected / summary.number_pairs_total
       
        summary = pd.concat([
            pairs[
                variables_measured
            ].reset_index(
                drop=True
            ).assign(
                dummy_variable=0
            ).groupby(
                variables_groupby
            ).agg(
                "sum"
            ) for pairs in pairs_measured
        ]).groupby(
            variables_groupby
        ).agg(
            "sum"
        ).assign(
            probability_connection=_probability_connection
        )
        if summary.empty:
            if with_soma_distance:
                summary = pd.DataFrame(
                    [],
                    columns=variables_measured + ["probability_connection"]
                )
            else:
                summary = pd.Series(dict(
                    number_pairs_total=0.,
                    number_pairs_connected=0.,
                    probability_connection=np.nan)
                )
        return summary.loc[0]

    def number_connections_afferent(self,
            pre_synaptic_cells,
            post_synaptic_cells,
            upper_bound_soma_distance=None,
            with_soma_distance=False):
        """
        Summrized number of afferent connections.


        Arguments
        -------------
        pre_synaptic_cells : pandas.DataFrame of cells on the pre-synaptic side.
        post_synaptic_cells: pandas.DataFrame of cells on the post-synaptic side.

        """
        pairs_measured = self.get_pairs(
            pre_synaptic_cells.rename(
                columns=self._at("pre_synaptic")
            ),
            post_synaptic_cells.rename(
                columns=self._at("post_synaptic")
            ),
            upper_bound_soma_distance=upper_bound_soma_distance,
            with_soma_distance=with_soma_distance
        )
        variables_measured =\
            ["number_pairs_total", "number_pairs_connected", "soma_distance"]\
            if with_soma_distance else\
               ["number_pairs_total", "number_pairs_connected"]
        variables_groupby =\
            ["dummy_variable", "soma_distance"]\
            if with_soma_distance else\
               ["dummy_variable"]

        summary = pd.concat([
            pairs[
                variables_measured
            ].reset_index(
                drop=True
            ).assign(
                dummy_variable=0
            ).groupby(
                variables_groupby
            ).agg(
                "sum"
            ) for pairs in pairs_measured
        ]).groupby(
            variables_groupby
        ).agg(
            ["mean", "std"]
        )
        if summary.empty:
            if with_soma_distance:
                return pd.DataFrame(
                    [],
                    columns=pd.MultiIndex.from_tuples([
                        ("number_pairs_total", "mean"),
                        ("number_pairs_total", "std"),
                        ("number_pairs_connected", "mean"),
                        ("number_pairs_connected", "std")
                    ])
                )
            return pd.Series({
                ("number_pairs_total", "mean"): 0.,
                ("number_pairs_connected", "mean"): 0.,
                ("number_pairs_total", "std"): 0.,
                ("number_pairs_connected", "std"): 0.
            })

        return pd.DataFrame({
            ("number_pairs_total", "mean"): summary.number_pairs_total["mean"],
            ("number_pairs_total", "std"): summary.number_pairs_total["std"],
            ("number_connections_afferent", "mean"): summary.number_pairs_connected["mean"],
            ("number_connections_afferent", "std"): summary.number_pairs_connected["std"]
        }).loc[0]

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
                "number_pairs_total" : 0.,
                "number_pairs_connected" : 0.})

    @staticmethod
    def soma_distance(
            xcell, ycell,
            bin_size=100.):
        """
        Soma distance between cells.

        Arguments
        -------------------------
        xcell / ycell : A single cell (i.e. a pandas.Series),
        ~               or a collection of cells (i.e. a pandas.DataFrame)
        """
        XYZ = ["x", "y", "z"]
        distance = np.linalg.norm(xcell[XYZ] - ycell[XYZ], axis=1)
        bin_starts = bin_size * np.floor(distance / bin_size)
        return [
            (bin_start, bin_start + bin_size)
            for bin_start in bin_starts]

    def get_pairs(self,
            pre_synaptic_cells,
            post_synaptic_cells,
            upper_bound_soma_distance=None,
            with_soma_distance=False,
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
                .reset_index(
                    drop=True
                ).assign(
                    number_pairs_connected=np.in1d(
                        pre_synaptic_cells.gid.values,
                        self.circuit_model.connectome.afferent_gids(
                            post_cell.gid)),
                    number_pairs_total=1.)
            if upper_bound_soma_distance is not None:
                soma_distance = self\
                    .soma_distance(
                        pre_synaptic_cells,
                        post_cell)
                pairs = pairs[
                    soma_distance < upper_bound_soma_distance
                ].reset_index(
                    drop=True)
            if with_soma_distance:
                pairs = pairs.assign(
                    soma_distance=self.soma_distance(
                        pre_synaptic_cells,
                        post_cell))
            post_cell_info = pd.DataFrame(
                pairs.shape[0] * [post_cell.drop("gid")]
            ).reset_index(
                drop=True
            )
            yield pd.concat(
                [pairs, post_cell_info],
                axis=1
            ).reset_index(
                drop=True)

    def __call__(self,
            pre_synaptic_cells,
            post_synaptic_cells,
            groupby=GroupByVariables(
                pre_synaptic_cell_type_specifier=None,
                post_synaptic_cell_type_specifier=None),
            upper_bound_soma_distance=None,
            with_soma_distance=None):
        """
        Compute, or retrieve from the store...

        Arguments
        -------------
        pre_synaptic_cells : pandas.DataFrame of cells on the pre-synaptic side.
        post_synaptic_cells: pandas.DataFrame of cells on the post-synaptic side.
        """
        if upper_bound_soma_distance is not None and with_soma_distance:
            raise TypeError(
                """
                Argument `with_soma_distance` cannot be `True` in
                `get_pairs(...)` call with a valid value of
                `upper_bound_soma_distance`.
                """)

        logger.study(
            logger.get_source_info(),
            """
            Compute pathway property for 
            pre_synaptic_cells:
            \t{}
            post_synaptic_cells:
            \t{}
            """.format(
                pre_synaptic_cells.shape[0],
                post_synaptic_cells.shape[0]))

        measurement_pairs =\
            self.get_pairs(
                pre_synaptic_cells.rename(
                    columns=self._at("pre_synaptic")),
                post_synaptic_cells.rename(
                    columns=self._at("post_synaptic")),
                upper_bound_soma_distance=upper_bound_soma_distance,
                with_soma_distance=with_soma_distance)

        summary =\
            self._full_summary(
                measurement_pairs,
                with_soma_distance=with_soma_distance)
        summary.at[
            "number_cells_pre_synaptic"] =\
                pre_synaptic_cells.shape[0]
        summary.at[
            "number_cells_post_synaptic"] =\
                post_synaptic_cells.shape[0]
        return connectome_summary(summary)


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
