"""Utilities for circuit composition by layer."""
from pathlib import Path
import numpy as np
from dmt.vtk.judgment.verdict import Verdict
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

def get_verdict(p_value, threshold):
    """Did the validation pass?
    Should we move this function somewhere more general?"""
    if np.isnan(p_value):
        return Verdict.NA
    if p_value > threshold:
        return Verdict.PASS
    if p_value <= threshold:
        return Verdict.FAIL
    return Verdict.INCONCLUSIVE

def plot_bars(plotting_datas, *args, **kwargs):
    """A method to plot data. Bars will be plotted in order passed
        in list 'plotting_data'.

        Parameters
        ------------------------------------------------------------------------
        plotting_datas :: [Measurement] #list of measurements to be plotted

        Return
        ------------------------------------------------------------------------
        Directory path where plots are saved.

        Implementation Note
        ------------------------------------------------------------------------
        For now we let 'Measurement' be a record: 

        Measurement = Record(measurement_label :: String,
        ~                    region_label :: String,
        ~                    data :: DataFrame["region", "mean", "std"])

        We assume that each Measurement.data has the same columns,
        and the same index.
        For example, if we are analyzing composition by cortical layer, each
        Measurement.data should have the index
        ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']. The DataFrame may bave NaNs.
        """
    if len(plotting_datas) == 0:
        raise ValueError(
            "Cannot plot without data, len(plotting_datas) == 0 "
        )
    output_dir_path = kwargs.get('output_dir_path', None)
    plot_customization = kwargs.get('plot_customization', {})
    legend_loc = plot_customization.get('legend_loc', 'upper_left')
    fheight = plot_customization.get('fheight', 10)
    fwidh = plot_customization.get('fwidth', None)
    color = plot_customization.get('colors',
                                       ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'])
    file_name = kwargs.get('file_name', None)

    try:
        title = kwargs['title']
    except:
        raise RequiredKeywordArgumentError("title")
    fig = golden_figure(fheight=fheight, fwidth=fwidth)

    nbar = len(plotting_datas)
    width = 1.0 / (1.0 + nbar)
    #expecting region_label to be same for all plotting_datas 
    region_label = plotting_datas[0].region_label 
    region_names = list(plotting_datas[0].index)
    x = np.arange(len(region_names))
    x0 = x - (nbar / 2) * width
    
    plot_index = 1
    for pe in plotting_datas:
        df = pe.data.fillna(0.0)
        a_plot = plt.bar(x0 + plot_index * width,
                         df['mean'].values,
                         width,
                         color=color[(plot_index - 1) % len(colors)],
                         yerr=df['std'].values,
                         label=pe.label)
        plot_index += 1

    plt.title(title, fontsize=24)
    plt.xlabel(region_label, fontsize=20)
    plt.xticks(x - width / 2., region_names)

    fontP = FontPropertis()
    fontP.set_size('small')
    plt.legend(prop=fontP, loc=legend_loc)

    if output_dir_path and file_name:
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)
        output_file = os.path.join(output_dir_path, file_name + ".png")
        print("Generating {}".format(output_file))
        pylab.savefig(output_file, dpi=100)
        return output_file

    return None

def save_report(report,
                template_dir_name,
                template_file_name='report_html_template.cheetah',
                entry_template_file_name=None, #'entry_html_template.cheetah',
                output_path=None):
    """Save a validation report to the disk.
    Parameters
    ----------------------------------------------------------------------------
    @report :: Report # containing relevant attributes
    @output_path :: File in which the report is to be saved.
    ----------------------------------------------------------------------------
    Return
    ----------------------------------------------------------------------------
    A Cheetah template that can be saved to the disk.
    ----------------------------------------------------------------------------
    Implementation Note
    ----------------------------------------------------------------------------
    We include this 'save_report' method here ---- so far this is the only
    reporting method we have, and the only template that this function uses.
    We will provide tools to assist the user to create their own templates, and
    reporting styles, that they can then share.
    """


    template_dir = Path(template_dir_name)
    if not template_dir.is_dir():
        raise Exception("""Not a directory 'template_path'.
        Provide a valid path to the directory where the Cheetah Templates lie.
        """)

    template_file = Path(template_dir_name, template_file_name)

    if not template_file.is_file():
        raise Exception(
            "Not Found Required file {} in the indicated directory {}"\
            .format(template_file_name, template_dir_name)
        )
            
    with open(template_file, 'r') as file:
        template_str = file.read()

    try:
        template = Template(template_str)
    except:
        raise Exception("Could not load template from file {}"\
                        .format(template_file))

    template.image_path = report.validation_image_path
    template.caption = report.caption
    template.datasets = {label: data.metadata
                         for label, data in report.datasetes.iteritems()}
    template.p_value = report.p_value
    template.is_pass = report.is_pass
    template.name = report.name
    template.author = report.author

    print("Saving {}".format(output_path))

    with open(output_path, 'w') as f:
        f.write(str(template))

    entry_template_str = """<tr>
    <td><a href="$uri">$name</a></td>
    #if $is_pass:
    <td><font color="#00FF00">passed</font></td>
    #else
    <template.><font color="#FF0000">failed</font></td>
    #end if
    <td>p=$p_value</td>
    <td>$author</td>
    </td>"""
    entry_template = Template(entry_template_str)
    entry_template.uri = report.name + 'report.html'
    entry_template.p_value = report.p_value
    entry_template.is_pass = report.is_pass
    entry_template.name = report.name
    entry_template.author = str(report.author)

    return str(entry_template)

