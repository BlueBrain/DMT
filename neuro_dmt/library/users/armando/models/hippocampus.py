import numpy as np
import pandas as pd
from dmt.model import interface, adapter
from neuro_dmt.library.users.armando.validations.hippocampus import\
    MtypeCellDensityValidation
from bluepy.v2.enums import Cell
from bluepy.v2.circuit import Circuit

@adapter.adapter(Circuit)
@interface.implementation(MtypeCellDensityValidation.AdapterInterface)
class HippocampusAdapter:

    def __init__(self, *args, **kwargs):
        pass

    def filter_interneuron_mtypes(self, dataframe):
        """mtypes are supposed to sit in the index of dataframe"""
        mtypes = set(dataframe.index)
        mtypes.remove('SP_PC')  # (sic)
        return mtypes

    def get_mtype_composition(self, circuit):
        """Get fraction of cells of each mtype.
        Cell fraction mean and std are computed over columns (O1 circuit)."""

        mtypes = circuit.cells.mtypes
        targets = ["mc{}".format(idx) for idx in range(7)]

        def __get_cell_fractions(target):
            """..."""
            cell_counts\
                = np.array([
                    len(circuit.cells.ids(
                        group={Cell.MTYPE: mtype,
                               Cell.REGION: "@{}.*".format(target)}))
                    for mtype in mtypes])
            return cell_counts/np.sum(cell_counts)

        cell_fracs\
            = pd.DataFrame(
                data={"cell_fraction": [c for target in targets
                                     for c in __get_cell_fractions(target)]},
                index=pd.MultiIndex.from_tuples(
                    tuples=[(target, mtype)
                            for target in targets for mtype in mtypes],
                    names=["target", "mtype"]))
        return cell_fracs.groupby("mtype")\
                         .agg(["mean", "std"])["cell_fraction"]

    def get_layer_composition(self, circuit):
        """..."""
        atlas = circuit.atlas
        brain_regions = atlas.load_data('brain_regions')
        hierarchy = atlas.load_hierarchy()
        labels = ['CA1', 'SLM-SR', 'SP', 'PC in SP', 'SO']
        df = pd.DataFrame(index=labels, columns=np.arange(7))
        scale = 1.e6

        def __get_atlas_ids(
                column_index,
                *layers):
            """..."""
            if not layers:
                return hierarchy.collect(
                    "acronym", "mc{}".format(column_index), "id")
            return {
                id for layer in layers
                for id in hierarchy.collect(
                        "acronym", "mc{};{}".format(column_index, layer), "id")}

        def __get_cell_density(
                column_index,
                layers=[],
                cell_type={}):
            """..."""
            column_atlas_ids\
                = __get_atlas_ids(column_index)
            column_cell_query = {k: v for k, v in cell_type.items()}
            column_cell_query.update({
                Cell.REGION: "@mc{}.*".format(column_index)})
            column_cells\
                = circuit.cells.ids(column_cell_query)
            if not layers:
                return (1.e6 *
                        len(column_cells) /
                        brain_regions.volume(column_atlas_ids))
            layers_atlas_ids\
                = __get_atlas_ids(column_index, *layers)

            def __layer_cell_query(layer):
                """..."""
                layer_cell_query = {k: v for k, v in cell_type.items()}
                layer_cell_query.update({
                    "layer": layer})
                return layer_cell_query

            layers_cells\
                = [gid for layer in layers
                   for gid in circuit.cells.ids(__layer_cell_query(layer))]
            column_layer_atlas_ids\
                = column_atlas_ids.intersection(
                    layers_atlas_ids)
            column_layer_cells\
                = np.intersect1d(column_cells, layers_cells)
            return(1.e6 *
                   len(column_layer_cells) /
                   brain_regions.volume(column_layer_atlas_ids))

        def __get_cell_density_array(
                layers=[],
                cell_type={}):
            """..."""
            return np.array([
                __get_cell_density(
                    column_index,
                    layers=layers,
                    cell_type=cell_type)
                for column_index in range(7)])

        cell_densities\
            = pd.DataFrame(
                data={"cell_density": np.concatenate([
                    __get_cell_density_array(),
                    __get_cell_density_array(
                        layers=["SLM", "SR"]),
                    __get_cell_density_array(
                        layers=["SP"]),
                    __get_cell_density_array(
                        layers=["SP"],
                        cell_type={Cell.MORPH_CLASS: "PYR"}),
                    __get_cell_density_array(
                        layers=["SO"])])},
                index=pd.MultiIndex.from_tuples(
                    [(column_index, layer_label)
                     for layer_label in ['CA1', 'SLM-SR', 'SP', 'PC in SP', 'SO']
                     for column_index in range(7)],
                    names=["column", "region"]))
        return cell_densities.groupby("region")\
                             .agg(["mean", "std"])["cell_density"]
        #df['sem'] = stds / means
