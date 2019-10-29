"""
Abstraction of a pathway and its properties.
"""
from collections.abc import Mapping
from collections import OrderedDict
import functools
import numpy as np
import pandas as pd
from .cell_type import CellType


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


class PathwayProperty:
    """
    A pathway property.
    Acting like a mapping.
    """
    def __init__(self, instance, instance_method):
        self._method = instance_method
        self._property_name = self.get_storage_name(instance_method)
        self._instance = instance
        self._cache = {}

    def _get_cache(self, cell_type_specifier):
        """..."""
        if cell_type_specifier not in self._cache:
            self._cache[cell_type_specifier] = {}

        return self._cache[cell_type_specifier]

    def _cached(self, pathway):
        """..."""
        cell_type_specifier_cache =\
            self._get_cache(
                CellType.specifier(pathway.pre))
        pre_cell_type = tuple(pathway.pre.values)
        if pre_cell_type not in cell_type_specifier_cache:
            cell_type_specifier_cache[pre_cell_type] = {}
        post_cell_type = tuple(pathway.post.values)
        if post_cell_type not in cell_type_specifier_cache[pre_cell_type]:
            cell_type_specifier_cache[pre_cell_type][post_cell_type] =\
                self._method(self._instance, pathway)
                    
        result = cell_type_specifier_cache[pre_cell_type][post_cell_type]
        if isinstance(result, (float, np.float)):
            return pd.Series({self._property_name: result})
        if isinstance(result, pd.Series):
            return result
        if isinstance(result, np.array):
            return pd.Series({
                (self._property_name, index): element
                for i, element in enumerate(result)})
        raise TypeError(
            """
            Pathway property values for a given pathway should evaluate to:
            \t1. a float
            \t2. a pandas.Series
            \t3. a numpy.array
            got {}
            """.format(result))

    @staticmethod
    def index_names(cell_type_specifier):
        """..."""
        at = lambda pos: [
            (pos, cell_property)
            for cell_property in cell_type_specifier]
        return at("pre") + at("post")
        
    def dataframe(self,
            cell_type_specifier=None,
            pathways=None):
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
                self._instance.pathways(cell_type_specifier)
        else:
            if pathways is None:
                raise type_error

        result = pathways.apply(self._cached, axis=1)

        return pd\
            .concat(
                [pathways, result],
                axis=1)\
            .set_index(list(pathways.columns))

    def __call__(self, pathway):
        """..."""
        return self._cached(pathway)

    @staticmethod
    def validate(instance_method):
        """
        Instance methods that compute pathway properties must start with `get_`
        """
        assert len(instance_method.__name__) > 4
        assert instance_method.__name__[0:3] == "get",\
            instance_method.__name__
        return True

    @staticmethod
    def get_storage_name(instance_method):
        """
        Name of the property to attach to an instance...
        """
        PathwayProperty.validate(instance_method)
        return instance_method.__name__[4:]

    @staticmethod
    def memoized(instance_method):
        """
        Decorate an `instance_method` as a PathwayProperty.
        
        Arguments
        -------------
        `instance_method`: Method of an class instance.
        """
        storage_name = PathwayProperty.get_storage_name(instance_method)

        @functools.wraps(instance_method)
        def effective(instance, pathway):
            """..."""
            if not hasattr(instance, storage_name):
                setattr(
                    instance, storage_name,
                    PathwayProperty(instance, instance_method))
            return getattr(instance, storage_name)(pathway)

        return effective


# class PathwayProperty0:
#     """
#     A pathway property.
#     Acting like a mapping.
#     """

#     def __init__(self, instance_method):
#         """
#         Initialize with a method.
#         """
#         self._method = instance_method
#         self._instance_cache_attribute =\
#             "_cache_{}".format(self._method.__name__)

#     def _get_cache(self, instance, cell_type_specifier):
#         """..."""
#         if not hasattr(instance, self._instance_cache_attribute):
#             setattr(
#                 instance,
#                 self._instance_cache_attribute,
#                 {})
#         cache = getattr(instance, self._instance_cache_attribute)
#         if cell_type_specifier not in cache:
#             cache[cell_type_specifier] = {}

#         return cache[cell_type_specifier]

#     def _cached(self, instance, pathway):
#         """..."""
#         cell_type_specifier =\
#             CellType.specifier(pathway.pre)
#         instance_cache =\
#             self._get_cache(instance, cell_type_specifier)
#         pre_cell_type = tuple(pathway.pre.values)
#         if pre_cell_type not in instance_cache:
#             instance_cache[pre_cell_type] = {}
#         post_cell_type = tuple(pathway.post.values)
#         if post_cell_type not in instance_cache[pre_cell_type]:
#             instance_cache[
#                 pre_cell_type][
#                     post_cell_type] =\
#                         self._method(instance, pathway)

#         return\
#             instance_cache[
#                 pre_cell_type][
#                     post_cell_type]

#     @staticmethod
#     def index_names(cell_type_specifier):
#         """..."""
#         at = lambda pos: [
#             (pos, cell_property)
#             for cell_property in cell_type_specifier]
#         return at("pre") + at("post")
        
#     def dataframe(self, instance, cell_type_specifier):
#         """..."""
#         pathways = instance.pathways(cell_type_specifier)
#         result = pathways.apply(
#             lambda pathway: self._cached(instance, pathway),
#             axis=1)
#         return result\
#             if not isinstance(result, pd.Series) else\
#                pd.DataFrame(result.rename(self._method.__name__))

#     def __call__(self, instance, pathway):
#         """..."""
#         return self._cached(instance, pathway)

#     @staticmethod
#     def memoized(instance_method):
#         """..."""
#         return PathwayProperty(instance_method)

def pathway_property(instance_method):
    """
    Decorate an `instance_method` as a PathwayProperty.

    Arguments
    -------------
    `instance_method`: Method of an class instance.
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
            CellType.specifier(pathway.pre)
        assert\
            CellType.specifier(pathway.post) == cell_type_specifier,\
            """
            Post cell type:
            {}.
            """.format(
                ".\n".join(
                    "{}: {}".join(key, value)
                    for key, value in pathway.post.items()))

        pre_cell_type = tuple(pathway.pre.values)
        post_cell_type = tuple(pathway.post.values)

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
