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

from ..import *

LOGGER = Logger(client=__file__)

class CompositionAnalysisSuite(WithFields):
    """
    Analyze the composition of a brain circuit model.
    """
    sample_size = Field(
        """
        Number of individual sample measurements for each set of parameter
        values.
        """,
        __default_value__=100)
    size_roi = Field(
        """
        Size of ROIs that composition phenomena will be computed in.
        """,
        __default_value__=50. * np.ones(3))
    path_reports = Field(
        """
        Location where the reports will be posted.
        """,
        __default_value__=os.path.join(os.getcwd(), "reports"))
    morphologies_interneurons = Field(
        """
        Interneuron morphologies that are stained by markers",
        """,
        __default_value__=[
            "BP", "BTC", "CHC", "DB", "LBC", "NBC", "MC", "SBC", "SSC"])
    number_cortical_thickness_bins = Field(
        """
        Number of bins for by depth or by height analyses.
        """,
        __default_value__=50)


    class AdapterInterface(Interface):
        """
        Document the methods that will be used by the analyses in this suite
        to measure a circuit model.

        To use this suite of analyses, provide these methods in an adapter of
        this interface.
        """
        def get_provenace(self, circuit_model):
            """
            Provide a dictionary with following keys:

            1. label: that names the circuit model
            2. authors: group that built the circuit model
            3. release_date: when the circuit model was released
            4. location: a URI from where the circuit model can be loaded
            5. animal: whose brain was modeled
            6. age: of the animal at which the brain was modeled
            7. brain_region: that was modeled
            """
            raise NotImplementedError

        def get_brain_regions(self, circuit_model):
            """
            A list of named regions in the `circuit_model`.
            """
            raise NotImplementedError

        def get_layers(self, circuit_model):
            """
            List of the layers in the brain region  modeled.
            """
            raise NotImplementedError

        def get_spatial_volume(self, circuit_model, **spatial_query):
            """
            Get total volume in circuit space that satisfies a spatial query.
            """
            raise NotImplementedError

        def random_position(self,
                circuit_model,
                region=None,
                layer=None,
                depth=None,
                height=None):
            """
            A random position in the circuit space that falls in the region
            specified by the query arguments for circuit location.

            Arguments
            ----------------
            `circuit_model`: model of a brain circuit
            `layer`: Layer where random position should be located
            `region`: Brain region where random position should be located
            `depth`: Cortical depth where random position should be located
            `height`: Cortical height where random position should be located

            How random position will be used
            ----------------------------------
            A cuboid region-of-interest (ROI) of specified size will be defined
            around the random position, and passed to the adapter method
            `get_cell_count` to obtain the number of cells in the ROI. Ratio of
            the number of cells to the ROI volume will be cell density. Multiple
            values of cell density obtained in this way, for the same location
            query will constitute sample cell density values.

            Returns
            -----------------
            None if there is no space corresponding to the query, else
            a 3D `np.ndarray` providing the X, Y, and Z components of a position
            in the circuit space.
            """
            raise NotImplementedError

        def get_cells(self, circuit_model, properties=None, **query):
            """
            Get cells in a region of interest (ROI) specified by a query.

            Arguments
            ---------------
            properties: cell properties to load
            query: var-kwargs specifying the region of interest,
            ~      and / or cell types of the cells to be retrieved

            Example
            ---------------
            adapter.get_cells(circuit_model,
            ~                 layer='L1',
            ~                 region='S1HL',
            ~                 mtype='L1_MC',
            ~                 etype='bNAC')
            """
            raise NotImplementedError

        def get_layer_thickness_values(self, circuit_model, region=None):
            """
            Get values of the thicknesses of layers in the given region.
            Because layer thickness of a region may not be fixed,
            the result may hold a sample of measurements.

            Returns
            ------------
            `pandas.Series` with `layer` value in the index.
            """
            raise NotImplementedError


    def _get_random_region(self, circuit_model, adapter, spatial_query):
        """
        Get a random region (of interest) located in the brain region specified
        by a spatial query.
        """
        position = adapter.random_position(circuit_model, **spatial_query)

        if position is None:
            return None

        return Cuboid(position - self.size_roi / 2.,
                      position + self.size_roi / 2.)

    def _get_random_cells(self, circuit_model, adapter, spatial_query):
        """..."""
        roi = self._get_random_region(circuit_model, adapter, spatial_query)

        if roi is None:
            return None

        try:
            roi = roi.bbox
        except AttributeError:
            pass

        return adapter.get_cells(circuit_model, roi=roi)

    @staticmethod
    def _with_brain_regions(dataframe, brain_regions):
        """..."""
        return pd.concat([
            dataframe.reset_index(
            ).assign(region=region
            ).set_index(
                ["region", "layer"]
            ) for region in brain_regions])

    @lazyfield
    def parameters_regions_and_layers(self):
        """..."""
        def _regions_and_layers(adapter, circuit_model):
            """..."""
            regions = adapter.get_brain_regions(circuit_model)
            layers = adapter.get_layers(circuit_model)
            return pd.DataFrame(
                [[r, l] for r in regions for l in layers],
                columns=["region", "layer"])

        return Parameters(_regions_and_layers, labels=("region", "layer"))

    @lazyfield
    def parameters_regions_and_depths(self):
        """..."""
        def _regions_and_depths(adapter, circuit_model):
            regions = adapter.get_brain_regions(circuit_model)
            number_bins = self.number_cortical_thickness_bins
            positions = np.linspace(0., 1., number_bins + 1)
            return pd.DataFrame({
                ("region", ""): [r for r in regions for _ in range(number_bins)],
                ("depth", "begin"): [d for _ in regions for d in positions[:-1]],
                ("depth", "end"): [d for _ in regions for d in positions[1:]]})

        return Parameters(_regions_and_depths, labels=("regions", "depth"))


    phenomena_analyzed = Record(
        cell_density = Phenomenon(
            "Cell Density",
            "Number of cells in a unit volume (mm^3)",
            group="Composition"),
        fraction_inhibitory = Phenomenon(
            "Inhibitory Cell Fraction",
            "Fraction of inhibitory cells",
            group="Composition"),
        marker_stain_density = Phenomenon(
            "Density of marker stains",
            "Density of cells in a unit of volume stained by markers.",
            group="Composition"))

    reference_data = Record(
        cell_density = OrderedDict(),
        fraction_inhibitory=OrderedDict(),
        marker_stain_density=OrderedDict())

    def measurement_cell_density_using_sampling(self,
            adapter,
            circuit_model,
            **query):
        """
        Get cell density by sampling random regions in circuit space
        specified by a query.
        """
        spatial_query =\
            terminology.circuit.get_spatial_query(query)
        cuboid_to_measure =\
            self._get_random_region(
                adapter, circuit_model, spatial_query)

        if cuboid_to_measure is None:
            return 0.

        cell_count =\
            adapter.get_cells(
                circuit_model, roi=cuboid_to_measure
            ).shape[0]
        spatial_volume =\
            cuboid_to_measure.volume

        return 1.e9 * cell_count / spatial_volume
