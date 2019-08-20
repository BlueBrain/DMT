import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from dmt.tk.enum import DATA_KEYS, MEAN
from dmt.tk.plotting.utils import make_hashable


# TODO: DOCSTRINGS DOCSTRINGS DOCSTRINGS
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

    def curve_polygon(self, from_angle1, from_angle2, to_angle1, to_angle2):
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
        return matplotlib.patches.Polygon(xy, closed=False)

    def segment_polygon(self, from_angle, to_angle, width):
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
        return matplotlib.patches.Polygon(xy, closed=True)


class CirclePlot:
    """
    a plotter for circle-plots. CirclePlots consist of circle segments
    connected by curves, the thickness of which corresponds to the weight
    of the connection
    """
    def __init__(self, space_between=0.0):
        """
        Arguments:
           space_between : the space to leave between segments, in radians
        """
        self.space_between = space_between
        self.circle = CircleTool(1.0)

    # TODO: test case where precol and postcol don't have same values
    # TODO: test case where pre and post are just strings instead of
    #       dicts
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
        non_data_columns = [col for col in df.columns
                            if col not in DATA_KEYS]
        assert len(non_data_columns) == 2
        df, tocol = make_hashable(df, non_data_columns[0])
        df, fromcol = make_hashable(df, non_data_columns[1])
        pivot_table = df.pivot_table(columns=tocol, index=fromcol,
                                     values=MEAN)
        return pivot_table

    def type_angles(self, pivot_table):
        """
        find the start and end angles for each segment representing a
        group in the table.

        Arguments:
            pivot_table: pandas pivot table with groups as index and columns

        Returns:
            dict {group: (start_angle, end_angle)}
        """
        tot_conn = np.sum(pivot_table.values)
        type_angles = {}
        angle = 0
        for typ in pivot_table.index:
            size =\
                (pivot_table.loc[typ, :].sum() + pivot_table.loc[:, typ].sum())
            angle_size = np.pi * size / tot_conn
            space = self.space_between * 0.5
            type_angles[typ] = (angle + space, angle + angle_size - space)
            angle += angle_size
        return type_angles

    def connection_angles(self, pivot_table, type_angles):
        """
        get the source and target angles for the curves representing
        the connections between groups

        Arguments:
            pivot_table: pandas pivot table with groups as index and columns
            type_angles: dict mapping group to the start and end angle

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
        for i, ind in enumerate(pivot_table.index):
            start_angle, end_angle = type_angles[ind]
            type_angle_size = end_angle - start_angle
            angle = start_angle

            tot_conn = (pivot_table.loc[ind, :].sum()
                        + pivot_table.loc[:, ind].sum())

            from_order =\
                list(pivot_table.index[i:]) + list(pivot_table.index[:i])
            to_order =\
                list(pivot_table.index[i+1:]) + list(pivot_table.index[:i+1])
            from_order.reverse()
            to_order.reverse()

            for from_ in from_order:
                angle_size = type_angle_size * pivot_table.loc[from_, ind]\
                             / tot_conn
                dest_angles[from_][ind] = (angle + angle_size, angle)
                angle += angle_size

            for to in to_order:
                angle_size = type_angle_size * pivot_table.loc[ind, to]\
                             / tot_conn
                source_angles[ind][to] = (angle, angle + angle_size)
                angle += angle_size

        return source_angles, dest_angles

    def connection_patches(self, pivot_table, type_angles):
        """
        get matplotlib polygons representing the connections between groups

        Arguments:
            pivot_table: pandas pivot_table
            type_angles: dict mapping group to the start and end angle

        Returns:
            dict of the form {<group>: {<group>: a::Polygon, ...} ...}
            for all the groups in pivot_table
        """
        source_angles, dest_angles =\
            self.connection_angles(pivot_table, type_angles)
        patches = {from_:
                   {to: self.circle.curve_polygon(*source_angles[from_][to],
                                                  *dest_angles[from_][to])
                    for to in pivot_table.index}
                   for from_ in pivot_table.index}
        return patches

    def type_patches(self, type_angles):
        """
        get matplotlib polygons representing the locations of groups
        on the circle

        Arguments:
            type_angles: dict mapping group to the start and end angle
        """
        return {
            typ: self.circle.segment_polygon(*angles, 0.1)
            for typ, angles in type_angles.items()}

    def get_patches(self, pivot_table):
        """
        get the patches for both connections and groups

        Arguments:
            pivot_table: pandas pivot_table

        Returns:
            type_patches: dict mapping groups to representative polygons
                          see type_patches method
            connection_patches: dict mapping groups to dicts mapping groups to
                                polygons representing the connection
                                see connection_patches method
        """
        type_angles = self.type_angles(pivot_table)
        connection_patches = self.connection_patches(pivot_table,
                                                     type_angles)
        type_patches = self.type_patches(type_angles)
        return type_patches, connection_patches

    # TODO: could do with some tests
    def patch_collections(self, type_patches, connection_patches):
        """
        turn the patch_dicts from get_patches into colored PatchCollections

        Arguments:
            type_patches: dict mapping groups to representative polygons
                          see type_patches method
            connection_patches: dict mapping groups to dicts mapping groups to
                                polygons representing the connection
                                see connection_patches method

        Returns:
            PatchCollection of type_patches
            PatchCollection of connection_patches
        """
        types = sorted(type_patches.keys())
        type_color = np.arange(len(types))
        type_patch_list = [type_patches[typ] for typ in types]
        connection_color = np.array(
            [type_color[i] for i, typ in enumerate(types)
             for _ in connection_patches[typ].values()])
        connection_patch_list = [
            p for typ in types
            for p in connection_patches[typ].values()]

        type_collection = matplotlib.collections.PatchCollection(
            type_patch_list)
        type_collection.set_array(type_color)
        connections_collection = matplotlib.collections.PatchCollection(
            connection_patch_list)
        connections_collection.set_array(connection_color)
        alpha = 0.5
        connections_collection.set_alpha(alpha)

        return type_collection, connections_collection

    # TODO: test the actual plot method one its clear what
    #        its supposed to do
    # TODO: test how it handles NaNs
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
        pivot_table = self._prepare_plot(df)
        assert sorted(pivot_table.index) == sorted(pivot_table.columns)
        ax = plt.axes()
        # TODO: adapt limits to text
        ax.set_xlim(left=-1.3, right=+1.3)
        ax.set_ylim(bottom=-1.3, top=+1.3)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        type_patches, connection_patches = self.get_patches(pivot_table)
        type_collection, connections_collection =\
            self.patch_collections(type_patches, connection_patches)
        ax.add_collection(type_collection)
        ax.add_collection(connections_collection)

        # awkward to re-calculate this!
        type_angles = {t: np.mean(a)
                       for t, a in self.type_angles(pivot_table).items()}
        textcirc = CircleTool(self.circle.radius * 1.2)
        for t, a in type_angles.items():
            plt.text(*textcirc.angles_to_points(type_angles[t]), t)
        return plt.gcf(), ax


# CirclePlot

# xlabel, ylabel are columns to plot by (e.g. pre and post)
# (these are inferred)
# make_hashable these columns
# plot_circle_plot(df.pivot_table(index=x_column, columns=y_column, values=MEAN))
# TODO: how to handle differing coloration by sclass?

# NOTE: for this plotter we certainly do need some data at analysis-composing time.
#       we need to know what to pivot around
#       (e.g. for connectomics 'pre' and 'post')
#       OR: well, do we really? couldn't we just find the two non-data columns
#           and complain if there are more
#       hmm... that seems like the simplest option
#       though presently their order isn't guaranteed, but that is
#       not the plotter's problem, but whoever passed the dataframe
#
#       it would still be best to make it possible to pass these as a kwarg.
# NOTE: default behavior is to infer, but can also pass args at initialization
#       or at plot-time
