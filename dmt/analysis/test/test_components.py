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
Test develop a components of an analysis.
"""

from collections import OrderedDict
from scipy import stats
from dmt.model.interface import interfacemethod
from dmt.tk.field import Record
from dmt.tk.plotting import Bars
from ..components import\
    Chapter,\
    Section,\
    Abstract,\
    Intrdoduction,\
    Methods,\
    Results,\
    Discussion,\
    Conclusion


class LayerThicknessAnalysis(Chapter):
    """
    Analyze layer thickness of a brain-circuit.
    """
    class Introduction(Section):
        """
        Cortical regions of the brain contain layers of cells.
        Here we analyze how layer thicknesses vary over  brain region.
        The extent to which layer thicknesses vary over brain regions can
        help us generalize thicknesses measured in one region to another where
        no such measurement is available.

        We should not expect layer thicknesses to match between two 
        brain-regions with significantly different total thicknesses.
        Hence, we will analyze the total thickness of regions separately from
        relative thickness (i.e. layer thickness divided by total thickness).

        """
        pass

   class Methods(Section):
       """
       Thicknesses are measured at a sample of points in the circuit space.

       Measurement of thickness in an unevenly shaped volume such as the
       cortex can be tricky. Thickness can be measured as the distance between
       a point in the top-surface and another in the bottom-surface.
       Matching a top-surface point with a bottom-surface point is not
       straightforward.

       For this measurement, a sample of positions inside a brain-region's
       volume is used. Thickness is measured for each position as length of
       segments that pass through the it.


       TODO: The exact implementation's documentation may need an invocation
       of adapter's methods. How?

       TODO: place parameters and measurement here
       """
       def parameters(self, *args, **kwargs):
           """
           Layer thickness is measured for brain-regions,
           hence the parameters for the measurement are the regions.

           TODO: Should parameters sit here or in the outer-scope,
           in the chapter?
           TODO: Should regions be attributed to the containing chapter?
           """
           return [{"region": r} for r in kwargs["regions"]]

       @interfacemethod
       def get_layer_thickness_values(adapter,
                circuit_model,
                region=None,
                **kwargs):
           """
           Get a sample of values for layer thickness in a named region of the
           circuit.
           
           Arguments
           --------------
           region : name of the region where the thickness must be computed.
           
           Notes
           --------------
           For brain regions with arbitrary shape, their thickness can be hard to
           define. The exact definition is left to the implementation. What this
           analysis expects is a collection (`pandas.Series`) that may contain
           a sample of values for each layer in the named region.
           """
           pass

       @property
       def measurement(self):
           def _get_thickness_relative(adapter, circuit_model, **parameters):
               """..."""
               thickness_layers =\
                   self.get_layer_thickness_values(
                       adapter, circuit_model, **parameters)
               thickness_total =\
                   thickness_layers.sum(axis=1, rename="thickness")
               wide_format =\
                   thickness_layers.apply(c: c / thickness_total)
               wide_format.columns.name = "layer"
               return\
                   pd.concat([
                       wide_format.iloc[i]
                       for i in range(wide_format.shape[0])])\
                     .rename("thickness")

           def _get_thickness_total(adapter, circuit_model, **parameters):
               thickness_layers =\
                   self.get_layer_thickness_values(
                       adapter, circuit_model, **parameters)
               return\
                   thickness_layers.sum(axis=1, rename="thickness")

           return {
               "thickness_layer": _get_thickness_relative,
               "thickness_total": _get_thickness_total}


   class Results(Section):
       """
       Overall, as well as relative layer thicknesses may not be the same
       across the entire neocortex. However we may expect these values to
       be close for contiguous brain areas.
       Our null-hypothesis is that relative layer thickness are constant 
       across sub-regions of a larger brain-region such as the SSCx. 
       To test if our null-hypothesis holds we compare each pair of sub-regions
       ($regions_analyzed) to determine if their total thickness and relative
       layer thicknesses are the same.
       """

       @property
       def illustration(self):
           """..."""
           return {
               "thickness_relative": Bars(xvar="layer",
                                       xlabel="Layer",
                                       yvar="thickness",
                                       ylabel="Thickness",
                                       gvar="region"),
               "thickness_total": Bars(xvar="region",
                                       xlabel="Region",
                                       yvar="thickness",
                                       ylabel="Thickness")}

       @property
       def statistical_analysis(self):
           """
           Think about it.
           """
           regions = self.data.index.get_level_values("region")
           layers = self.data.index.get_level_values("layer")

           def _stats_thickness_total(region_1, region_2):
               data_1 =\
                   self.data\
                       .thickness_total\
                       .xs(region_1, level="region")\
                       .thickness\
                       .to_numpy(np.float64)
               data_2 =\
                   self.data\
                       .thickness_total\
                       .xs(region_2, level="region")\
                       .thickness\
                       .to_numpy(np.float64)
               
               return stats.ttest_ind(data_1, data_2)

           def _stats_thickness_relative(region_1, region_2):
               def _stats_layer(layer):
                   data_1 =\
                       self.data\
                           .thickness_relative\
                           .xs((region_1, layer), level=("region", "layer"))\
                           .thickness\
                           .to_numpy(np.float64)
                   data_2 =\
                       self.data\
                           .thickness_relative\
                           .xs((region_2, layer), level=("region", "layer"))\
                           .thickness\
                           .to_numpy(np.float64)
                   return stats.ttest_ind(data_1, data_2)
               return {
                   layer: _stats_layer(layer)
                   for layer in layers}

           return{
               r1: {
                   r2: {
                       "total": _stats_thickness_total(r1, r2),
                       "relative": _stats_thickness_relative(r1, r2)}}
               for r1 in regions
               for r2 in regions if r2 != r1}


   class Discussion(document.Section):
       """
       Discussion of the results may require a knowledge of the result.
       Pass on this one before developing other sections.
       """
       pass

   class ReferenceData(document.Section):
       """
       List and discuss all the reference data used...
       Pass on this one before developing other sections
       """
       pass








