import numpy as np
import pandas as pd
from dmt.model import interface, adapter
from neuro_dmt.library.users.armando.validations.hippocampus import\
    MtypeCellDensityValidation
from bluepy.v2.enums import Cell, Synapse
from bluepy.v2.circuit import Circuit
from bluepy.utils import take_n

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

        def get_cell_fractions(target):
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
                                        for c in get_cell_fractions(target)]},
                index=pd.MultiIndex.from_tuples(
                    tuples=[(target, mtype)
                            for target in targets for mtype in mtypes],
                    names=["target", "mtype"]))
        return cell_fracs.groupby("mtype")\
                         .agg(["mean", "std"])["cell_fraction"]

    def get_atlas_ids(self,
            atlas,
            column_index,
            *layers):
        """..."""
        rmap = atlas.load_region_map()
        if not layers:
            query = "mc{}".format(column_index)
            return rmap.find(query, 'acronym', with_descendants=True)
        for layer in layers:

            return {
                id for layer in layers
                for id in rmap.find("mc{};{}".format(column_index, layer),
                                'acronym', with_descendants=True)}

    def circuit_regions(self, circuit):
        """why are we passing circuit again?"""
        return range(7)

    def get_cell_density(self,
                         circuit,
                column_index,
                layers=[],
                cell_type={}):
        """..."""
        brain_regions = circuit.atlas.load_data("brain_regions")
        column_atlas_ids\
            = self.get_atlas_ids(circuit.atlas, column_index)

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
            = self.get_atlas_ids(circuit.atlas, column_index, *layers)

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

    def get_laminar_distribution(self, circuit):
        annotation = circuit.atlas.load_data("brain_regions")
        hierarchy = circuit.atlas.load_hierarchy()

        result = circuit.stats.synapse_region_distribution(annotation,
                                                           Synapse.PRE_MTYPE,
                                                           pre={'$target':
                                                                'cylinder'},
                                                           normalize=True)
        mapping = {k: v for v in ['SLM', 'SR', 'SP', 'SO']
                   for k in hierarchy.collect('acronym', v, 'id')}

        result2 = result.groupby(lambda r: mapping.get(r, 'out'),
                                 axis=1).sum()
        cols = ['SO', 'SP', 'SR', 'SLM', 'out']
        result2 = result2[cols]
        result2.index = result2.index.astype(str)
        result2.loc['S_BS'] = result2.loc[['SP_BS', 'SO_BS']].mean()
        result2.drop(['SP_BS', 'SO_BS'], inplace=True)
        result2.rename(lambda x: x.split('_')[1], inplace=True)
        return result2

    def get_syns_conn_dist(self, circuit, pre, post, max_nsample):
        it = circuit.connectome.iter_connections(pre, post,
                                                 return_synapse_ids=True,
                                                 shuffle=True,
                                                 unique_gids=True)
        sample = [conn[2] for conn in take_n(it, max_nsample)]
        nsample = len(sample)

        # if not nsample:
        #     return

        synapse_ids = sum(sample, [])
        nsyns_conn = list(map(len, sample))
        table = circuit.connectome.synapse_properties(
            synapse_ids,
            [Synapse.POST_BRANCH_ORDER,
             Synapse.POST_NEURITE_DISTANCE,
             Synapse.POST_BRANCH_TYPE,
             Synapse.PRE_BRANCH_ORDER,
             Synapse.PRE_NEURITE_DISTANCE])
        return nsample, nsyns_conn, table

    def get_mtypes(self, circuit):
        return circuit.cells.mtypes

    def connection_probability(self, circuit, pre_mtype, post_mtype,
                               distance, nsample):

        def pair_euclidian_distance(circuit, pregid, postgid):
            p0 = circuit.cells.get(pregid, [Cell.X, Cell.Y, Cell.Z]).values
            p1 = circuit.cells.get(postgid, [Cell.X, Cell.Y, Cell.Z]).values
            return np.linalg.norm(p1 - p0)

        connected = 0
        pregids = circuit.cells.ids(pre_mtype, nsample)
        for pregid in pregids:
            # check if the cells are within the defined distance
            distant = True
            while distant:
                postgid = circuit.cells.ids(post_mtype, sample=1)
                if postgid == pregid:
                    pass
                if pair_euclidian_distance(circuit, pregid, postgid)\
                   < distance:
                    distant = False
            if circuit.stats.sample_pathway_synapse_count(1, pre=pregid,
                                                          post=postgid) > 0:
                connected += 1
        return connected/nsample
