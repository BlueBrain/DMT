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


class PathwayProperty(Mapping):
    """
    A pathway property.
    Acting like a mapping.
    """

    def __init__(self, method):
        """
        Initialize with a method.
        """
        raise NotImplementedError


    def __getitem__(self, key):
        """
        """
        raise NotImplementedError


def pathway_property(instance_method):
    """
    Decorate an `instance_method` as a PathwayProperty.

    Arguments
    -------------
    `instance_method`: Method of an class instance.
    """
    method_name_for_storage = "_{}".format(instance_method.__name__)

    instance_method._cache = {}

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
        cell_type_specifier = CellType.specifier(pathway.pre)
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

        if cell_type_specifier not in instance_method._cache:
            instance_method._cache[cell_type_specifier] = {}
        
        cache = instance_method._cache[cell_type_specifier]
        if pre_cell_type not in cache:
            cache[pre_cell_type] = {}

        if post_cell_type not in cache[pre_cell_type]:
            cache[pre_cell_type][post_cell_type] =\
                instance_method(instance, pathway)

        return\
            instance_method._cache[
                cell_type_specifier][
                    pre_cell_type][
                        post_cell_type]

    return effective


        




