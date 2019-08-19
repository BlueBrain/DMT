import numpy as np
import matplotlib
from dmt.tk.enum import DATA_KEYS, MEAN
from dmt.tk.plotting.utils import make_hashable

# TODO: DOCSTRINGS DOCSTRINGS DOCSTRINGS
class CircleTool:

    def __init__(self, radius, center=None, rotation=0):
        if center is None:
            center = np.zeros((2,))
        self.center = center
        self.radius = radius
        self.rot = rotation

    def angles_to_points(self, angles):
        angles = np.array(angles)
        xes = np.sin(angles + self.rot) * self.radius + self.center[0]
        yes = np.cos(angles + self.rot) * self.radius + self.center[1]
        if angles.shape == ():
            return np.array([xes, yes])
        return np.array([xes, yes]).transpose()

    def segment_points(self, from_angle, to_angle, N=50):
        return self.angles_to_points(np.linspace(from_angle, to_angle, N))

    def circle_points(self, N=100):
        return self.segment_points(0, 2 * np.pi, N=N)

    def _arc_circle(self, from_angle, to_angle):
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
        if np.isclose(np.abs(from_angle - to_angle), np.pi):
            start = self.angles_to_points(from_angle)
            end = self.angles_to_points(to_angle)
            xspace = np.linspace(start[0], end[0], N)
            yspace = np.linspace(start[1], end[1], N)
            return np.array([xspace, yspace]).transpose()

        a, ngl = self._arc_circle(from_angle, to_angle)
        return a.segment_points(0, ngl, N=N)

    def draw(self, N=100, *args, **kwargs):
        from matplotlib import pyplot as plt
        pts = self.circle_points(N=N)
        plt.plot(pts[:, 0], pts[:, 1], *args, **kwargs)

    def curve_polygon(self, from_angle1, from_angle2, to_angle1, to_angle2):
        xy = np.concatenate(
            [self.curve_points(from_angle1, to_angle1),
             self.segment_points(to_angle1, to_angle2),
             self.curve_points(to_angle2, from_angle2),
             self.segment_points(from_angle2, from_angle1)])
        return matplotlib.patches.Polygon(xy, closed=False)

    def segment_polygon(self, from_angle, to_angle, width):
        outer = CircleTool(self.radius + width)
        xy = np.concatenate(
            [self.segment_points(from_angle, to_angle),
             outer.segment_points(to_angle, from_angle)])
        return matplotlib.patches.Polygon(xy, closed=True)


class CirclePlot:

    def __init__(self):
        self.circle = CircleTool(1.0)

    # TODO: test case where precol and postcol don't have same values
    def _prepare_plot(self, df):
        non_data_columns = [col for col in df.columns
                            if col not in DATA_KEYS]
        assert len(non_data_columns) == 2
        df, tocol = make_hashable(df, non_data_columns[0])
        df, fromcol = make_hashable(df, non_data_columns[1])
        pivot_table = df.pivot_table(columns=tocol, index=fromcol,
                                     values=MEAN)
        return pivot_table

    def type_angles(self, pivot_table):
        tot_conn = np.sum(pivot_table.values)
        type_angles = {}
        angle = 0
        for typ in pivot_table.index:
            size =\
                (pivot_table.loc[typ, :].sum() + pivot_table.loc[:, typ].sum())
            angle_size = np.pi * size / tot_conn
            type_angles[typ] = (angle, angle + angle_size)
            angle += angle_size
        return type_angles

    def connection_angles(self, pivot_table, type_angles):
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
                dest_angles[from_][ind] = (angle, angle + angle_size)
                angle += angle_size

            for to in to_order:
                angle_size = type_angle_size * pivot_table.loc[ind, to]\
                             / tot_conn
                source_angles[ind][to] = (angle, angle + angle_size)
                angle += angle_size

        return source_angles, dest_angles

    def connection_patches(self, pivot_table, type_patch_angles):
        source_angles, dest_angles =\
            self.connection_angles(pivot_table, type_patch_angles)
        patches = {from_:
                   {to: self.circle.curve_polygon(*source_angles[from_][to],
                                                  *dest_angles[from_][to])
                    for to in pivot_table.index}
                   for from_ in pivot_table.index}
        return patches

    def get_patches(self, pivot_table):
        type_angles = self.type_angles(pivot_table)
        connection_patches = self.connection_patches(pivot_table,
                                                     self.type_angles)
        type_patches = self.type_patches(type_angles)
        return type_patches, connection_patches

    def plot(self, df):
        pivot_table = self._prepare_plot(df)
        assert sorted(pivot_table.index) == sorted(pivot_table.columns)


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
