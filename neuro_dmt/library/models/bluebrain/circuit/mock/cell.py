# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Definitions and methods for cells in a MockCircuit.
"""

from collections import Mapping
import numpy as np
import pandas as pd
from neuro_dmt import terminology
from dmt.tk.field import Field, Property, WithFields, lazy
from . import CircuitComposition

cell_properties =[
    terminology.bluebrain.cell.index,
    terminology.bluebrain.cell.layer,
    terminology.bluebrain.cell.region,
    terminology.bluebrain.cell.mtype,
    terminology.bluebrain.cell.etype,
    terminology.bluebrain.cell.morphology,
    terminology.bluebrain.cell.morph_class,
    terminology.bluebrain.cell.me_combo,
    terminology.bluebrain.cell.x,
    terminology.bluebrain.cell.y,
    terminology.bluebrain.cell.z,
    terminology.bluebrain.cell.synapse_class]


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
        """)
        #__default_value__="NAC")
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
        Property-value pairs of this cell, as a dict.
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
    layers = Field(
        """
        Layers represented in the circuit model.
        """,
        __required__=False)
    regions = Field(
        """
        Brain regions represented in the circuit model.
        """,
        __required__=False)

    def __init__(self, cells, **field_values):
        """
        Initialize

        Arguments
        --------------
        cells :: Either a pandas dataframe, or a list of Cells.
        """
        super().__init__(**field_values)
        if isinstance(cells, pd.DataFrame):
            self._dataframe = cells
        else:
            self._dataframe =\
                pd.DataFrame([
                    cell.as_dict for cell in list(cells)])
        self.size = self._dataframe.shape[0]
        self.gids = np.array(self._dataframe.index)

    def get_property_filter(self, property_name, property_value):
        """
        Get a logical vector that can be used to filter 'cell_property',
        by applying it to the cell collectiondef  dataframe.
        """
        if property_name in ["x", "y", "z"]:
            return np.logical_and(
                self._dataframe[property_name] >= property_value[0],
                self._dataframe[property_name] < property_value[1])
        return\
            self._dataframe[property_name]\
                .apply(
                    lambda v: (
                        v == property_value
                        if not isinstance(property_value, (frozenset, set, list))
                        else v in frozenset(property_value)))

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
        if len(group) == 0:
            return __get_properties(self._dataframe)

        filtered =\
            pd.Series(
                self._dataframe.shape[0] * [True],
                name="filtered")
        for property_name, property_value in group.items():
            property_filter =\
                self.get_property_filter(
                    property_name,
                    property_value)
            filtered =\
                np.logical_and(filtered, property_filter)

        return __get_properties(self._dataframe[filtered])
            
    def ids(self, group=None):
        """
        GIDs of cells in `group`.
        """
        return self.get(group).index.values
