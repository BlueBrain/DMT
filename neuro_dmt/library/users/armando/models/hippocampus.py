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
            column_cell_query\
                = {k: v for k, v in cell_type.items()}
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
                layer_cell_query\
                    = {k: v for k, v in cell_type.items()}
                layer_cell_query.update({
                    "layer": layer})
                return layer_cell_query

            layers_cells\
                = [gid for layer in layers
                   for gid in circuit.cells.ids(
                           __layer_cell_query(
                               layer))]
            column_layer_atlas_ids\
                = column_atlas_ids.intersection(
                    layers_atlas_ids)
            column_layer_cells\
                = np.intersect1d(
                    column_cells,
                    layers_cells)
            return(1.e6 *
                   len(column_layer_cells) /
                   brain_regions.volume(
                       column_layer_atlas_ids))

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

    def get_bouton_density(self, circuit, sample):
        """get bouton density"""
        mtypes = circuit.cells.mtypes
        data = pd.DataFrame(index=mtypes, columns=np.arange(sample)+1)
        for mtype in mtypes:
            gids = circuit.cells.ids(group={Cell.MTYPE: mtype,
                                            Cell.REGION: '@mc2.*'},
                                     limit=sample)

            data.loc[mtype][:len(gids)]\
                = circuit.stats.sample_bouton_density(
                    sample, group=gids, synapses_per_bouton=1.2)

        return data, mtypes

    def get_syns_per_conn(self, circuit, nsample=10):

        mtypes = circuit.cells.mtypes
        model_mean = pd.DataFrame(index=mtypes, columns=mtypes, dtype=float)
        model_std = pd.DataFrame(index=mtypes, columns=mtypes, dtype=float)

        for pre_mtype in mtypes:
            for post_mtype in mtypes:
                pre = circuit.cells.ids(group={Cell.MTYPE: pre_mtype,
                                               '$target': 'mc2_Column'},
                                        limit=nsample)

                post = circuit.cells.ids(group={Cell.MTYPE:  post_mtype})
                data = circuit.stats.sample_pathway_synapse_count(nsample,
                                                                  pre=pre,
                                                                  post=post)
                # only pre cells from cylinder

                model_mean[post_mtype][pre_mtype] = data.mean()
                model_std[post_mtype][pre_mtype] = data.std()

        ###############################################
        # TODO does this code actually do anything? ##
        pre = circuit.cells.ids(group={Cell.MTYPE: 'SP_PC',
                                       '$target': 'mc2_Column'})
        post = circuit.cells.ids(group='SP_PC')
        data = circuit.stats.sample_pathway_synapse_count(1000,
                                                          pre=pre,
                                                          post=post)
        # only pre cells from cylinder# only pre cells from cylinder
        #############################################
        return model_mean, model_std

    def get_number_connections(self, circuit):

        mtypes = circuit.cells.mtypes
        means = pd.DataFrame(index=mtypes, columns=mtypes, dtype=float)
        stds = pd.DataFrame(index=mtypes, columns=mtypes, dtype=float)
        max_nsample = 10

        for pre in mtypes:
            for post in mtypes:
                pre_gids = circuit.cells.ids(group={Cell.MTYPE: pre,
                                                    '$target': 'mc2_Column'},
                                             limit=max_nsample)

                post_gids = circuit.cells.ids(group={Cell.MTYPE: post,
                                                     '$target': 'Mosaic'})
                data = circuit.stats.sample_divergence(pre=pre_gids,
                                                       post=post_gids,
                                                       by='conn')
                means[post][pre] = data.mean()
                stds[post][pre] = data.std()
        return means, stds, mtypes

    def get_conn_to_PC_INT(self, means, mtypes):

        conn_pc = means.SP_PC
        conn_int = (means.sum(axis=1) - means.SP_PC)
        connections = pd.DataFrame(index=mtypes)
        connections['model_PC'] = conn_pc.values
        connections['model_INT'] = conn_int.values
        connections['model_UN'] = 0.0
        # quick hack to combine same cell type from different layers
        connections.loc['S_BS'] = connections.loc[['SP_BS', 'SO_BS']].mean()
        connections.drop(['SP_BS', 'SO_BS'], inplace=True)
        connections.rename(lambda x: x.split('_')[1], inplace=True)
        return connections

    def get_n_eff_syns(self, circuit):
        max_nsample = 10
        mtypes = circuit.cells.mtypes
        means = pd.DataFrame(index=mtypes, columns=mtypes, dtype=float)
        stds = pd.DataFrame(index=mtypes, columns=mtypes, dtype=float)
        for pre in mtypes:
            for post in mtypes:
                pre_gids = circuit.cells.ids(group={Cell.MTYPE: pre,
                                                    '$target': 'Mosaic'})
                post_gids = circuit.cells.ids(group={Cell.MTYPE: post,
                                                     '$target': 'mc2_Column'},
                                              limit=max_nsample)


                data = circuit.stats.sample_convergence(pre=pre_gids,
                                                        post=post_gids,
                                                        by='syn')
                means[post][pre] = data.mean()
                stds[post][pre] = data.std()


        conn_pc = means.loc['SP_PC',:]
        conn_int = (means.sum(axis=0) - means.loc['SP_PC',:])
        connections = pd.DataFrame(index=mtypes)
        connections['model_PC'] = conn_pc.values
        connections['model_INT'] = conn_int.values

        connections.loc['S_BS'] = connections.loc[['SP_BS', 'SO_BS']].mean()
        connections.drop(['SP_BS', 'SO_BS'], inplace=True)

        connections.rename(lambda x: x.split('_')[1], inplace=True)
        connections['model_tot'] = connections['model_PC']\
                                   + connections['model_INT']

        return connections
