"""Brain models developed at the Blue Brain Project, EPFL."""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from bluepy.v2.circuit import Circuit
from bluepy.v2.enums import Cell, Synapse, Segment, Section
from bluepy.geometry.roi import ROI
import neurom as nm
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from neuro_dmt.models.bluebrain.circuit import geometry, cell_collection



class BlueBrainModelHelper:
    """Brain circuit models developed at the Blue Brain Project (BBP) can be 
    studied with the bluepy API, also developed at the BBP. This class extends
    'bluepy.v2.circuit.Circuit'."""

    def __init__(self, *args, **kwargs):
        """initialize common stuff

        Keyword Arguments
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.circuit.Circuit #optional
        circuit_config :: str #path to a circuit
        ------------------------------------------------------------------------
        Provide one of circuit or circuit_config
        """
        self._circuit = kwargs.get('circuit', None)

        if self._circuit is None:
            circuit_config = kwargs.get('circuit_config', None)
            if circuit_config is None:
                raise RequiredKeywordArgumentError(
                    "Either circuit or circuit_config"
                )
            self._circuit = Circuit(circuit_config)

        self._cell_mtypes = None #initialize when first called

        try:
            super(BlueBrainModelHelper, self).__init__(*args, **kwargs)
        except:
            pass

    def geometric_bounds(self, cell_query, target=None):
        """Geometric bounds of this circuit, determined by a bounding box around
        the queried cells contained in this circuit within the specified
        'target'."""
        def with_target(cell_query):
            if isinstance(target, str):
                cell_query['$target'] = target
            elif isinstance(target, int):
                cell_query[Cell.HYPERCOLUMN] = target
            else:
                if target is not None:
                    raise TypeError("Unhandled target type: {}"\
                                    .format(type(target)))
            return cell_query

        cell_positions = self._circuit.cells.positions(with_target(cell_query))
        return cell_collection.bounds(cell_positions)

    def get_segments(self, roi):
        """Get segments in a region."""
        segidx = self._circuit.morph.spatial_index
        if not segidx:
            raise ValueError("No spatial index for this circuit!")
        p0, p1 = roi.bbox if isinstance(roi, ROI) else roi
        return segidx.q_window_oncenter(p0, p1)

    def region_dendrite_length(self, roi):
        """Total dendrite length in a region of interest.

        Parameters
        ------------------------------------------------------------------------
        roi :: bluepy.geometry.ROI or tuple(np.ndrray, np.ndarray)
        """
        segdf = self.get_segments(roi)

        dendf = segdf[(segdf[Section.NEURITE_TYPE] == nm.BASAL_DENDRITE) |
                      (segdf[Section.NEURITE_TYPE] == nm.APICAL_DENDRITE)]

        pos1 = dendf[[Segment.X1, Segment.Y1, Segment.Z1]].values
        pos2 = dendf[[Segment.X2, Segment.Y2, Segment.Z2]].values
        return np.sum( np.sqrt( np.sum((pos1 - pos2)**2, axis=1) ) )

    def _aggregated_by_mtype(self, df, agg_func):
        """Aggregated data-frame, by mtype."""
        cell_gids = df.gid.unique()
        mdf = df.set_index('gid')\
                .join(self._circuit.cells.get(cell_gids, [Cell.MTYPE]))
        grouped_by_mtype = mdf.groupby(u'mtype')
        mtypes = mdf.mtype.unique()

        def get_group_segments(m):
            """..."""
            group_df = grouped_by_mtype.get_group(m)
            return {'mtype': m,
                    nm.AXON: agg_func(group_df, nm.AXON),
                    nm.BASAL_DENDRITE: agg_func(group_df, nm.BASAL_DENDRITE),
                    nm.APICAL_DENDRITE: agg_func(group_df, nm.APICAL_DENDRITE)}
        
        return pd.DataFrame([get_group_segments(m) for m in mtypes])

    def segment_lengths(self, roi, by=None):
        """Segment length in a region of interest,
        either total, or as a dict.

        Parameters
        ------------------------------------------------------------------------
        roi :: bluepy.geometry.ROI or tuple(np.ndarray, np.ndarray)
        """
        segdf = self.get_segments(roi)
        pos1 = segdf[[Segment.X1, Segment.Y1, Segment.Z1]].values
        pos2 = segdf[[Segment.X2, Segment.Y2, Segment.Z2]].values
        segdf['length'] = np.sqrt( np.sum( (pos1 - pos2)**2, axis = 1) )

        def total_length(sdf, nt):
            """total length of segments of neurite_type 'nt'"""
            return np.sum(sdf.length[sdf[Section.NEURITE_TYPE] == nt].values)
                
        if by is None:
            return pd.Series({nt: total_length(segdf, nt)
                              for nt in (nm.AXON,
                                         nm.BASAL_DENDRITE,
                                         nm.APICAL_DENDRITE)})
        if by == 'mtype':
            return self._aggregated_by_mtype(segdf, total_length)
        raise ValueError("Unknown criterion to get segment lengths by: {}"\
                         .format(by))

    def segment_volumes(self, roi, by=None):
        """segment volume fraction in a region."""
        segdf = self.get_segments(roi)

        pos1 = segdf[[Segment.X1, Segment.Y1, Segment.Z1]].values
        pos2 = segdf[[Segment.X2, Segment.Y2, Segment.Z2]].values
        segdf['length'] = np.sqrt( np.sum( (pos1 - pos2)**2, axis = 1) )
        rs = segdf[[Segment.R1, Segment.R2]].values
        segdf['radius'] = np.mean(rs, axis=1)
        segdf['volume'] = np.pi * (segdf.radius ** 2) * (segdf.length)

        def total_volume(sdf, nt):
            """Total volume of neuite type nt."""
            return np.sum(sdf.volume[sdf[Section.NEURITE_TYPE]==nt].values)

        if by is None:
            return pd.Series({nt: total_volume(nt)
                              for nt in (nm.AXON,
                                         nm.BASAL_DENDRITE,
                                         nm.APICAL_DENDRITE)})
        if by == 'mtype':
            return self._aggregated_by_mtype(segdf, total_volume)
        raise ValueError("Unknown criterion to get segment lengths by: {}"\
                         .format(by))

    @property
    def cell_mtypes(self):
        """mtypes of cells."""
        if not self._cell_mtypes:
            self._cell_mtypes \
                =  self._circuit.cells.get(properties=[Cell.MTYPE])
        return self._cell_mtypes

    def cell_gids_for_mtype(self, mtype):
        return np.array(self.cell_mtypes.index[
            self.cell_mtypes[Cell.MTYPE] == mtype
        ].values)

    def cell_counts_by_cell_type(self, roi):
        """Counts of inhibitory and excitatory cells, in a region of interest,
        as a pandas Series."""
        p0, p1 = roi.bbox
        query = {Cell.X: (p0[0], p1[0]),
                 Cell.Y: (p0[1], p1[1]),
                 Cell.Z: (p0[2], p1[2])}
        props = [Cell.X, Cell.Y, Cell.Z, Cell.SYNAPSE_CLASS]
        cells = self._circuit.cells.get(query, props)
        cells_inh = cells[cells.synapse_class == "INH"]
        cells_exc = cells[cells.synapse_class == "EXC"]

        inh_in_roi = roi.contains(cells_inh[[Cell.X, Cell.Y, Cell.Z]].values)
        roi_inh_count = np.count_nonzero(inh_in_roi)

        exc_in_roi = roi.contains(cells_exc[[Cell.X, Cell.Y, Cell.Z]].values)
        roi_exc_count = np.count_nonzero(exc_in_roi)

        return pd.Series({"INH": roi_inh_count,
                          "EXC": roi_exc_count,
                          "TOT": roi_exc_count + roi_inh_count})

    def cell_counts(self, roi):
        """Alias, for compatibility. Remember to remove..."""
        return self.cell_counts_by_cell_type(roi)

    def cell_counts_by_mtype(self, roi):
        p0, p1 = roi.bbox
        q = {Cell.X: (p0[0], p1[0]),
             Cell.Y: (p0[1], p1[1]),
             Cell.Z: (p0[2], p1[2])}
        cells = self._circuit.cells.get(q, properties=[Cell.MTYPE])
        return cells.mtype.value_counts()

    def cell_counts_by_morphology(self, roi):
        mtcounts = self.cell_counts_by_mtype(roi)
        df = pandas.DataFrame({
            'mtype': mtcounts.index,
            'count': mtcounts.values
        })
        df['morphology'] = [mtype.split('_')[1] for mtype in df.mtype]
        return df.groupby('morphology').sum()

    def cell_densities_by_mtype(self, roi):
        mtcts = self.cell_counts_by_mtype(roi)
        return pd.DataFrame({
            'mtype': mtcts.index,
            'cell_density': 1.e9 * mtcts.values / roi.volume
        })

    def synapse_density(self, roi, scale_factor=1.0):
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
        p0, p1 = roi.bbox
        synapses = self._circuit.connectome\
                                .spatial_index.q_window_oncenter(p0, p1)
        synapses_exc = synapses[synapses.excitatory == True]
        synapses_inh = synapses[synapses.excitatory == False]
        midpoints_exc = 0.5 * (synapses_exc[[Synapse.PRE_X_CENTER,
                                             Synapse.PRE_Y_CENTER,
                                             Synapse.PRE_Z_CENTER]].values +
                               synapses_exc[[Synapse.POST_X_CENTER,
                                             Synapse.POST_Y_CENTER,
                                             Synapse.POST_Z_CENTER]].values)
        midpoints_inh = 0.5 * (synapses_inh[[Synapse.PRE_X_CENTER,
                                             Synapse.PRE_Y_CENTER,
                                             Synapse.PRE_Z_CENTER]].values +
                               synapses_inh[[Synapse.POST_X_CENTER,
                                             Synapse.POST_Y_CENTER,
                                             Synapse.POST_Z_CENTER]].values)
        syn_count_exc = np.count_nonzero(roi.contains(midpoints_exc))
        syn_count_inh = np.count_nonzero(roi.contains(midpoints_inh))
        synapse_count = pd.Series({
            "EXC": syn_count_exc,
            "INH": syn_count_inh,
            "TOT": syn_count_inh + syn_count_exc
        })
        return scale_factor * 1.e9 * synapse_count / roi.volume

    def marker_stains(self, roi, gtypes):
        mtcounts = self.cell_counts_by_morphology(roi)\
                       .loc[gtypes.keys()].fillna(0.0)
        ms = pandas.DataFrame({
            mt: gts.iloc[
                [np.random.randint(gts.shape[0])
                 for i in range(mtcounts.loc[mt])]
            ].sum(axis=0)
            for mt, gts in gtypes.iteritems()
        }).sum(axis=1)

        return pandas.DataFrame({
            'gtype': ms.index,
            'stain': 1.e9 * ms.values / roi.volume
        })

    def spine_density(self, roi,
                      spine_density_per_unit_len=1.05,
                      spine_density_per_unit_len_stdev=0.35):

        def spine_count(dataframe):
            p1 = dataframe[[Segment.X1, Segment.Y1, Segment.Z1]].values
            p2 = dataframe[[Segment.X2, Segment.Y2, Segment.Z2]].values
            total_dendrite_length = np.sum( np.sqrt( np.sum((p1 - p2)**2,
                                                            axis=1) ) )
            sd = np.random.normal(spine_density_per_unit_len,
                                  spine_density_per_unit_len_stdev)
            return sd * total_dendrite_length

        segdf = self.get_segments(roi)
        dendf = segdf[(segdf[Section.NEURITE_TYPE] == nm.BASAL_DENDRITE) |
                      (segdf[Section.NEURITE_TYPE] == nm.APICAL_DENDRITE)]
        return spine_count(dendf)

    def spine_count_density(self, roi,
                            queried_spine_type=[nm.BASAL_DENDRITE,
                                                nm.APICAL_DENDRITE],
                            spine_density_per_unit_len_mean=1.05,
                            spine_density_per_unit_len_std=0.35):
        
        seg_lens = self.segment_lengths(roi)
        total_spine_length = np.sum([seg_lens[nt] for nt in queried_spine_type])
        
        def random_spine_density():
            """return a random spine density"""
            return np.random.normal(spine_density_per_unit_len_mean,
                                    spine_density_per_unit_len_std)

        return (random_spine_density() * total_spine_length /roi.volume
                if total_spine_length else None)


    def soma_volume_fraction(self, roi):
        def contourWithSpines(cmorph):
            contour = cmorph.soma.points[:, 0:3]
            spines  = np.vstack([n.points[0][0:3] for n in cmorph.neurites])
            return np.vstack([contour, spines])

        def volume_estimate(gid):
            morph = self._circuit.morph.get(gid)
            try:
                return soma.estimate_convex_hull_volume( contourWithSpines(morph))
            except Exception as e:
                return None

        #return soma.estimate_volume_assuming_sphere(morph.soma.points[:, 0:3])


        p0, p1 = roi.bbox
        gids = self._circuit.cells.ids({Cell.X: (p0[0], p1[0]),
                                  Cell.Y: (p0[1], p1[1]),
                                  Cell.Z: (p0[2], p1[2])})
        print("for soma volume fraction, obtained ", len(gids), " neuron ids in ROI")
        #soma_volumes = [soma.estimate_convex_hull_volume(c) for c in envelop]
        #soma_volumes = [soma.estimate_volume_assuming_sphere(c) for c in contours]

        soma_volumes = [volume_estimate(gid) for gid in gids]

        #total_volume = np.sum(volume_estimate(gid) for gid in gids)
        #return total_volume / roi.volume
        nvalid = np.sum([1.0 for v in soma_volumes if v])
        ntotal = 1. * len(soma_volumes)

        if nvalid != ntotal:
            print("Soma volume estimate.",
                  "Number of cells for which volume calculation failed",
                  ntotal - nvalid,
                  " out of ", ntotal, " total cells.")
            print("total volumes obtained ", ntotal,
                  " with number valid ", nvalid)

            f = ((ntotal + 1.0)/ (nvalid + 1.0))
            vol_frac = (f * np.sum([v for v in soma_volumes if v]) / roi.volume)
            print("soma volume fraction for the roi: ", vol_frac)

        return volume_fraction

