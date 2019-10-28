"""
Abstraction of a pathway and its properties.
"""
from collections.abc import Mapping
from collections import OrderedDict
import functools
import numpy as np
import pandas as pd


class CellType:
    """
    How do we specify the type of a cell.
    """
    def __init__(self, value):
        """
        Arguments
        --------------
        `value`: a Mapping like an OrderedDict, or a pandas.Series
        """
        self._specifier = CellType.specifier(value)
        self._value = value

    @staticmethod
    def specifier(cell_type):
        """
        Get specifiers for a given cell type.

        Arguments
        --------------
        `cell_type`: a Mapping like an OrderedDict, or a pandas.Series
        """
        if isinstance(cell_type, OrderedDict):
            return tuple(cell_type.keys())
        if isinstance(cell_type, pd.Series):
            return tuple(cell_type.index.values)
        raise TypeError(
            """
            Can extract cell type specifiers from an `OrderedDict`
            or a `pandas.Series`, received a {}
            """.format(type(cell_type)))

    @staticmethod
    def pathway(
            pre_synaptic_cell_type,
            post_synaptic_cell_type):
        """
        A `Pathway` like object from a specified cell type on the
        pre-synaptic side and a specified cell type on  the 
        post-synaptic side.
        """
        def _at(pos, cell_type):
            return pd.Series(
                cell_type.values,
                index=pd.MultiIndex.from_tuples([
                    (pos, value)
                    for value in cell_type.index.values]))
        return\
            _at("pre", pre_synaptic_cell_type).append(
                _at("post", post_synaptic_cell_type))

    @staticmethod
    def memoized(instance_method):
        """
        Memoize the results of a method that takes
        cell type specifiers as arguments.
        """
        instance_method._cache = {}

        @functools.wraps(instance_method)
        def effective(instance, cell_type_specifier):
            """..."""
            if cell_type_specifier not in instance_method._cache:
                instance_method._cache[cell_type_specifier] =\
                    instance_method(instance, cell_type_specifier)
            return instance_method._cache[cell_type_specifier]

        return effective

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
                    
        return cell_type_specifier_cache[pre_cell_type][post_cell_type]

    @staticmethod
    def index_names(cell_type_specifier):
        """..."""
        at = lambda pos: [
            (pos, cell_property)
            for cell_property in cell_type_specifier]
        return at("pre") + at("post")
        
    def dataframe(self, cell_type_specifier):
        """..."""
        pathways = self._instance.pathways(cell_type_specifier)
        result = pathways.apply(
            lambda pathway: self._cached(pathway),
            axis=1)
        return result\
            if not isinstance(result, pd.Series) else\
               pd.DataFrame(result.rename(self._method.__name__))

    def __call__(self, pathway):
        """..."""
        return self._cached(pathway)

    @staticmethod
    def memoized(instance_method):
        """
        Decorate an `instance_method` as a PathwayProperty.
        
        Arguments
        -------------
        `instance_method`: Method of an class instance.
        """
        assert len(instance_method.__name__) > 4
        assert instance_method.__name__[0:3] == "get",\
            instance_method.__name__
        storage_name =\
            instance_method.__name__[4:]
        
        @functools.wraps(instance_method)
        def effective(instance, pathway):
            if not hasattr(instance, storage_name):
                setattr(
                    instance,
                    storage_name,
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
