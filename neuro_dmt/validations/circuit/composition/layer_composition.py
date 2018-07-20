"""Utilities for circuit composition by layer."""
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError

def probability_of_validity(real_measurement, model_measurement):
    """What is the probability that model's measurement is valid?
    Parameters
    ----------
    @real_measurement :: Record{ data  :: DataFrame<region, mean, std>,
    ~                            label :: String }
    @model_measurement :: Record{ data  :: DataFrame<region, mean, std>,
    ~                             label :: String }
    -------------------------------------------------"""
    from dmt.vtk.statistics import FischersPooler
    def pvalue(mean_1, std_1, mean_2, std_2):
        combined_std = np.sqrt(std_1 ** 2 + std_2 ** 2)
        zscore = np.abs(mean_2 - mean_1) / combined_std
        return 1. - erf(zscore)
    
    delta_mean = np.abs(model_measurement.data.mean -
                        real_measurement.data.mean)
    std = np.sqrt(real_measurement.data.std ** 2 +
                  model_measurement.data.std ** 2)
    region_p_values = pd.DataFrame(dict(
        region=real_measurement.data.index,
        delta_mean=delta_mean,
        std=std,
        z_score=delta_mean/std,
        p_value=1.-erf(z_score)
    ))

    return {
        'p_value_by_region': region_p_values,
        'pooled': FischersPooler.eval(region_p_values.p_value)
    }

def plot_comparison(plotting_datas, **kwargs):
    """Plot bars for measurements of real and model systems.
    Bars will be plotted in the order of the list @plotting_datas.
    
    Parameters
    ----------
    @plotting_datas :: [Measurement] #list of measurements to be plotted
    
    Implementation Notes
    -------
    In the current implementation we assume that a Measurement is a
    dmt.vtk.collections.Record[data :: DataFrame, label :: String].
    
    Return
    ----------
    DirectoryPath #where plots are saved

    Question
    ----------
    Should we define @plotting_datas to be a list of tuples
    (MeasurableSystem, DataFrame), where MeasurableSystem may be a model or
    (experimental) data-object?

    Notes
    ----------
    It is assumed that each Measurement.data in 'plotting_datas' has the same
    format, and the same index.
    For example, if we are analyzing composition by cortical layer,
    each Measurement.data should have the index
    ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']. The data-frames may have NaNs.
    """

    if len(plotting_datas) == 0:
        raise ValueError("len(plotting_datas) == 0: " +
                         "Cannot plot a comparison of no data!!!")

    output_dir_path = kwargs.get('output_dir_path', None)
    plot_customization = kwargs.get('plot_customization', {})
    legend_loc = plot_customization.get('legend_loc', 'upper_left')
    fheight = plot_customization.get('fheight', 10)
    fwidth = plot_customization.get('fwidth', None)

    default_colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
    colors = plot_customization.get('colors', default_colors)
                                    
    file_name = kwargs.get('file_name', None)
    try:
        title = kwargs['title']
    except:
        raise RequiredKeywordArgumentError("title")

    fig = golden_figure(fheight=fheight, fwidth=fwidth)

    nbar = len(plotting_datas)
    width = 1.0 / (1 + nbar)
    x = np.arange(len(region_names))
    x0 = x - (nbar / 2) * width

    plot_index = 1
    for pe in plotting_datas:
        df = pe.data.fillna(0.0)
        a_plot = plt.bar(x0 + plot_index * width,
                         df.mean.values,
                         width,
                         color=colors[(plot_index - 1) % len(colors)],
                         yerr=df.std.values
                         label=pe.label)
        plot_index += 1
        
    plt.title(title + " comparison .", fontsize=24)
    plt.xlabel("Layer", fontsize=20)
    plt.xticks(x - width / 2., region_names)
    
    fontP = FontProperties()
    fontP.set_size('small')
    plt.legend(prop=fontP, loc=legend_loc)
    
    if output_dir_path and file_name:
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)
        output_file_path = os.path.join(output_dir_path, file_name+".png")
        print("Generating {}".format(output_file_path))
        pylab.savefig(output_file_path, dpi=100)
        return output_file_path
    else:
        return None
