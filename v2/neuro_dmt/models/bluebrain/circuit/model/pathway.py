"""
Abstraction of a pathway and its properties.
"""
from collections.abc import Mapping
from collections import OrderedDict
import functools
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


class PathwayProperty(WithFields):
    """
    A pathway property.
    Acting like a mapping.
    """
    phenomenon = LambdaField(
        """
        A label to go with the pathway property.
        """,
        lambda self: self.get_storage_name(self.definition))
    definition = Field(
        """
        Defining computation of the pathway property.
        """)
    circuit_model = Field(
        """
        The circuit model in whose body this `PathwayProperty` has been
        defined. This field is required only when the pathway property's
        computation is not a bound method of the circuit model instance,
        in which case the data associated with the circuit model needs to be
        known to compute the pathway property, and hence this `PathwayProperty`
        instance will need access to the circuit model.
        """,
        __required__=False)
    family_variables = Field(
        """
        A tuple (that may be empty), that provides the family defining variables
        for the measurements. For example, if the pathway property must be
        evaluated as a function of soma-distance, this variable must be provided
        as a family variable. The family will then consist of all possible
        pathway definitions.
        """,
        __default_value__=tuple())

    @lazyfield
    def store(self):
        """
        A dict that will hold the cached results.
        """,
        return {}

    @staticmethod
    def as_tuple(pathway):
        """..."""
        return (
            tuple(pathway.pre_synaptic.values),
            tuple(pathway.post_synaptic.values))

    @staticmethod
    def _pre_cell_type(pathway):
        """..."""
        return tuple(pathway.pre_synaptic.values)

    @staticmethod
    def _post_cell_type(pathway):
        """..."""
        return tuple(pathway.post_synaptic.values)

    def _get_store(self, pathway):
        """..."""
        pre_cell_type = self._pre_cell_type(pathway)
        if pre_cell_type not in self.store:
            self.store[pre_cell_type] = {}

        if not self.family_variables:
            return self.store[pre_cell_type]

        post_cell_type = self._post_cell_type(pathway)
        if post_cell_type not in self.store[pre_cell_type]:
            self.store[pre_cell_type][post_cell_type] = {}
        return self.cache[pre_cell_type][post_cell_type]

    def _get(self, pathway, **kwargs):
        """
        Don't use the cache.
        """
        logger.info(
            logger.get_source_info(),
            """
            Call definition with kwargs:  {}
            """.format(kwargs))
        try:
            value = self.definition(self.circuit_model, pathway, **kwargs)
        except AttributeError:
            value = self.definition(pathway, **kwargs)
        if isinstance(value, pd.Series):
            return value
        if isinstance(value, (float, np.float)):
            return pd.Series({self.label: value})
        if isinstance(value, tuple):
            assert len(value) == len(self.label),\
                """
                value: {}
                label: {}
                """.format(value, self.label)
            return pd.Series(dict(zip(self.label, value)))
        if isinstance(value, np.array):
            return pd.Series({
                (self.label, index): element
                for index, element in enumerate(value)})
        raise TypeError(
            """
            Pathway property values for a given pathway should evaluate to:
            \t1. a float
            \t2. a pandas.Series
            \t3. a numpy.array
            got {}
            """.format(value))

    def _stored(self, pathway, resample=False, **kwargs):
        """..."""
        store = self._get_store(pathway)
        if not self.family_variables:
            post_cell_type = self._post_cell_type(pathway)
            if post_cell_type not in store:
                store[post_cell_type] =\
                    self._get(
                        pathway,
                        **kwargs)
            return store[post_cell_type]

        family_values = tuple(
            kwargs.pop(variable)
            for variable in self.family_variables}
        if family_values not in store or resample:
            store[family_values] =\
                self._get(
                    pathway,
                    **dict(zip(self.family_variables, family_values)),
                    **kwargs)

        return store[family_values]
                    
    @staticmethod
    def index_names(cell_type_specifier):
        """..."""
        at = lambda pos: [
            (pos, cell_property)
            for cell_property in cell_type_specifier]
        return at("pre") + at("post")
        
    def dataframe(self,
            cell_type_specifier=None,
            pathways=None,
            resample=False):
        """
        Arguments
        ------------
        `cell_type_specifier`: tuple of cell properties
        `pathways` : pandas.DataFrame of pathways.
        """
        type_error = TypeError(
            """
            {} method {} accepts only one of two arguments:
            \t 1. cell_type_specifier: a tuple of strings
            \t 2. pathways: pandas.DataFrame
            """)
        if cell_type_specifier:
            if pathways is not None:
                raise type_error
            pathways =\
                self.circuit_model.pathways(cell_type_specifier)
        else:
            if pathways is None:
                raise type_error

        result = pathways.apply(
            lambda pathway: self._cached(pathway, resample),
            axis=1)

        return pd\
            .concat(
                [pathways, result],
                axis=1)\
            .set_index(list(pathways.columns))

    def __call__(self, pathway, **kwargs):
        """..."""
        return self._cached(pathway, **kwargs)

    @staticmethod
    def validate(get_one_pathway):
        """
        Instance methods that compute pathway properties must start with `get_`
        """
        assert len(get_one_pathway.__name__) > 4
        assert get_one_pathway.__name__[0:3] == "get",\
            get_one_pathway.__name__
        return True

    @staticmethod
    def get_storage_name(get_one_pathway):
        """
        Name of the property to attach to an instance...
        """
        PathwayProperty.validate(get_one_pathway)
        return get_one_pathway.__name__[4:]

    @staticmethod
    def memoized(get_one_pathway):
        """
        Decorate an instance method as a PathwayProperty.
        
        Arguments
        -------------
        `get_one_pathway`: Method of an class instance.
        """
        storage_name = PathwayProperty.get_storage_name(get_one_pathway)

        @functools.wraps(get_one_pathway)
        def effective(instance, pathway):
            """..."""
            if not hasattr(instance, storage_name):
                setattr(
                    instance, storage_name,
                    PathwayProperty(instance, get_one_pathway))
            return getattr(instance, storage_name)(pathway)

        return effective



class PathwayPropertyFamily(WithFields):
    """
    A family of pathway properties measures the same phenomenon,
    with each member of the family identified by its measurement parameters.
    """
    phenomenon = LambdaField(
        """
        The phenomenon whose measurement values are managed by this
        `PathwayPropertyFamily` instance and all it's
        `PathwayProperty` instances held by it.
        """,
        lambda self: PathwayProperty.get_storage_name(self.definition))
    definition = Field(
        """
        Defining computation of the pathway property.
        """)
    family_variables = Field(
        """
        A tuple (that may be empty), that provides the family defining variables
        for the measurements. For example, if the pathway property must be
        evaluated as a function of soma-distance, this variable must be provided
        as a family variable. The family will then consist of all possible
        pathway definitions.
        """,
        __default_value__=tuple())

    @lazyfield
    def store(self):
        """
        A dict to hold the cached results
        """
        return P{}

    def _stored(self, pathway):
        """
        Get stored, or a new -- storing before returning.
        """
        cell_type_specifier = CellType.specifier(pathway.pre_synaptic)
        if not CellType.specifier(pathway.post_synaptic) != cell_type_specifier:
            raise TypeError(
                """
                PathwayPropertyFamily expects symmetric pathways.
                """)
        try:
            return self.store[cell_type_specifier]
        except KeyError:
            self.store[cell_type_specifier]=\
                PathwayProperty(
                    phenomenon=self.phenomenon,
                    definition=self.definition)
        return self.store[cell_type_specifier]

    def __call__(self, pathway, **kwargs):
        """
        Arguments
        ------------
        pathway : Basically (pre, post) combination
        kwargs :: Key word arguments containing information family variable
        values.
        """
        if not all(variable in kwargs for variable in self.family_variables):
            raise TypeError(
                """
                A PathwayPropertyFamily can be called only with
                values for all of its family variables provided as
                variable keyword arguments.
                """)
        handler_pathway_property = self._stored(pathway)
        return handler_pathway_property(pathway, **kwargs)   


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
            CellType.specifier(pathway.pre_synaptic)
        assert\
            CellType.specifier(pathway.post_synaptic) == cell_type_specifier,\
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
