"""
Definitions and methods for cells in a MockCircuit.
"""

from collections import Mapping
import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell as CellProperty
from dmt.tk.field import Field, Property, WithFields, lazy
from . import CircuitComposition

cell_properties =[
    CellProperty.ID,
    CellProperty.LAYER,
    CellProperty.MTYPE,
    CellProperty.MORPHOLOGY,
    CellProperty.MORPH_CLASS,
    CellProperty.ME_COMBO,
    CellProperty.REGION,
    CellProperty.X, CellProperty.Y, CellProperty.Z,
    CellProperty.SYNAPSE_CLASS]


class Cell(WithFields):
    """
    Defines a cell, and documents it's (data) fields.
    This class is mostly for documenting and learning purposes.
    """
    region = Field(
        """
        Label of the region where this cell lies.
        For example, 'SSCx', 'Somatosensory-cortex'.
        """,
        __default_value__="brain")
    layer = Field(
        """
        Label of the layer that this cell lies in.
        Field 'layer' makes sense for brain areas with layers,
        such as the cortex, and the hippocampus.
        """,
        __default_value__="not-defined")
    nucleus = Field(
        """
        Nucleus of cells among which this cell lies.
        Field 'nucleus' makes sense for brain areas like the thalamus.
        (Check facts, I am making things up.)
        """,
        __default_value__="not-defined")
    position = Field(
        """
        Position of the cell in circuit space.
        """)
    mtype = Field(
        """
        The morphological type of this cell.
        The mtype must be one of several categories.
        """)
    etype = Field(
        """
        The electrical type this cell.
        The etype must be one of several categories.
        """,
        __default_value__="not-defined")
    morph_class = Field(
        """
        The morphological class of this cell's morphology
        (categorized as mtype). There are at least two morphological classes,
        namely 'PYR' (pyramidal cells) and 'INT' (interneuron cells).
        """,
        __default_value__="not-defined")

    @property
    def synapse_class(self):
        """
        Synapse class of a cell is either EXCitatory or INHibitory.
        """
        return "EXC" if "PC" in self.mtype else "INH"

    @property
    def as_dict(self):
        """
        Convert this Cell instance to a dict.
        """
        try:
            x = self.position.X
            y = self.position.Y
            z = self.position.Z
        except AttributeError:
            x = self.position[0]
            y = self.position[1]
            z = self.position[2]

        return dict(
            region=self.region,
            layer=self.layer,
            nucleus=self.nucleus,
            mtype=self.mtype,
            etype=self.etype,
            morph_class=self.morph_class,
            synapse_class=self.synapse_class,
            x=x, y=y, z=z)


class CellCollection(WithFields):
    """
    Collection of cells.
    Cell gids are set here.
    This collection will be immutable.
    """
    def __init__(self, cells):
        """
        Initialize

        Arguments
        --------------
        cells :: Either a pandas dataframe, or a list of Cells.
        """
        if isinstance(cells, pd.DataFrame):
            self._dataframe = cells
        else:
            self._dataframe =\
                pd.DataFrame([
                    cell.as_dict for cell in list(cells)])
        self.size = self._dataframe.shape[0]
        self.gids = np.array(self._dataframe.index)

    def get_property_filter(self, cell_property, value):
        """
        Get a logical vector that can be used to filter 'cell_property',
        by applying it to the cell collectiondef  dataframe.
        """
        property_values = self._dataframe[cell_property]
        try:
            value_set = set(value)
            return property_values.apply(lambda v: v in value_set)
        except TypeError:
            return property_values.apply(lambda v: v == value)
                
        raise TypeError(
            "Unfilterable type of value {}".format(value))
        # return\
        #     self._dataframe[cell_property]\
        #         .apply(
        #             lambda v: v == value\
        #             if not isinstance(value, (set, list)) else\
        #             lambda v: v in set(value))


    def get(self, group=None, properties=None):
        """
        Get a dataframe, with cells of 'group' (any cell type if None).
        Not all but only specified 'properties' will be returned.
        If no 'properties' are specified, all properties will be returned.

        Arguments
        -----------------
        group :: Either a cell gid, or a list of gids, or a mapping from
        cell property to its value (or value set).
        properties :: A single property or a list of properties to get.
        """
        def __get_properties(data_frame_or_series):
            """
            Only columns corresponding to 'properties' requested.
            """
            return data_frame_or_series if properties is None\
                else data_frame_or_series[properties]
        
        if group is None:
            return __get_properties(self._dataframe)
        if (isinstance(group, (int, np.integer,)) or
            isinstance(group, (list, np.ndarray))): #has to be list of ints
            return __get_properties(self._dataframe.loc[group])

        assert isinstance(group, Mapping)
        return __get_properties(
            self._dataframe[
                np.logical_and([
                    self.get_property_filter(cell_property, property_value)
                    for cell_property, property_value in group.items()])])
