import numpy as np
from warnings import warn


def compose_atlas_adapter(atlas_dir):
    """..."""
    return AtlasAdapter(atlas_dir)
    pass


def _list_if_not_list(item):
    if isinstance(item, list):
        return item
    return [item]


# TODO: what if someone wants to request a property for
#       region X OR layer Y
#       OPTION1: accept list of queries and interperet as or
#       OPTION2: create query class and allow constructing
#               from other queries with and/or
#       pref. option 1 for now
# TODO: what if someone wants to exclude from their query
#       e.g. All Thalamus except RT
#       OPTION1: option 2 above, including 'not'
#       OPTION2: allow 'exclude' key in query, which links to
#                another query of values to exclude
class AtlasAdapter():

    def __init__(self, atlas_dir):
        from voxcell.nexus.voxelbrain import Atlas
        self._atlas = Atlas.open(atlas_dir)

    # TODO: should I pass whole query to _translate_layer
    def mask_for_query(self, query):
        masks = [self._atlas.load_data("brain_regions").raw > 0]
        if 'region' in query:
            region_mask = np.any(
                [self._region_mask(region)
                 for region in _list_if_not_list(query['region'])], axis=0)
            masks.append(region_mask)
        if 'layer' in query:
            layer_mask = np.any(
                [self._layer_mask(layer)
                 for layer in _list_if_not_list(query['layer'])], axis=0)
            masks.append(layer_mask)
        if 'column' in query:
            column_mask = np.any(
                [self._column_mask(column)
                 for column in _list_if_not_list(query['column'])], axis=0)
            masks.append(column_mask)

        return np.all(masks, axis=0)

    # TODO: compose
    def _layer_mask(self, layer):  #
        # TODO: auto-detect on initialization?
        return self._atlas.get_region_mask(
            "@{}$".format(layer), attr="acronym").raw

    def _region_mask(self, region):
        warn(Warning("{} ignores 'region' as it is not relevant to O1 atlas"
                     .format(self)))
        return self._atlas.get_region_mask("O1").raw

    def _column_mask(self, column):
        return self._atlas.get_region_mask(column + "_Column").raw

    # TODO: compose
    #def _cell_density_filename(self, extension):
    #    return extension
    # def _cell_density_filename(self, extension):
    #      return '[cell_density]' + extension

    # # TODO: compose
    # def _density_types(self):
    #     import glob
    #     import os
    #     all_nrrds = glob.glob(os.path.join(self._atlas.dirpath, "*.nrrd"))
    #     all_nrrds = [os.path.basename(nrrd).split(".")[0] for nrrd in all_nrrds]
    #     all_nrrds = [nrrd.split("[cell_density]")[1] if nrrd.startswith("[cell_density]") else nrrd
    #                 for nrrd in all_nrrds]
    #     excluded = ['brain_regions', 'orientation', '[PH]y', 'height', 'distance', 'relative_distance', 'depth'] \
    #     + ['[PH]{}'.format(i) for i in range(1, 7)]\
    #     + ['thickness:L{}'.format(i) for i in range(1, 7)]\
    #     + ["EXC", "INH"]

    #     density_nrrds = [nrrd for nrrd in all_nrrds if nrrd not in excluded]
    #     return density_nrrds

    def cell_density(self, query):
        warn(Warning("{} atlas has no cell density, returning NaN"
                     .format(self)))
        return np.nan

    # def cell_density(self, query):
    #     mask = self.mask_for_query(query)
    #     sclass = query.get('sclass', ['EXC', 'INH'])
    #     if isinstance(sclass, str):
    #         sclass = [sclass]
    #     density_types = self._density_types()

    #     return sum(
    #         self._atlas.load_data(self._cell_density_filename(dtype)).raw[mask]
    #         for dtype in sclass)#density_types)


# translate layer
def column_semicolon_int(self, layer):
    return "@;{}$".format(layer[1]), "acronym"
