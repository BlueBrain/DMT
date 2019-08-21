"""
Brain circuit models from the Blue Brain project
"""

import os
from pathlib import Path
import numpy
import pandas
import bluepy
from bluepy.v2.enums import Cell, Synapse, Segment, Section
from bluepy.v2.circuit import Circuit
from bluepy.geometry.roi import ROI as RegionOfInterest
import neurom
from dmt.tk.field import Field, lazyfield, WithFields
from dmt.tk.journal import Logger

logger = Logger("BlueBrainCircuitModel")

def _get_bounding_box(region_of_interest):
    """
    Get bounding box of a region of interest
    """
    try:
        return region_of_interest.bbox
    except AttributeError:
        return region_of_interest
    return None

class BlueBrainCircuitModel(WithFields):
    """
    A wrapper around bluepy circuit.
    """
    label = Field(
        """
        A label for this circuit instance.
        """,
        __default_value__="BlueBrainCircuitModel")
    circuit_config = Field(
        """
        Path to the circuit's config file.
        """)
    animal = Field(
        """
        Animal species whose brain region was modeled.
        """,
        __default_value__="NA")
    brain_region = Field(
        """
        Name of the brain region that was modeled.
        """,
        __default_value__="NA")
    
    @lazyfield
    def uri(self):
        """
        Universal Resource Identifier.
        Where can we find this circuit?
        """
        return Path(self.circuit_config).parent
    
    @lazyfield
    def bluepy_circuit(self):
        """
        The circuit, as BluePy sees it.
        """
        return Circuit(self.circuit_config)
    
    @lazyfield
    def cells(self):
        """
        CellCollection of this circuit
        """
        return self.bluepy_circuit.cells
    
    @lazyfield
    def connectome(self):
        """
        Connectome of this circuit
        """
        try:
            return self.bluepy_circuit.connectome
        except bluepy.exceptions.BluePyError:
            logger.warn(
                "No connectome for circuit {}".format(self.circuit_config))

        return None

    @lazyfield
    def segment_index(self):
        """
        Segment Index for the morphology spatial index.
        """
        segment_index =  self.bluepy_circuit.morph.spatial_index

        if not segment_index:
            raise AttributeError(
                "No spatial index for circuit {}.".format(self.circuit_config))

        return segment_index


    def get_segments(self, region_of_interest):
        """
        Segments in a region.
        """
        corner_0, corner_1 = _get_bounding_box(region_of_interest)

        dataframe_segments = self\
            .segment_index\
            .q_window_oncenter(corner_0, corner_1)

        position_1 = dataframe_segments[
            [Segment.X1, Segment.Y1, Segment.Z1]
        ].values
        position_2 = dataframe_segments[
            [Segment.X2, Segment.Y2, Segment.Z2]
        ].values
        lengths =  numpy.sqrt(numpy.sum(
            (position_1 - position_2) ** 2,
            axis=1))
        radiuses =  numpy.mean(
            dataframe_segments[[Segment.R1, Segment.R2]].values,
            axis=1)
        volumes = numpy.pi * (radiuses ** 2) * lengths

        return dataframe_segments.assign(
            length=lengths, radius=radiuses, volume=volumes)


    def get_dendrite_length(self, region_of_interest):
        """
        Total dendrite length in a  region of interest

        Arguments
        -----------
        region_of_interest:
        ~   bluepy.geometry.ROI or tuple(numpy.ndarray, numpy.ndarray)
        """
        segments = self.get_segments(region_of_interest, with_length=True)


        dendrites = segments[
            (segments[Section.NEURITE_TYPE] == neurom.BASAL_DENDRITE) |
            (segments[Section.NEURITE_TYPE] == neurom.APICAL_DENDRITE)]

        return numpy.sum(dendrites.length)

    def _segments_aggregated_by_mtype(self, dataframe, aggregator):
        """
        Aggregate a segments dataframe by mtypes.

        Arguments
        ---------
        dataframe:
        ~   pandas.DataFrame
        aggregator:
        ~   a function that aggregates
        """
        gids_cell = dataframe.gid.unique()
        mtypes_cell = self.cells.get(gids_cell, properties=[Cell.MTYPE])
        mtype_dataframe = dataframe.set_index("gid").join(mtypes_cell)
        grouped_by_mtype = mtype_dataframe.groupby(u"mtype")
        mtypes = mtype_dataframe.mtype.unique

        def _get_group_segments(mtype):
            """..."""
            group_dataframe = grouped_by_mtype.get_group(mtype)
            return {
                "mtype": mtype,
                neurom.AXON: aggregator(
                    group_dataframe,
                    neurom.AXON),
                neurom.BASAL_DENDRITE: aggregator(
                    group_dataframe,
                    neurom.BASAL_DENDRITE),
                neurom.APICAL_DENDRITE: aggregator(
                    group_dataframe,
                    neurom.APICAL_DENDRITE)}

        return pandas.DataFrame([
            _get_group_segments(mtype) for mtype in mtypes])

    def get_segment_lengths(self, region_of_interest, by=None):
        """
        Length of segments in a region of interest,
        either total, or by mtype.
        """

        segments = self.get_segments(region_of_interest)

        def _total_length(dataframe, neurite_type):
            """
            Total length of a given neurite type.
            """
            return numpy.sum(
                dataframe.length[
                    dataframe[Section.NEURITE_TYPE] == neurite_type
                ].values)

        if not by:
            return pandas.Series({
                neurite_type: _total_length(segments, neurite_type)
                for neurite_type in (
                        neurom.AXON,
                        neurom.BASAL_DENDRITE,
                        neurom.APICAL_DENDRITE)})

        if by == "mtype":
            return self._segments_aggregated_by_mtype(segments, _total_length)

        raise ValueError(
            "Unkown criterion to get segment lengths by: {}".format(by))

    def get_segment_volumes(self, region_of_interest, by=None):
        """
        Segment volume fraction in a region.
        """
        segments = self.get_segments(region_of_interest)

        def _total_volume(dataframe, neurite_type):
            """
            Total volume of `neurite_type`.
            """
            return numpy.sum(
                dataframe.volume[
                    dataframe[Section.NEURITE_TYPE] == neurite_type
                ].values)

        if by is None:
            return pandas.Series({
                neurite_type: _total_volume(segments, neurite_type)
                for neurite_type in (
                        neurom.AXON,
                        neurom.BASAL_DENDRITE,
                        neurom.APICAL_DENDRITE)})
        if by == "mtype":
            return self._segments_aggregated_by_mtype(segments, _total_volume)

        raise ValueError(
            "Unkown criterion to get segment volumes by: {}".format(by))


    @staticmethod
    def get_region_query(region_of_interest):
        """
        Get a dict to query `cells` in `region_of_interest`
        """
        corner_0, corner_1 = _get_bounding_box(region_of_interest)
        return {
            Cell.X: (corner_0[0], corner_1[0]),
            Cell.Y: (corner_0[1], corner_1[1]),
            Cell.Z: (corner_0[2], corner_1[2])}


    def get_synapse_density(self, region_of_interest, scale_factor=1.0):
        """
        Synapse density withing given region of interest.

        Arguments
        ----------
        region_of_interest:
            (bluepy.geometry.roi.ROI)
        Returns
        ---------
        synapse density within region of interest / volume
        [units: 1 / mm^3]

        Note
        -------
        When queried for synapse densities
        in a layer (roi in a single layer),
        this function will return all synapses,
        including synapses on / between cells
        whose soma-bodies fall in other layers
        (technically cells of other layers).
        We use this function to get synapse density of inhibitory synapses,
        which mostly  belong to cells in the same layer as the synapse.
        """
        corner_0, corner_1 = region_of_interest.bbox

        PRE_CENTERS =[
            Synapse.PRE_X_CENTER,
            Synapse.PRE_Y_CENTER,
            Synapse.PRE_Z_CENTER]
        POST_CENTERS =[
            Synapse.POST_X_CENTER,
            Synapse.POST_Y_CENTER,
            Synapse.POST_Z_CENTER]
        synapses = self\
            .connectome\
            .spatial_index\
            .q_window_oncenter(
                corner_0, corner_1)
        synapses_excitatory = synapses[synapses.excitatory == True]
        midpoints_excitatory = 0.5 * (
            synapses_excitatory[PRE_CENTERS].values +
            synapses_excitatory[POST_CENTERS].values)
        synapse_count_excitatory = numpy.count_nonzero(
            region_of_interest.contains(
                midpoints_excitatory))
        synapses_inhibitory = synapses[synapses.inhibitory == True]
        midpoints_inhibitory = 0.5 * (
            synapses_inhibitory[PRE_CENTERS].values +
            synapses_inhibitory[POST_CENTERS].values)
        synapse_count_inhibitory = numpy.count_nonzero(
            region_of_interest.contains(
                midpoints_inhibitory))
        synapse_count = pandas.Series({
            "EXC": synapse_count_excitatory,
            "INH": synapse_count_inhibitory,
            "TOT": synapse_count_excitatory + synapse_count_inhibitory})
        return 1.e9 * scale_factor * synapse_count / region_of_interest.volume

    def get_spine_density(self,
            region_of_interest,
            spine_density_per_unit_len=1.05,
            spine_density_per_unit_len_stdev=0.35):
        """..."""
        def _spine_count(dataframe):
            corner_1  = dataframe[[
                Segment.X1, Segment.Y1, Segment.Z1]
            ].values
            corner_2  = dataframe[[
                Segment.X2, Segment.Y2, Segment.Z2]
            ].values
            total_dendrite_length = numpy.sum(
                numpy.sqrt(numpy.sum(
                    (corner1 - corner2)**2,
                    axis=1)))
            spine_density_sample = np.random.normal(
                spine_density_per_unit_len,
                spine_density_per_unit_len_stdev)
            return spine_density_sample * total_dendrite_length

        segments = self.get_segments(region_of_interest)
        
        return _spine_count(segments[
            (segments[Section.NEURITE_TYPE] == nm.BASAL_DENDRITE)|
            (segments[Section.NEURITE_TYPE] == nm.APICAL_DENDRITE)])

    def get_spine_count_density(self,
            region_of_interest,
            queried_neurite_type=[
                nm.BASAL_DENDRITE,
                nm.APICAL_DENDRITE],
            spine_density_per_unit_len_mean=1.05,
            spine_density_per_unit_len_std=0.35,
            scale_factor=1.e0):
        """Density of number of spines per 1 mm^3 cube volume.
        Parameters
        -----------------------
        scale_factor :: Double #can be used to set a unit of counting.
        ~                      #eg: 1000 spines, or 10^9 spines..."""
        segment_lengths = self.get_segment_lengths(region_of_interest)
                
        total_segment_length = numpy.sum([
            segment_lengths[neurite_type]
            for neurite_type in queried_neurite_type])
        if not total_segment_length:
            return 0.

        def _random_spine_density():
            """return a random spine density"""
            return numpy.random.normal(
                spine_density_per_unit_len_mean,
                spine_density_per_unit_len_std)
        
        return\
            scale_factor * _random_spine_density() *\
            total_segment_length/(1.e-9 * region_of_interest.volume)
