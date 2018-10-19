"""Brain models developed at the Blue Brain Project, EPFL."""
import sys
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import bluepy
from bluepy.v2.circuit import Circuit
from bluepy.v2.enums import Cell, Synapse, Segment, Section
from bluepy.geometry.roi import ROI
import neurom as nm
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.utils.logging import Logger, with_logging
from neuro_dmt.models.bluebrain.circuit import geometry, cell_collection



@with_logging(Logger.level.STUDY)
class BlueBrainModelHelper:
    """Brain circuit models developed at the Blue Brain Project (BBP) can be 
    studied with the bluepy API, also developed at the BBP. This class extends
    'bluepy.v2.circuit.Circuit'."""

    def __init__(self,
            *args, **kwargs):
        """initialize common stuff

        Keyword Arguments
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.circuit.Circuit #optional
        circuit_config :: str #path to a circuit
        ------------------------------------------------------------------------
        Provide one of circuit or circuit_config
        """
        self.logger.info(
            self.logger.get_source_info(),
            "initialize {} instance with kwargs:".format(self.__class__),
            *["key: {}, arg: {}\n".format(k, v) for k, v in kwargs.items()])
        
        self._circuit\
            = kwargs.get(
                'circuit',
                None)

        if self._circuit is None:
            circuit_config\
                = kwargs.get(
                    'circuit_config',
                    None)
            if circuit_config is None:
                raise RequiredKeywordArgumentError(
                    "Either circuit or circuit_config")
            self._circuit\
                = Circuit(circuit_config)
        self._cells\
            = self._circuit.cells
        try:
            self._conn\
                = self._circuit.connectome
        except bluepy.exceptions.BluePyError:
            sys.stderr.write(
                '\nWarning: circuit does not have connectome\n')
            self._conn\
                = None
        try:
            super().__init__(
                *args, **kwargs)
        except:
            pass

    def geometric_bounds(self,
            cell_query,
            target=None):
        """Geometric bounds of this circuit, determined by a bounding box around
        the queried cells contained in this circuit within the specified
        'target'."""
        def with_target(
                cell_query):
            if isinstance(target, str):
                cell_query['$target'] = target
            elif isinstance(target, int):
                cell_query[Cell.HYPERCOLUMN]\
                    = target
            else:
                if target is not None:
                    raise TypeError(
                        "Unhandled target type: {}"\
                        .format(type(target)))
            return cell_query

        cell_positions\
            = self._cells.positions(
                with_target(
                    cell_query))
        if cell_positions.shape[0] > 0: 
            return cell_collection.bounds(
                cell_positions)
        return None

    def get_segments(self,
            roi):
        """Get segments in a region."""
        segidx\
            = self._circuit.morph.spatial_index
        if not segidx:
            raise ValueError(
                "No spatial index for this circuit!")
        corner0, corner1\
            = roi.bbox if isinstance(roi, ROI) else roi
        return segidx.q_window_oncenter(
            corner0,
            corner1)

    def region_dendrite_length(self,
            roi):
        """Total dendrite length in a region of interest.

        Parameters
        ------------------------------------------------------------------------
        roi :: bluepy.geometry.ROI or tuple(np.ndrray, np.ndarray)
        """
        segdf\
            = self.get_segments(
                roi)

        dendf\
            = segdf[
                (segdf[Section.NEURITE_TYPE] == nm.BASAL_DENDRITE) |
                (segdf[Section.NEURITE_TYPE] == nm.APICAL_DENDRITE)]

        position1\
            = dendf[
                [Segment.X1, Segment.Y1, Segment.Z1]]\
                .values
        position2\
            = dendf[
                [Segment.X2, Segment.Y2, Segment.Z2]]\
                .values
        return np.sum(
            np.sqrt(
                np.sum(
                    (position1 - position2)**2,
                    axis=1) ) )

    def _aggregated_by_mtype(self,
            dataframe,
            agg_function):
        """Aggregated data-frame, by mtype."""
        cell_gids\
            = dataframe.gid\
                       .unique()
        mtype_dataframe\
            = dataframe.set_index('gid')\
                .join(
                    self._cells.get(
                        cell_gids,
                        properties=[Cell.MTYPE]))
        grouped_by_mtype\
            = mtype_dataframe.groupby(
                u'mtype')
        mtypes\
            = mtype_dataframe.mtype\
                             .unique()
        def get_group_segments(mtype):
            """..."""
            group_dataframe\
                = grouped_by_mtype.get_group(
                    mtype)
            return {'mtype': mtype,
                    nm.AXON: agg_function(
                        group_dataframe,
                        nm.AXON),
                    nm.BASAL_DENDRITE: agg_function(
                        group_dataframe,
                        nm.BASAL_DENDRITE),
                    nm.APICAL_DENDRITE: agg_function(
                        group_dataframe,
                        nm.APICAL_DENDRITE)}
        
        return pd.DataFrame([
            get_group_segments(m) for m in mtypes])

    def segment_lengths(self,
            region_of_interest,
            by=None):
        """Segment length in a region of interest,
        either total, or as a dict.

        Parameters
        ------------------------------------------------------------------------
        roi :: bluepy.geometry.ROI or tuple(np.ndarray, np.ndarray)
        """
        segment_dataframe\
            = self.get_segments(
                region_of_interest)
        position1\
            = segment_dataframe[[
                Segment.X1,
                Segment.Y1,
                Segment.Z1]]\
                .values
        position2\
            = segment_dataframe[[
                Segment.X2,
                Segment.Y2,
                Segment.Z2]]\
                .values
        segment_dataframe['length']\
            = np.sqrt(
                np.sum(
                    (position1 - position2)**2,
                    axis = 1) )

        def total_length(
                segment_dataframe,
                neurite_type):
            """total length of segments of neurite_type 'nt'"""
            return np.sum(
                segment_dataframe.length[
                    segment_dataframe[
                        Section.NEURITE_TYPE] == neurite_type]\
                .values)
                
        if by is None:
            return pd.Series({
                neurite_type: total_length(
                    segment_dataframe,
                    neurite_type)
                for neurite_type in (nm.AXON,
                           nm.BASAL_DENDRITE,
                           nm.APICAL_DENDRITE)})
        if by == 'mtype':
            return self._aggregated_by_mtype(
                segment_dataframe,
                total_length)
        raise ValueError(
            "Unknown criterion to get segment lengths by: {}"\
            .format(by))

    def segment_volumes(self,
            region_of_interest,
            by=None):
        """segment volume fraction in a region."""
        segment_dataframe\
            = self.get_segments(
                region_of_interest)
        position1\
            = segment_dataframe[[
                Segment.X1,
                Segment.Y1,
                Segment.Z1]]\
                .values
        position2\
            = segment_dataframe[[
                Segment.X2,
                Segment.Y2,
                Segment.Z2]]\
                .values
        segment_dataframe['length']\
            = np.sqrt(
                np.sum(
                    (position1 - position2)**2,
                    axis = 1) )
        rs\
            = segment_dataframe[[
                Segment.R1, Segment.R2]]\
                .values
        segment_dataframe['radius']\
            = np.mean(
                rs,
                axis=1)
        segment_dataframe['volume']\
            = (np.pi *
               (segment_dataframe.radius ** 2) *
               (segment_dataframe.length) )

        def total_volume(
                segment_dataframe,
                neurite_type):
            """Total volume of neuite type nt."""
            return np.sum(
                segment_dataframe.volume[
                    segment_dataframe[
                        Section.NEURITE_TYPE]==nt]\
                .values)

        if by is None:
            return pd.Series({
                neurite_type: total_volume(neurite_type)
                for neurite_type in (nm.AXON,
                                     nm.BASAL_DENDRITE,
                                     nm.APICAL_DENDRITE)})
        if by == 'mtype':
            return self._aggregated_by_mtype(
                segment_dataframe,
                total_volume)
        raise ValueError(
            "Unknown criterion to get segment lengths by: {}"\
            .format(by))

    def target_cells(self,
            target=None):
        """GIDs of cells in a target."""
        cells\
            = (self._cells.get({"$target": target})
               if target else 
               self._cells.get())
        return set(
            cells.index)

    def cell_mtypes(self,
            target=None):
        """mtypes of cells."""
        properties\
            = [Cell.MTYPE]
        return(
            self._cells.get(
                properties=properties)
            if target is None else
            self._cells.get(
                {"$target": target},
                properties=properties))

    def cell_gids_for_mtype(self,
            mtype,
            target="mc2_Column"):
        mtypes\
            = self.cell_mtypes(
                target=target)
        return np.array(
            mtypes.index[
                mtypes[Cell.MTYPE] == mtype]\
            .values)

    def cells_in_region(self,
            region_of_interest,
            properties=[]):
        """..."""
        corner0, corner1\
            = region_of_interest.bbox
        query\
            = {Cell.X: (corner0[0], corner1[0]),
               Cell.Y: (corner0[1], corner1[1]),
               Cell.Z: (corner0[2], corner1[2])}
        cells\
            = self._cells.get(
                query,
                [Cell.X, Cell.Y, Cell.Z] + properties)
        return cells[
            region_of_interest.contains(
                self.__xyz(
                    cells))]

    @staticmethod
    def __xyz(df):
        """..."""
        return df[[
            Cell.X,
            Cell.Y,
            Cell.Z]]\
            .values

    def cell_counts(self,
                    region_of_interest,
                    by_property=None,#if None count all cells
                    for_given_type=)
    def cell_counts(self,
            region_of_interest,
            by_cell_property=None,#if None count all cells
            for_given_cell_type={},#empty dict will count all cells, not a subset
            *args, **kwargs):
        """..."""
        if by_cell_property in for_given_cell_type:
            raise TypeError(
                """Property to count cells by also given a required value!
                \n\t'by_cell_property' {} appears in 'for_given_cell_type'"""\
                .format(by_cell_property))
        properties\
            = list(
                for_given_cell_type.keys())
        if by_cell_property:
            properties.append(by_cell_property)
        cells\
            = self.cells_in_region(
                region_of_interest,
                properties=properties)
        for _property, value in for_given_cell_type.items():
            cells\
                = cells[
                    cells[_property] == value]
        if not by_cell_property:
            return cells.shape[0]
        return cells[
            by_cell_property]\
            .value_counts()
        
    def __cell_counts_by_property(self,
            region_of_interest,
            _property):
        """..."""
        properties\
            = [] if not _property else [_property]
        cells\
            = self.cells_in_region(
                region_of_interest,
                properties=properties)
        if not _property:
            return np.count_nonzero(
                roi.contains(
                    self.__xyz(
                        cells)))
        property_values\
            = cells[
                _property]\
                .unique()
        data_series\
            = pd.Series({
                prop: np.count_nonzero(
                    region_of_interest.contains(
                        self.__xyz(
                            cells[
                                cells[_property] == prop])))
                for prop in property_values})
        data_series["TOT"]\
            = data_series.sum()
        return data_series

    def cell_counts_by_cell_type(self,
            region_of_interest):
        """Counts of inhibitory and excitatory cells, in a region of interest,
        as a pandas Series."""
        return self.cell_counts(
            region_of_interest,
            _property=Cell.SYNAPSE_CLASS)

    def cell_counts_by_synapse_class(self,
            region_of_interest):
        """alias..."""
        return self.cell_counts(
            region_of_interest,
            _property=Cell.SYNAPSE_CLASS)

    def cell_counts_by_morph_class(self,
            region_of_interest):
        """Counts of inhibitory and excitatory cells, in a region of interest,
        as a pandas Series."""
        return self.cell_counts(
            region_of_interest,
            _property=Cell.MORPH_CLASS)

    def cell_counts_by_mtype(self,
            region_of_interest):
        """..."""
        return self.cell_counts(
            region_of_interest,
            _property=Cell.MTYPE)

    def cell_counts_by_morphology(self,
            region_of_interest):
        mtype_counts\
            = self.cell_counts_by_mtype(
                region_of_interest)
        dataframe\
            = pd.DataFrame({
                'mtype': mtcounts.index,
                'count': mtcounts.values})
        dataframe['morphology']\
            = [mtype.split('_')[1]
               for mtype in dataframe.mtype]
        return dataframe\
            .groupby(
                'morphology')\
            .sum()

    def cell_densities_by_mtype(self,
            region_of_interest):
        mtype_counts\
            = self.cell_counts_by_mtype(
                region_of_interest)
        cell_density\
            = 1.e9 * mtype_counts.values / region_of_interest.volume 
        return pd.DataFrame({
            'mtype': mtype_counts.index,
            'cell_density': cell_density})

    def synapse_density(self,
            region_of_interest,
            scale_factor=1.0):
        """
        Synapse density withing given region of interest.
        roi :: region of interest (bluepy.geometry.roi.ROI)

        @return :: synapse density within region of interest / volume
        [units: 1 / mm^3]

        @note: When queried for synapse densities
        in a layer (roi in a single layer),
        this function will return all synapses,
        including synapses on / between cells
        whose soma-bodies fall in other layers
        (technically cells of other layers).
        We use this function to get synapse density of inhibitory synapses,
        which mostly  belong to cells in the same layer as the synapse.
        """
        corner0, corner1\
            = region_of_interest.bbox
        synapses\
            = self._circuit.connectome\
                           .spatial_index\
                           .q_window_oncenter(
                               corner0,
                               corner1)
        synapses_excitatory\
            = synapses[
                synapses.excitatory == True]
        synapses_inhibitory\
            = synapses[
                synapses.excitatory == False]
        midpoints_excitatory\
            = 0.5 * (
                synapses_excitatory[[
                    Synapse.PRE_X_CENTER,
                    Synapse.PRE_Y_CENTER,
                    Synapse.PRE_Z_CENTER]]\
                .values
                +
                synapses_excitatory[[
                    Synapse.POST_X_CENTER,
                    Synapse.POST_Y_CENTER,
                    Synapse.POST_Z_CENTER]]\
                .values)
        midpoints_inhibitory\
            = 0.5 * (
                synapses_inhibitory[[
                    Synapse.PRE_X_CENTER,
                    Synapse.PRE_Y_CENTER,
                    Synapse.PRE_Z_CENTER]]\
                .values
                +
                synapses_inhibitory[[
                    Synapse.POST_X_CENTER,
                    Synapse.POST_Y_CENTER,
                    Synapse.POST_Z_CENTER]]\
                .values)
        synapse_count_excitatory\
            = np.count_nonzero(
                region_of_interest.contains(
                    midpoints_excitatory))
        synapse_count_inhibitory\
            = np.count_nonzero(
                region_of_interest.contains(
                    midpoints_inhibitory))
        synapse_count = pd.Series({
            "EXC": synapse_count_excitatory,
            "INH": synapse_count_inhibitory,
            "TOT": synapse_count_inhibitory + synapse_count_excitatory
        })
        return(
            1.e9 * scale_factor *
            synapse_count /
            region_of_interest.volume())

    def marker_stains(self,
            region_of_interest,
            gtype_dataframe):
        mtype_counts\
            = self.cell_counts_by_morphology(region_of_interest)\
                  .loc[gtype_dataframe.keys()]\
                  .fillna(0.0)
        marker_stain_dataframe\
            = pd.DataFrame({
                mtype: gtypes.iloc[[
                    np.random.randint(gtypes.shape[0])
                    for i in range(mtype_counts.loc[mtype])]]\
                .sum(axis=0)
                for mtype, gtypes in gtype_dataframe.iteritems()})\
            .sum(axis=1)
        return pd.DataFrame({
            'gtype': marker_stain_dataframe.index,
            'stain': (1.e9 *
                      marker_stain_dataframe.values /
                      region_of_interest.volume) })

    def spine_density(self,
            region_of_interest,
            spine_density_per_unit_len=1.05,
            spine_density_per_unit_len_stdev=0.35):
        """..."""
        def spine_count(
                dataframe):
            corner1\
                = dataframe[[
                    Segment.X1,
                    Segment.Y1,
                    Segment.Z1]]\
                    .values
            corner2\
                = dataframe[[
                    Segment.X2,
                    Segment.Y2,
                    Segment.Z2]]\
                    .values
            total_dendrite_length\
                = np.sum(
                    np.sqrt(
                        np.sum(
                            (corner1 - corner2)**2,
                            axis=1) ) )
            spine_density_sample\
                = np.random.normal(
                    spine_density_per_unit_len,
                    spine_density_per_unit_len_stdev)
            return spine_density_sample * total_dendrite_length

        segments\
            = self.get_segments(
                region_of_interest)
        dendrites\
            = segments[
                (segments[Section.NEURITE_TYPE] == nm.BASAL_DENDRITE)|
                (segments[Section.NEURITE_TYPE] == nm.APICAL_DENDRITE)]
        return spine_count(dendrites)

    def spine_count_density(self,
            region_of_interest,
            queried_spine_type=[
                nm.BASAL_DENDRITE,
                nm.APICAL_DENDRITE],
            spine_density_per_unit_len_mean=1.05,
            spine_density_per_unit_len_std=0.35):
        """..."""
        segment_lengths\
            = self.segment_lengths(region_of_interest)
        total_spine_length\
            = np.sum([
                segment_lengths[neurite_type]
                for neurite_type in queried_spine_type])
        
        def random_spine_density():
            """return a random spine density"""
            return np.random.normal(
                spine_density_per_unit_len_mean,
                spine_density_per_unit_len_std)

        return(
            random_spine_density() * total_spine_length / roi.volume
            if total_spine_length else None)

    def soma_volume_fraction(self,
            region_of_interest):
        def contour_with_spines(
                cmorph):
            contour\
                = cmorph.soma.points[:, 0:3]
            spines\
                = np.vstack([
                    n.points[0][0:3] for n in cmorph.neurites])
            return np.vstack([
                contour,
                spines])

        def volume_estimate(gid):
            morph = self._circuit.morph.get(gid)
            try:
                return soma.estimate_convex_hull_volume(
                    contour_with_spines(morph))
            except Exception as e:
                return None

        #return soma.estimate_volume_assuming_sphere(morph.soma.points[:, 0:3])


        corner0, corner1 = roi.bbox
        gids = self._cells.ids({
            Cell.X: (corner0[0], corner1[0]),
            Cell.Y: (corner0[1], corner1[1]),
            Cell.Z: (corner0[2], corner1[2])})
        print(
            "for soma volume fraction, obtained ",
            len(gids),
            " neuron ids in ROI")
        #soma_volumes = [soma.estimate_convex_hull_volume(c) for c in envelop]
        #soma_volumes = [soma.estimate_volume_assuming_sphere(c) for c in contours]

        soma_volumes = [volume_estimate(gid) for gid in gids]

        #total_volume = np.sum(volume_estimate(gid) for gid in gids)
        #return total_volume / roi.volume
        nvalid = np.sum([1.0 for v in soma_volumes if v])
        ntotal = 1. * len(soma_volumes)

        if nvalid != ntotal:
            print(
                "Soma volume estimate.",
                "Number of cells for which volume calculation failed",
                ntotal - nvalid,
                " out of ", ntotal, " total cells.")
            print(
                "total volumes obtained ", ntotal,
                " with number valid ", nvalid)

            f = ((ntotal + 1.0)/ (nvalid + 1.0))
            vol_frac = (f * np.sum([v for v in soma_volumes if v]) / roi.volume)
            print("soma volume fraction for the roi: ", vol_frac)

        return volume_fraction
