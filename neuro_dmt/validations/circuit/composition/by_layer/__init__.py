"""Utilities for circuit composition by layer."""
import pandas as pd
import numpy as np
from dmt.validation.single_phenomemon import SinglePhenomenonValidation
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.utils.collections import Record
from neuro_dmt.validations.circuit.composition.by_layer.validation_report \
    import CompositionReport


class CompositionValidation(SinglePhenomenonValidation):
    """Validation of a single circuit composition phenomenon."""

    region_type = Field(
        __name__ = "region_type",
        __type__ = type,
        __is_valid_vlue__ = lambda rtype: isubclass(rtype, BrainRegion),
        __doc__ = """Composition phenomena are to measured as a function of
        a region type, for example cell density in the cortex as a functionf of
        'CorticalLayer'"""
    )
    def __init__(self, validation_data, *args, **kwargs):
        """
        This validation will be made against multiple datasets. Each dataset
        should provide a 'Record' as specified below.

        Arguments
        ------------------------------------------------------------------------
        validation_data :: List[Record(measurement_label :: String,
        ~                              region_label :: String,
        ~                              data :: DataFrame["region", "mean", "std"])],
        ~                              citation :: Citation,
        ~                              what :: String)]
        ------------------------------------------------------------------------

        Keyword Arguments
        ------------------------------------------------------------------------
        p_value_threshold :: Float #optional
        output_dir_path :: String #optional
        report_file_name :: String #optional
        plot_customization :: Dict #optional
        """

        #add keyword arguments and call super intiialization
        kwargs.update({
            'validation_data': validation_data,
        })
        super(CompositionValidation, self).__init__(*args, **kwargs)

        self.p_value_threshold = kwargs.get('p_value_threshold', 0.05)
        self.output_dir_path = kwargs.get('output_dir_path', os.getcwd())
        self.report_file_name = kwargs.get('report_file_name', 'report.html')
        self.plot_customization = kwargs.get('plot_customization', {})


    @classmethod
    def get_caption(cls, model_measurement):
        """Caption for a plot.
        This method produces a caption from a measurement of the
        model.

        Parameters
        ------------------------------------------------------------------------
        model_measurement :: Record(phenomenon :: Phenomenon#that was measured,
        ~                           label :: String,#used to label the measureemnt
        ~                           region_label :: String,#for regions measured
        ~                           data :: DataFrame["region", "mean", "std"],
        ~                           method :: String #how measurement was made.])
        """
        return "{} is plotted. {}\n Method: {}"\
            .format(model_measurement.phenomenon.title,
                    model_measurement.phenomenon.description,
                    model_measurement.method)

    def plot(self, model_measurement, *args, **kwargs):
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
        plotting_datas = [model_measurement] + self.validation_data
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


    def probability_of_validity(self, model_measurement):
        """Probability that a model measurement is valid.

        Parameters
        ------------------------------------------------------------------------
        model_measurement :: Record(...)
        """
        from dmt.vtk.statistics import FischersPooler
        from scipy.special import erf
        from numpy import abs, sqrt

        real_measurement = self.validated_data[0]
        delta_mean\
            = abs(model_measurement.data.mean - real_measurement.data.mean)
        stdev\
            = sqrt(real_measurement.data.std**2 + model_measurement.data.std**2)
        z_score = delta_mean / stdev
        layer_p_values\
            = pd.DataFrame(dict(
                region = real_measurement.data.index,
                delta_mean = delta_mean,
                std = stdev,
                z_score = z_score,
                p_value = 1. - erf(z_score)
            ))
        return Record(
            p_value_by_region = layer_p_values,
            pooled = FischersPooler.eval(layer_p_values.p_value)
        )

    def get_verdict(self, p):
        """Get verdict for p-value p.

        Parameters
        ------------------------------------------------------------------------
        p :: Float #p value of an experimental measurement.
        """
        pass

    @abstractmethod
    def get_measurement(self, circuit_model):
        """Get the measurement to be validated."""
        pass

    def __call__(self, circuit_model, *args, **kwargs):
        """...Call Me..."""
        output_dir_path = kwargs.get('output_dir_path', self.output_dir_path)
        report_file_name = kwargs.get('report_file_name', self.report_file_name)

        model = self.adapted(circuit_model) #and use model as you wish!
        model_measurement = self.get_measurement(circuit_model)
        model_label = model.get_label()

        p_val = self.probability_of_validity(model_measurement)
        verdict = self.get_verdict(p_val)

        return CompositionReport(
            validated_phenomenon = self.validated_phenomenon.title,
            validated_image_path = self.plot(model_measurement),
            author = self.author,
            caption = self.get_caption(model_measurement),
            validation_datasets = self.validation_data,
            is_pass = verdict == Verdict.PASS,
            is_fail = verdict == Verdict.FAIL,
            p_value = p_val.pooled
        )


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
                         yerr=df.std.values,
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

def save_report(report,
                template_dir_name,
                output_path,
                template_file_name='report_html_template.cheetah',
                entry_template_file_name='entry_html_template.cheetah'):
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

