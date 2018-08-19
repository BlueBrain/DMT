"""Brain models developed at the Blue Brain Project, EPFL."""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from bluepy.v2.circuit import Circuit
from bluepy.v2.enums import Cell, Synapse, Segment, Section
from bluepy.geometry.roi import ROI
import neurom as nm
import geometry


class BlueBrainModel(Circuit):
    """Brain circuit models developed at the Blue Brain Project (BBP) can be 
    studied with the bluepy API, also developed at the BBP. This class extends
    'bluepy.v2.circuit.Circuit'."""

    def __init__(self, *args, **kwargs):
        """initialize common stuff"""
        super(BlueBrainModel, self).__init__(*args, **kwargs)

    def geometric_bounds(self, cell_query, target=None):
        "Geometric bounds of this circuit, determined by a bounding box around
        the queried cells contained in this circuit within the specified
        'target'."
        def with_target(cell_query):
            if isinstance(target, str):
                cell_query['$target'] = target
            elif isinstance(target, Cell.HYPERCOLUMN):
                cell_query[Cell.HYPERCOLUMN] = target
            else:
                raise TypeError("Unhandled target type: {}"\
                                .format(type(target)))
            return cell_query

        return geometry.bounds(
            self.cells.position() if target is None \
            else self.cells.get(with_target(cell_query))
        )

    def collect_sample(self, measurement,
                       sampled_bbox_shape=np.array([25.0, 25.0, 25.0]),
                       sample_size=100,
                       region_to_explore=None,
                       cell_query=None,
                       target=None):
        """Collect samples of a measurement.

        Parameters
        ------------------------------------------------------------------------
        measurement :: FunctionType
        sampled_bbox_shape :: numpy.ndarray [x, y, z] #to create ROIs around sampled locations
        sample_size :: int
        region_to_explore :: regionfc-cache -f -v in the circuit to explore random locations in
        cell_query :: dict
        """
        if region_to_explore is None:
            if cell_query is None:
                raise Exception(
                    "Neither a region to explore, nor a cell query provided."
                )
            region_to_explore = self.geometric_bounds(cell_query, target)

        points = (geometry.sample_location(region_to_explore)
                  for i in range(sample_size))

        def sampled_bbox(center):
            """..."""
            half_box = sampled_bbox_shape / 2.0
            return Cuboid(center - half_box, center + half_box)

        ms = (measurement(self, sampled_bbox(center)) for center in points)

        return (m for m in ms if m is not None)

    def get_segments(self, roi):
        """Get segments in a region."""
        segidx = self.morph.spatial_index
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

    def __aggregated_by_mtype(self, df, agg_func):
        """Aggregated data-frame, by mtype."""
        cell_gids = df.gid.unique()
        mdf = df.set_index('gid')\
                .join(self.cells.get(cell_gids, [Cell.MTYPE]))
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
            return self.__aggregated_by_mtype(segdf, total_length)
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
            return self.__aggregated_by_mtype(segdf, total_volume)
        raise ValueError("Unknown criterion to get segment lengths by: {}"\
                         .format(by))

    def cell_gids_for_mtype(self, mtype, target=None):
        cells = (self.cells.get({'$target': target}, properties=[Cell.MTYPE])
                 if target else circuit.cells.get(properties=[Cell.MTYPE]))
        return np.array(cells.index[cells[Cell.MTYPE] == mtype].values)

    def cell_counts_by_mtype(self, roi):
        p0, p1 = roi.bbox
        q = {Cell.X: (p0[0], p1[0]),
             Cell.Y: (p0[1], p1[1]),
             Cell.Z: (p0[2], p1[2])}
        cells = self.cells.get(q, properties=[Cell.MTYPE])
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
        return pandas.DataFrame({
            'mtype': mtcts.index,
            'cell_density': 1.e9 * mtcts.values / roi.volume
        })

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

        segIdx = self.morph.spatial_index
        if not segIdx.exists(): return None

        p0, p1 = roi.bbox
        segmentDF  = segIdx.q_window_oncenter(p0, p1)
        dendriteDF = segmentDF[
            (segmentDF[Section.NEURITE_TYPE] == nm.BASAL_DENDRITE) |
            (segmentDF[Section.NEURITE_TYPE] == nm.APICAL_DENDRITE)
        ]

        return spine_count(dendriteDF)

    def spine_count_density(self, roi,
                            queried_spine_type=[nm.BASAL_DENDRITE,
                                                nm.APICAL_DENDRITE],
                            spine_density_per_unit_len_mean=1.05,
                            spine_density_per_unit_len_stdev=0.35):
        
        total_spine_length = segment_length(self, roi, queried_spine_type)
        
        randomSpineDensity = lambda: np.random.normal(
            spine_density_per_unit_len_mean,
            spine_density_per_unit_len_stdev
        )

        return (randomSpineDensity() * total_spine_length /roi.volume
                if total_spine_length
                else None)


    def soma_volume_fraction(self, roi):
        def contourWithSpines(cmorph):
            contour = cmorph.soma.points[:, 0:3]
            spines  = np.vstack([n.points[0][0:3] for n in cmorph.neurites])
            return np.vstack([contour, spines])

        def volume_estimate(gid):
            morph = self.morph.get(gid)
            try:
                return soma.estimate_convex_hull_volume( contourWithSpines(morph) )
            except Exception as e:
                return None

        #return soma.estimate_volume_assuming_sphere(morph.soma.points[:, 0:3])


        p0, p1 = roi.bbox
        gids = self.cells.ids({Cell.X: (p0[0], p1[0]),
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

