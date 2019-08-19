import numpy as np
import pandas as pd
import numpy.testing as npt
import pytest as pyt
from dmt.tk.enum import MEAN, STD
from dmt.tk.plotting.circle import CircleTool, CirclePlot


class TestCircleTool:

    def test_angles_to_points(self):
        unitcircle = CircleTool(1.0)
        npt.assert_array_equal(unitcircle.angles_to_points(0), [0, 1])
        npt.assert_array_equal(unitcircle.angles_to_points([0]), [[0, 1]])
        npt.assert_array_almost_equal(unitcircle.angles_to_points(
            [np.pi/2, np.pi]), [[1, 0], [0, -1]])

    def test_segment_points(self):
        unitcircle = CircleTool(1.0)

        def assert_points_at_angles(points, angles):
            npt.assert_array_equal(points[:, 0],
                                   np.sin(angles) * unitcircle.radius)
            npt.assert_array_equal(points[:, 1],
                                   np.cos(angles) * unitcircle.radius)

        npt.assert_array_equal(unitcircle.segment_points(0, np.pi/4, 0),
                               np.zeros((0, 2)))
        assert_points_at_angles(unitcircle.segment_points(0, np.pi/4, 1),
                                [0])
        assert_points_at_angles(
            unitcircle.segment_points(3 * np.pi / 5, 3 * np.pi / 4, 2),
            [3 * np.pi / 5, 3 * np.pi/4])

        assert_points_at_angles(
            unitcircle.segment_points(np.pi/4, np.pi, 3),
            [np.pi / 4, 5 * np.pi / 8, np.pi])

        drawpoints = unitcircle.segment_points(np.pi/4, 3 * np.pi/4)
        assert_points_at_angles(drawpoints[0:1], [np.pi/4])
        assert_points_at_angles(drawpoints[-1:], [3 * np.pi/4])
        drawpoints = unitcircle.circle_points(100)
        npt.assert_array_almost_equal(
            drawpoints[:, 0]**2 + drawpoints[:, 1]**2, unitcircle.radius)

        npt.assert_array_almost_equal(
            unitcircle.segment_points(2 * np.pi / 3, 0),
            np.flip(unitcircle.segment_points(0, 2 * np.pi / 3), axis=0))

    def test_circle_points(self):
        unitcircle = CircleTool(1.0)
        npt.assert_array_equal(unitcircle.circle_points(0),
                               np.zeros((0, 2)))
        npt.assert_array_equal(unitcircle.circle_points(1),
                               [[0., 1.]])
        npt.assert_array_almost_equal(
            unitcircle.circle_points(2),
            [[0., 1.], [0., 1.]])
        npt.assert_array_almost_equal(
            unitcircle.circle_points(5),
            [[0., 1.], [1., 0.], [0., -1.], [-1, 0], [0., 1.]])
        drawpoints = unitcircle.circle_points(100)
        npt.assert_array_almost_equal(
            drawpoints[:, 0]**2 + drawpoints[:, 1]**2, unitcircle.radius)

    def test_curve_points(self):
        unitcircle = CircleTool(1.0)
        pts = unitcircle.curve_points(0, np.pi/2)
        start = pts[0]
        end = pts[-1]
        npt.assert_array_almost_equal(start, [0, 1])
        npt.assert_array_almost_equal(end, [1, 0])
        N = 10
        npt.assert_array_almost_equal(
            unitcircle.curve_points(0, np.pi, N=N),
            np.array([(0, p) for p in np.linspace(1, -1, N)]))

    # TODO: test and implement curve_polygon
    def test_curve_polygon(self):
        unitcircle = CircleTool(1.0)
        f1, f2, t1, t2 = np.pi/2, 3 * np.pi / 4, np.pi, 8 * np.pi / 7
        poly = unitcircle.curve_polygon(f1, f2, t1, t2)
        npt.assert_array_equal(np.concatenate(
            [unitcircle.curve_points(f1, t1),
             unitcircle.segment_points(t1, t2),
             unitcircle.curve_points(t2, f2),
             unitcircle.segment_points(f2, f1)]),
                               poly.get_xy())

    def test_segment_polygon(self):
        unitcircle = CircleTool(1.0)
        angle1, angle2 = 2 * np.pi/3, np.pi
        width = 0.01
        outer = CircleTool(1 + width)
        inner_points = unitcircle.segment_points(angle1, angle2)
        npt.assert_array_almost_equal(
            unitcircle.segment_polygon(angle1, angle2, width).get_xy(),
            np.concatenate([
                inner_points,
                outer.segment_points(angle2, angle1),
                [inner_points[0]]]))


class TestCirclePlot:

    def test_prepare_plot(self):
        df = pd.DataFrame({
            MEAN: [1, 2, 1, 2],
            STD: [1, 2, 3, 1],
            'pre': [{'mtype': 'a'}, {'mtype': 'a'},
                    {'mtype': 'b'}, {'mtype': 'b'}],
            'post': [{'mtype': 'a'}, {'mtype': 'b'},
                     {'mtype': 'a'}, {'mtype': 'b'}]})
        table = CirclePlot()._prepare_plot(df)
        pd.testing.assert_frame_equal(table,
                                      pd.DataFrame({
                                          'pre: mtype': ['a', 'a', 'b', 'b'],
                                          'post: mtype': ['a', 'b', 'a', 'b'],
                                          MEAN: [1, 2, 1, 2]})
                                      .pivot_table(index='pre: mtype',
                                                   columns='post: mtype',
                                                   values=MEAN))

    def test_type_patch_angles(self):
        pivot_table = pd.DataFrame({
            'pre: mtype': ['a', 'a', 'b', 'b'],
            'post: mtype': ['a', 'b', 'a', 'b'],
            MEAN: [1, 2, 1, 2]})\
                        .pivot_table(index='pre: mtype',
                                     columns='post: mtype',
                                     values=MEAN)
        plotter = CirclePlot()
        type_angles = plotter.type_angles(pivot_table)

        exp_type = {'a': (0, 5/6 * np.pi),
                    'b': (5/6 * np.pi, 12/6 * np.pi)}

        for f in ['a', 'b']:
            assert type_angles[f] == pyt.approx(exp_type[f])

    def test_connection_angles(self):

        pivot_table = pd.DataFrame({
            'pre: mtype': ['a', 'a', 'b', 'b'],
            'post: mtype': ['a', 'b', 'a', 'b'],
            MEAN: [1, 2, 1, 2]})\
                        .pivot_table(index='pre: mtype',
                                     columns='post: mtype',
                                     values=MEAN)

        plotter = CirclePlot()
        source_angles, dest_angles = plotter.connection_angles(
            pivot_table, plotter.type_angles(pivot_table))

        exp_source = {'a': {'a': (2/6 * np.pi, 3/6 * np.pi),
                            'b': (3/6 * np.pi, 5/6 * np.pi)},
                      'b': {'a': (11/6 * np.pi, 12/6 * np.pi),
                            'b': (9/6 * np.pi, 11/6 * np.pi)}}

        exp_dest = {'b': {'a': (0, 1/6 * np.pi),
                          'b': (7/6 * np.pi, 9/6 * np.pi)},
                    'a': {'a': (1/6 * np.pi, 2/6 * np.pi),
                          'b': (5/6 * np.pi, 7/6 * np.pi)}}
        for f in ['a', 'b']:
            for t in ['a', 'b']:
                assert dest_angles[f][t] == pyt.approx(exp_dest[f][t])
                assert source_angles[f][t] == pyt.approx(exp_source[f][t])
