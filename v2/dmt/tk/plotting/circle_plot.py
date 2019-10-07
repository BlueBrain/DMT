"""
Make a circle plot.
"""
"""
Plot heat maps.
"""
import numpy as np
import pandas as pd
import seaborn
from . import golden_aspect_ratio
from .figure import Figure
from dmt.tk.plotting.utils import pivot_table
from dmt.tk.field import Field, lazyproperty, WithFields
from . import get_dataframe


class GraphicCircle(WithFields):
    """
    The circle that will be plotted
    """

    center = Field(
        """
        Center of the circle.
        """,
        __default_value__=np.array([0., 0.]))
    radius = Field(
        """
        Radius of the circle.
        """,
        __default_value__=1.)
    rotation = Field(
        """
        Some kind of rotation, that I do not understand.
        """,
        __default_value__=0.)

    def at(self, angle):
        return self.center + np.array([
            np.sin(angle + self.rotation) * self.radius,
            np.cos(angle + self.rotation) * self.radius])

    def segment_points(self, _from=0., to=2*np.pi, N=100):
        return np.array([
            self.at(angle)
            for angle in np.linspace(_from, to, N)])

    def _arc_circle(self, angle_1, angle_2):
        angle_mean = (angle_1 + angle_2) / 2.
        #mn_ngl = (angle1 + angle2) / 2
        angle_off = angle_mean - np.minimum(angle_1, angle_2)
        #off_ngl = mn_ngl - numpy.minimum(angle1, angle2)
        angle_center = np.pi - 2 * angle_off
        #ctr_ngl = numpy.pi - 2 * off_ngl
        angle_rotation = np.pi / 2 - np.minimum(angle_1, angle_2)
        #rot_ngl = numpy.pi / 2 - numpy.minimum(angle1, angle2)
        length = self.radius / np.cos(angle_off)
        #L = self.r / numpy.cos(off_ngl)
        radius_arc = self.radius * np.tan(angle_off);
        #Lp = self.r * numpy.tan(off_ngl)
        center_arc = self.center + np.array([
            length * np.sin(angle_mean + self.rotation),
            length * np.cos(angle_mean + self.rotation)])
        #c = numpy.array([numpy.sin(mn_ngl + self.rot) * L,
        #                 numpy.cos(mn_ngl + self.rot) * L]) + self.c
        arc_circle =\
            GraphicCircle(
                center=center_arc,
                radius=radius_arc,
                rotation=self.rotation - angle_rotation)\
                if angle_1 < angle_2 else\
                   GraphicCircle(
                       center=center_arc,
                       radius=radius_arc,
                       rotation=self.rotation - angle_rotation - angle_center)
        arc_angle =\
            - angle_center if angle_1 < angle_2 else angle_center

        return arc_circle, arc_angle
        # if angle1 < angle2:
        #     return Circle(c, Lp, rotation=self.rot-rot_ngl), -ctr_ngl
        # return Circle(c, Lp, rotation=self.rot-rot_ngl-ctr_ngl), ctr_ngl

    def arc_points(self, angle_one, angle_two, N=100):
        arc_circle, arc_angle = self._arc_circle(angle_one, angle_two)
        return arc_circle.segment_points(0, arc_angle, N=N)

    def draw(self, N=100, *args, **kwargs):
        from matplotlib import pyplot as plt
        pts = self.segment_points(N=N)
        plt.plot(pts[:, 0], pts[:, 1], *args, **kwargs)


class Synaptome(GraphicCircle):

    blowup = Field(
        """
        Some sort of factor, to be understood
        """,
        __default_value__=1.5)
    buf_main = Field(
        """
        buffer_main?
        """,
        __default_value__=0.3)
    lbl_min_sz = Field(
        """
        Min size for the labels?
        """,
        __default_value__=0.02)
    arr_min_size = Field(
        """
        Min size of an array?
        """,
       __default_value__=0.02)
    fontsize = Field(
        """
        Fontsize
        """,
        __default_value=[8, 25])
    col_dict = Field(
        """
        A dict of colors?
        """,
        __default_value__=dict([
            (_m, numpy.random.rand(3) * 0.6)
            for _m in self.data_exc.keys() + self.data_inh.keys()]))

    def __init__(self, aff, eff, mtype=None, c=numpy.array([0.0, 0.0]), r=1.0,
                 blowup=1.5, buf_main=0.3, transparency_coeff=(0.0, 1.0),
                 col_dict=None, lbl_min_sz=0.02, arr_min_sz=0.02, fontsize=[8, 25], **kwargs):
        super(Synaptome, self).__init__(c, r, **kwargs)
        self.blowup = blowup
        self.buf_main = buf_main
        self.lbl_min_sz = lbl_min_sz
        self.arr_min_sz = arr_min_sz
        self.fontsize = fontsize
        self.eff_aff = ('EFF', 'AFF')
        if mtype is not None:
            self.eff_aff = (mtype, mtype)
        self.alpha_fun = lambda s: numpy.maximum(
            numpy.minimum(
                transparency_coeff[0] + numpy.abs(numpy.diff(s)) * transparency_coeff[1],
                1.0),
            0.05)
                          
        self.prepare_data(aff, eff)
        self.prepare_area(sc_mtype=mtype)
        self.link_starts = {}; self.link_ends = {}
        self.prepare_link_starts([self.vals_eff_inh, self.vals_eff_exc],
                                 self.sum_eff, [self.data_inh.keys(), self.data_exc.keys()],
                                 self.space_eff, 'EFF', self.link_starts)
        self.prepare_link_starts([self.vals_aff_exc, self.vals_aff_inh],
                                 self.sum_aff, [self.data_exc.keys(), self.data_inh.keys()],
                                 self.space_aff, 'AFF', self.link_starts, shortcut=(mtype, self.link_ends, 'EFF'))
        self.prepare_link_ends(self.data_exc, self.sum_exc, self.space_exc, self.link_ends, sc_mtype=mtype)
        self.prepare_link_ends(self.data_inh, self.sum_inh, self.space_inh, self.link_ends, sc_mtype=mtype)
        if col_dict is None:
            self.col_dict = dict([(_m, numpy.random.rand(3) * 0.6) for _m in self.data_exc.keys() + self.data_inh.keys()])
        else:
            self.col_dict = col_dict

    def __extract_data__(self, aff, eff, match):
        extract = OrderedDict([(_a[0], numpy.array([_a[2], 0.0])) for _a in aff if _a[1] == match])
        for _a in eff:
            if _a[1] == match:
                extract.setdefault(_a[0], numpy.array([0.0, 0.0]))[1] = _a[2]
        return extract

    def prepare_data(self, aff, eff):
        self.data_exc = self.__extract_data__(aff, eff, 'EXC')
        self.data_inh = self.__extract_data__(aff, eff, 'INH')
        self.vals_eff_inh = [v[1] for v in self.data_inh.values()]
        self.vals_eff_exc = [v[1] for v in self.data_exc.values()]
        self.vals_aff_inh = [v[0] for v in self.data_inh.values()]
        self.vals_aff_exc = [v[0] for v in self.data_exc.values()]

    def prepare_area(self, sc_mtype=None):
        self.sum_aff = numpy.sum(self.vals_aff_inh) + numpy.sum(self.vals_aff_exc)
        self.sum_eff = numpy.sum(self.vals_eff_inh) + numpy.sum(self.vals_eff_exc)
        self.sum_exc = numpy.sum(self.vals_eff_exc) + numpy.sum(self.vals_aff_exc)
        self.sum_inh = numpy.sum(self.vals_eff_inh) + numpy.sum(self.vals_aff_inh)
        self.sum_exc -= numpy.sum(self.data_exc.get(sc_mtype, (0, 0)))
        self.sum_inh -= numpy.sum(self.data_inh.get(sc_mtype, (0, 0)))
        base_space = 2 * numpy.pi - 4 * self.buf_main
        space_eff = base_space * (self.blowup * self.sum_eff) / (self.blowup * (self.sum_eff + self.sum_aff) + self.sum_exc + self.sum_inh)
        self.space_eff = (-space_eff / 2.0, space_eff / 2.0)
        space_exc = base_space * (self.sum_exc) / (self.blowup * (self.sum_eff + self.sum_aff) + self.sum_exc + self.sum_inh)
        self.space_exc = (self.space_eff[1] + self.buf_main + space_exc, self.space_eff[1] + self.buf_main)
        space_aff = base_space * (self.blowup * self.sum_aff) / (self.blowup * (self.sum_eff + self.sum_aff) + self.sum_exc + self.sum_inh)
        self.space_aff = (self.space_exc[0] + self.buf_main, self.space_exc[0] + self.buf_main + space_aff)
        space_inh = base_space * (self.sum_inh) / (self.blowup * (self.sum_eff + self.sum_aff) + self.sum_exc + self.sum_inh)
        self.space_inh = (self.space_aff[1] + self.buf_main + space_inh, self.space_aff[1] + self.buf_main)

    def prepare_link_starts(self, vals, nrmlz, lbls, space, prefix, mp, shortcut=None):
        sc_mtype = None
        if shortcut is not None:
            sc_mtype, mp_alt, prefix_alt = shortcut
        delta = space[1] - space[0]
        s = space[0]
        for _vals, _lbls in zip(vals, lbls):
            for _v, _l in zip(_vals, _lbls):
                if _l == sc_mtype:
                    mp_alt[prefix_alt + _l] = (s + _v * delta / nrmlz, s)
                else:
                    mp[prefix + _l] = (s, s + _v * delta / nrmlz)
                s += _v * delta / nrmlz
        return mp

    def prepare_link_ends(self, data, nrmlz, space, mp, sc_mtype=None):
        delta = space[1] - space[0]
        s = space[0]
        for kk in data.keys():
            if kk != sc_mtype:
                mp['AFF' + kk] = (s, s + data[kk][0] * delta / nrmlz)
                s = mp['AFF' + kk][1]
                mp['EFF' + kk] = (s, s + data[kk][1] * delta / nrmlz)
                s = mp['EFF' + kk][1]
        return mp

    def link_pts(self, lnk_name):
        s = self.link_starts[lnk_name]
        e = self.link_ends[lnk_name]
        side1 = self.arc_points(s[1], e[1], N=50)
        side2 = self.arc_points(e[0], s[0], N=50)
        strt = self.segment_points(s[0], s[1], N=10)
        nd = self.segment_points(e[1], e[0], N=10)
        if numpy.abs(numpy.diff(s)) >= self.arr_min_sz:
            if lnk_name.startswith('EFF'):
                return [numpy.vstack([strt, side1, nd, side2]),
                        self.arrow_pts(side1, side2, s, e)]
            return [numpy.vstack([strt, side1, nd, side2]),
                    self.arrow_pts(side1[-1::-1], side2[-1::-1], e, s)]
        return [numpy.vstack([strt, side1, nd, side2])]

    def arrow_pts(self, side1, side2, s, e):
        md_s1 = 0.4 * s[0] + 0.6 * s[1]; md_s2 = 0.6 * s[0] + 0.4 * s[1]
        md_e1 = 0.45 * e[0] + 0.55 * e[1]; md_e2 = 0.55 * e[0] + 0.45 * e[1]
        md_e = 0.5 * e[0] + 0.5 * e[1]
        pt_e = numpy.array([self.at(md_e)])
        arc1 = self.arc_points(md_s1, md_e1, N=50)[:45]
        arc2 = self.arc_points(md_e2, md_s2, N=50)[5:]
        crn_1 = 0.65 * side1[int(len(side1) * 0.9), :] + 0.35 * side2[int(len(side2) * 0.1), :] 
        crn_2 = 0.35 * side1[int(len(side1) * 0.9), :] + 0.65 * side2[int(len(side2) * 0.1), :]
        return numpy.vstack([arc1, crn_1, pt_e, crn_2, arc2])

    def link_collection(self):
        from matplotlib.collections import PolyCollection
        ln_nms = [k for k, v in self.link_starts.items() if numpy.diff(v) != 0]
        verts = []; cols = []
        for _name in ln_nms:
            verts.extend(self.link_pts(_name))
            _a = self.alpha_fun(self.link_ends[_name])
            cols.append(numpy.hstack([self.col_dict[_name[3:]], _a]))
            while len(verts) > len(cols):
                cols.append(cols[-1] * numpy.array([0.8, 0.8, 0.8, 1.0]))
        return PolyCollection(verts, facecolors=cols, edgecolors='grey', linewidth=0.1)

    def label_loc(self, mname):
        tpl = self.link_ends['AFF' + mname] + self.link_ends['EFF' + mname]
        ngl = 0.5 * (numpy.max(tpl) + numpy.min(tpl))
        pos = Circle(self.c, self.r * 1.04, rotation=self.rot).at(ngl)
        rot_angle = 90 - 180 * (self.rot + ngl) / numpy.pi
        return pos, rot_angle

    def label_collection(self):
        coll = []

        def mk_kwargs(ngl, **kwargs):
            kwargs['horizontalalignment'] = 'left'
            kwargs['verticalalignment'] = 'center'
            if ngl > 90:
                ngl -= 180
                kwargs['horizontalalignment'] = 'right'
            elif ngl < -90:
                ngl += 180
                kwargs['horizontalalignment'] = 'right'
            kwargs['rotation'] = ngl
            return kwargs
        for mname in list(self.data_exc.keys()) + list(self.data_inh.keys()):
            sz = -numpy.diff(self.link_ends.get('AFF' + mname, (0, 100))) \
            - numpy.diff(self.link_ends['EFF' + mname])
            if sz < self.lbl_min_sz:
                continue
            pos, ngl = self.label_loc(mname)
            coll.append(((pos[0], pos[1], mname), mk_kwargs(ngl, fontsize=self.fontsize[0])))
        for tpname, data in zip(self.eff_aff, [self.space_eff, self.space_aff]):
            ngl = numpy.mean(data)
            pos = self.at(ngl)
            coll.append(((pos[0], pos[1], tpname), mk_kwargs(90 - 180 * (self.rot + ngl) / numpy.pi,
                                                             fontsize=self.fontsize[1])))
        return coll

    def draw(self, ax=None):
        from matplotlib import pyplot as plt
        if ax is None:
            ax = plt.gca()
        ax.add_collection(self.link_collection())
        for a, kw in self.label_collection():
            ax.text(*a, **kw)
        ax.set_xlim([-1.1 * self.r, 1.1 * self.r])
        ax.set_ylim([-1.1 * self.r, 1.2 * self.r])
        plt.axis('off')


layer_cols = {'1': numpy.array([0.3, 0.3, 0]),
              '2': numpy.array([0.0, 0.3, 0.3]),
              '3': numpy.array([0.15, 0.3, 0.15]),
              '4': numpy.array([0.3, 0.0, 0.3]),
              '5': numpy.array([0.0, 0.6, 0.0]),
              '6': numpy.array([0.1, 0.1, 0.4])}
default = numpy.array([0.2, 0.2, 0.2])
add_ei = {'EXC': numpy.array([0.5, 0.0, 0.0]),
          'INH': numpy.array([0.0, 0.0, 0.5])}


def make_col_dict(mtypes):
    return dict([(_m[0], numpy.minimum(layer_cols.setdefault(_m[0][1], default)
                                       + add_ei[_m[1]] +
                                       numpy.random.rand(3) * 0.25, 1.0))
                 for _m in mtypes])


def make_synaptome(cfg, mtype, sample=100, **kwargs):
    import bluepy.v2 
    import progressbar
    from builtins import sum as bsum
    circ = bluepy.v2.Circuit(cfg)
    mtypes = circ.cells.get(properties=bluepy.v2.Cell.MTYPE)
    mtype_names = circ.cells.get(properties=[bluepy.v2.Cell.MTYPE,
                                                bluepy.v2.Cell.SYNAPSE_CLASS]).drop_duplicates().values
    mtype_names = mtype_names[numpy.argsort([_m[0] for _m in mtype_names])]
    gids = circ.cells.ids(group={bluepy.v2.Cell.MTYPE: mtype})
    if len(gids) > sample:
        gids = numpy.random.choice(gids, sample, replace=False)
    ctm = circ.connectome

    def __reader__(func, pbar_lbl, rd_props):
        pbar = progressbar.ProgressBar(widgets=[progressbar.widgets.FormatLabel(pbar_lbl), progressbar.widgets.Bar()])
        data = []
        for _g in pbar(gids):
            try:
                data.append(mtypes[func(_g, properties=rd_props).values].value_counts())
            except Exception as an_exc:
                print(str(_g) + '::' + str(an_exc))
        return bsum(data)
    data_eff = __reader__(ctm.efferent_synapses, 'EFF ', bluepy.v2.Synapse.POST_GID)
    data_aff = __reader__(ctm.afferent_synapses, 'AFF ', bluepy.v2.Synapse.PRE_GID)
    eff = [(m[0], m[1], data_eff[m[0]]) for m in mtype_names]
    aff = [(m[0], m[1], data_aff[m[0]]) for m in mtype_names]
    if 'col_dict' not in kwargs:
        kwargs['col_dict'] = make_col_dict(mtype_names)
    s = Synaptome(aff, eff, transparency_coeff=(0.0, 3.0), mtype=mtype, **kwargs)
    if 'rotation' not in kwargs:
        s.rot = -0.5 * numpy.mean(s.space_aff)
    return s


if __name__ == "__main__":
    import sys
    import os
    from matplotlib import pyplot as plt
    if os.path.exists(sys.argv[2]) and os.path.isdir(sys.argv[2]):
        import bluepy.v2
        circ = bluepy.v2.Circuit(sys.argv[1])
        for m in circ.cells.mtypes:
            print(m)
            ax = plt.figure(figsize=(8.0, 6.5)).add_axes([0.2, 0.1, 0.6, 0.8])
            make_synaptome(sys.argv[1], m).draw(ax=ax)
            #ax.set_title(m, fontsize=25)
            plt.gcf().savefig(os.path.join(sys.argv[2], 'SYNAPTOME' + m + '.pdf'))
            plt.gcf().savefig(os.path.join(sys.argv[2], 'SYNAPTOME' + m + '.png'))
            plt.close(plt.gcf())
    else:
        ax = plt.figure(figsize=(8.0, 6.5)).add_axes([0.2, 0.1, 0.6, 0.8])
        make_synaptome(sys.argv[1], sys.argv[2]).draw(ax=ax)
        #ax.set_title(sys.argv[2], fontsize=25)
        plt.show()
