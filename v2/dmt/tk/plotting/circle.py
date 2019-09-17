import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from collections import OrderedDict
from dmt.tk.enum import DATA_KEYS, MEAN
from dmt.tk.data import multilevel_dataframe
from dmt.tk.plotting.utils import pivot_table, default_group_label
from dmt.tk.plotting import golden_figure


# TODO: test that rotation works
class CircleTool:
    """a helper for drawing circles, circle segments, and arcs"""

    def __init__(self, radius, center=None, rotation=0):
        """
        initialize a circle with radius and center on the plot

        Arguments:
            radius: float, the radius of the circle
            center: np.array (shp (2,)), center of the circle
            rotation: float, rotation of the circle in radians
                      0 (default) means that angle 0 points along y-axis
        """
        if center is None:
            center = np.zeros((2,))
        self.center = center
        self.radius = radius
        self.rot = rotation

    def angles_to_points(self, angles):
        """
        get the coordinates on the circle at angle(s)

        Arguments:
            angles: number or array{number}. The angle(s) for which to get
                    the points, in radians

        Returns:
            positions: (2,) or (N, 2) array of x and y coordinates at angle(s)
        """

        angles = np.array(angles) + self.rot
        xes = np.sin(angles) * self.radius + self.center[0]
        yes = np.cos(angles) * self.radius + self.center[1]
        if angles.shape == ():
            return np.array([xes, yes])
        return np.array([xes, yes]).transpose()

    def segment_points(self, from_angle, to_angle, N=50):
        """
        get N points along the circle between from_angle and to_angle

        Arguments:
           from_angle: number, start angle in radians
           to_angle: number, end angle in radians
           N: integer, number of points to get

        Returns:
            (N, 2) array of x and y positions on the circle
        """
        return self.angles_to_points(np.linspace(from_angle, to_angle, N))

    def circle_points(self, N=100):
        """
        get N points around the full circle
        """
        return self.segment_points(0, 2 * np.pi, N=N)

    def _arc_circle(self, from_angle, to_angle):
        """
        get a circle which intersects the two points on the current circle

        Arguments:
            from_angle: first intersection angle in radians
            to_angle: second intersection angle in radians

        Returns:
            a CircleTool which intersects the first point at its own '0' angle
            the angle in the returned circle where it intersects at to_angle
        """
        mn_ngl = (from_angle + to_angle) / 2
        off_ngl = mn_ngl - np.minimum(from_angle, to_angle)
        ctr_ngl = np.pi - 2 * off_ngl
        rot_ngl = np.pi / 2 - np.minimum(from_angle, to_angle)
        L = self.radius / np.cos(off_ngl)
        Lp = self.radius * np.tan(off_ngl)
        c = np.array([np.sin(mn_ngl + self.rot) * L,
                      np.cos(mn_ngl + self.rot) * L]) + self.center
        if from_angle < to_angle:
            return CircleTool(Lp, center=c,
                              rotation=self.rot-rot_ngl), -ctr_ngl
        return CircleTool(Lp, center=c,
                          rotation=self.rot-rot_ngl-ctr_ngl), ctr_ngl

    def curve_points(self, from_angle, to_angle, N=100):
        """
        get N points representing a curve from from_angle on the circle
        to to_angle on the circle

        Arguments:
            from_angle: the source angle in radians
            to_angle: the target angle in radians
            N: the number of points to represent the curve with

        Returns:
            (N, 2) array of points
        """
        if np.isclose(np.abs(from_angle - to_angle), np.pi):
            start = self.angles_to_points(from_angle)
            end = self.angles_to_points(to_angle)
            xspace = np.linspace(start[0], end[0], N)
            yspace = np.linspace(start[1], end[1], N)
            return np.array([xspace, yspace]).transpose()

        a, ngl = self._arc_circle(from_angle, to_angle)
        return a.segment_points(0, ngl, N=N)

    def draw(self, N=100, *args, **kwargs):
        """draw the full circle"""
        from matplotlib import pyplot as plt
        pts = self.circle_points(N=N)
        plt.plot(pts[:, 0], pts[:, 1], *args, **kwargs)

    def curve_polygon(self, from_angle1, from_angle2, to_angle1, to_angle2,
                      **kwargs):
        """
        generate a matplotlib polygon of a curved path connecting two
        segments on the circle.

        (All angles in radians)

        Arguments:
            from_angle1: start angle of first curve, start of first segment
            from_angle2: start angle of second curve, end of first segment
            to_angle1: end angle of first curve, end of second segment
            to_angle2: end angle of second curve, start of second segment

        Returns:
            a Polygon enclosed by the curves and segments
        """

        xy = np.concatenate(
            [self.curve_points(from_angle1, to_angle1),
             self.segment_points(to_angle1, to_angle2),
             self.curve_points(to_angle2, from_angle2),
             self.segment_points(from_angle2, from_angle1)])
        return matplotlib.patches.Polygon(xy, closed=False, **kwargs)

    def segment_polygon(self, from_angle, to_angle, width, **kwargs):
        """
        generate a matplotlib polygon representing a segment on the circle

        Arguments:
           from_angle: start angle of the segment, in radians
           to_angle: end angle of the segment, in radians
           width: the width of the polygon

        returns:
           a Polygon representing a ring segment
        """
        outer = CircleTool(self.radius + width)
        xy = np.concatenate(
            [self.segment_points(from_angle, to_angle),
             outer.segment_points(to_angle, from_angle)])
        return matplotlib.patches.Polygon(xy, closed=True, **kwargs)


class CirclePlot:
    """
    a plotter for circle-plots. CirclePlots consist of circle segments
    connected by curves, the thickness of which corresponds to the weight
    of the connection
    """
    def __init__(self, space_between=0.0, value_callback=default_group_label):
        """
        Arguments:
           space_between : the space to leave between segments, in radians
        """
        if space_between < 0 or space_between >= np.pi:
            raise ValueError("cannot have np.pi or greater space_between, "
                             "there wouldn't be any space left for the actual "
                             "plot.")

        self.space_between = space_between
        self.circle = CircleTool(1.0)
        self.value_callback = value_callback
        self.outer_thickness = 0.1

    def _prepare_plot(self, df):
        """
        convert the data into a pivot table for plotting
        with mean as the values, and the two non-data columns
        as the index and column values.

        Arguments:
            df: DataFrame with {MEAN} column

        Returns:
            pivot table of {MEAN}
        """.format(MEAN=MEAN)

        try:
            [df[c].unique() for c in df.columns]
        except TypeError:
            df = multilevel_dataframe(df)

        # TODO: should this work on samples without mean?
        if MEAN not in df.columns:
            raise ValueError(
                "dataframe must have {} column".format(MEAN))

        columns = df.columns
        if isinstance(columns[0], tuple):
            columns = []
            for c in df.columns:
                if c[0] not in columns:
                    columns.append(c[0])

        non_data_columns = [col for col in columns
                            if col not in DATA_KEYS]

        if len(non_data_columns) != 2:
            raise ValueError(
                "dataframe must have exactly two columns aside from {}, "
                "found: {}"
                .format(DATA_KEYS, non_data_columns))
        if self.value_callback is not None:
            return pivot_table(
                df, non_data_columns[0], non_data_columns[1], MEAN,
                value_callback=self.value_callback)

        return pivot_table(
            df, non_data_columns[0], non_data_columns[1], MEAN)

    # TODO: instead of sorting by labels, group order should simply
    #       be preserved from the table, and all dicts passed around
    #       should be OrderedDicts or DataFrames
    def group_angles(self, pivot_table):
        """
        find the start and end angles for each segment representing a
        group in the table.

        Arguments:
            pivot_table: pandas pivot table with groups as index and columns

        Returns:
            dict {group: (start_angle, end_angle)}
        """
        tot_conn = np.nansum(pivot_table.values)
        group_angles = {}
        groups = sorted(set(pivot_table.index) | set(pivot_table.columns))
        angle = 0
        occupied_space = self.space_between * len(groups)

        # TODO: better to warn and reduce size?
        if occupied_space >= 2 * np.pi:
            raise ValueError("with {} groups, space_between cannot be >="
                             " {}".format(len(groups),
                                          2 * np.pi / len(groups)))

        available_space = 2 * np.pi - occupied_space
        aspace_div2 = available_space * 0.5
        for grp in groups:
            try:
                size_from = np.nansum(pivot_table.loc[grp, :])
            except KeyError:
                size_from = 0

            try:
                size_to = np.nansum(pivot_table.loc[:, grp])
            except KeyError:
                size_to = 0

            size = size_from + size_to
            angle_size = aspace_div2 * size / tot_conn

            space = self.space_between * 0.5
            start = angle + space
            end = start + angle_size
            group_angles[grp] = (start, end)
            angle = end + space
        return group_angles

    def connection_angles(self, pivot_table, group_angles):
        """
        get the source and target angles for the curves representing
        the connections between groups

        Arguments:
            pivot_table: pandas pivot table with groups as index and columns
            group_angles: dict mapping group to the start and end angle

        Returns:
            tuple of dict (source_angles, dest_angles)
            each of the form {<group1>: {<group1>: start angle, end angle,
                                         <group2>: ...
                                         ...}
                              <group2>: {...}
                               ...}
            for all the groups
            where start_angle and end_angle are the angles defining a segment
        """
        source_angles = {ind: {} for ind in pivot_table.index}
        dest_angles = {ind: {} for ind in pivot_table.index}
        groups = sorted(group_angles.keys())
        for i, grp in enumerate(groups):
            start_angle, end_angle = group_angles[grp]
            group_angle_size = end_angle - start_angle
            angle = start_angle

            try:
                tot_from = np.nansum(pivot_table.loc[grp, :])
            except KeyError:
                tot_from = 0

            try:
                tot_to = np.nansum(pivot_table.loc[:, grp])
            except KeyError:
                tot_to = 0

            tot_conn = tot_from + tot_to

            from_order =\
                list(groups[i:]) + list(groups[:i])
            to_order =\
                list(groups[i+1:]) + list(groups[:i+1])
            from_order.reverse()
            to_order.reverse()

            for from_ in from_order:
                try:
                    angle_size = group_angle_size * pivot_table.loc[from_, grp]\
                                 / tot_conn
                    if not np.isnan(angle_size):
                        dest_angles[from_][grp] = (angle + angle_size, angle)
                        angle += angle_size
                except KeyError:
                    pass

            for to in to_order:
                try:
                    angle_size = group_angle_size * pivot_table.loc[grp, to]\
                                 / tot_conn
                    if not np.isnan(angle_size):
                        source_angles[grp][to] = (angle, angle + angle_size)
                        angle += angle_size
                except KeyError:
                    pass

        return source_angles, dest_angles

    def _conn_patch(self, source, dest, **kwargs):
        return self.circle.curve_polygon(*source, *dest, **kwargs)

    def _group_patch(self, angles, **kwargs):
        return self.circle.segment_polygon(
            *angles, self.outer_thickness, **kwargs)

    def group_colors(self, groups):
        return OrderedDict((grp, {'color': [1.0, 1.0, 1.0]})
                           for grp in groups)

    def __plot_components__(self, df):
        pvt = self._prepare_plot(df)
        group_angles = self.group_angles(pvt)
        groups = OrderedDict([(g, 'TODO:') for g in group_angles.keys()])
        group_colors = self.group_colors(groups)
        conn_angles = self.connection_angles(pvt, group_angles)
        group_patchdata = (group_angles, group_colors)

        group_labels = {grp: np.mean(a) for grp, a in group_angles.items()}
        return groups, group_labels, group_patchdata, conn_angles

    def plot(self, df):
        """"
        create a CirclePlot of the data in df

        Arguments:
             df: a pandas DataFrame which must have a {MEAN} column,
                 may have any of {DATA_KEYS} columns,
                 and must have exactly two other columns
                 the entries of which will define the groups to plot
                 the {MEAN} column will determine the connection weight
                 between the corresponding groups

        Returns:
            figure, axis with CirclePlot
        """.format(MEAN=MEAN, DATA_KEYS=DATA_KEYS)

        groups, group_labels, group_patchdata, conn_angles\
            = self.__plot_components__(df)
        group_angles, group_colors = group_patchdata
        source_angles, dest_angles = conn_angles
        sz = 60  # len(pivot_table.index)*4
        fig, ax = golden_figure(width=sz, height=sz)
        # TODO: adapt limits to text
        ax.set_xlim(left=-1.3, right=+1.3)
        ax.set_ylim(bottom=-1.3, top=+1.3)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.add_collection(matplotlib.collections.PatchCollection([
            self._conn_patch(s_angles, dest_angles[from_][to],
                             **group_colors[from_])
            for from_, conn in source_angles.items()
            for to, s_angles in conn.items()]))
        ax.add_collection(matplotlib.collections.PatchCollection([
            self._group_patch(angles, **group_colors[group])
            for group, angles in group_angles.items()]))

        oldfont = plt.rcParams.get('font.size')
        plt.rcParams.update({'font.size': sz})
        textcirc = CircleTool(self.circle.radius * 1.2)
        for t, a in group_labels.items():
            plt.text(*textcirc.angles_to_points(a), t,
                     rotation=90-a*(180/np.pi), rotation_mode="anchor")
        plt.rcParams.update({"font.size": oldfont})
        return fig, ax

    # TODO: test the actual plot method once its clear what
    #        its supposed to do
    # TODO: test how it handles NaNs
    # def plot(self, df):
    #     """"
    #     create a CirclePlot of the data in df

    #     Arguments:
    #          df: a pandas DataFrame which must have a {MEAN} column,
    #              may have any of {DATA_KEYS} columns,
    #              and must have exactly two other columns
    #              the entries of which will define the groups to plot
    #              the {MEAN} column will determine the connection weight
    #              between the corresponding groups

    #     Returns:
    #         figure, axis with CirclePlot
    #     """.format(MEAN=MEAN, DATA_KEYS=DATA_KEYS)
    #     pivot_table = self._prepare_plot(df)
    #     sz = 60# len(pivot_table.index)*4
    #     print(pivot_table.index, len(pivot_table.index))
    #     fig, ax = golden_figure(width=sz, height=sz)
    #     # TODO: adapt limits to text
    #     ax.set_xlim(left=-1.3, right=+1.3)
    #     ax.set_ylim(bottom=-1.3, top=+1.3)
    #     ax.get_xaxis().set_visible(False)
    #     ax.get_yaxis().set_visible(False)
    #     ax.set_xticklabels([])
    #     ax.set_yticklabels([])
    #     group_patches, connection_patches = self.get_patches(pivot_table)
    #     group_collection, connections_collection =\
    #         self.patch_collections(group_patches, connection_patches)
    #     ax.add_collection(group_collection)
    #     ax.add_collection(connections_collection)

    #     # awkward to re-calculate this!
    #     group_angles = {t: np.mean(a)
    #                     for t, a in self.group_angles(pivot_table).items()}
    #     oldfont = plt.rcParams.get('font.size')
    #     plt.rcParams.update({'font.size': sz})
    #     textcirc = CircleTool(self.circle.radius * 1.2)
    #     for t, a in group_angles.items():
    #         plt.text(*textcirc.angles_to_points(a), t,
    #                  rotation=90-a*(180/np.pi), rotation_mode="anchor")
    #     plt.rcParams.update({"font.size": oldfont})
    #     return fig, ax
