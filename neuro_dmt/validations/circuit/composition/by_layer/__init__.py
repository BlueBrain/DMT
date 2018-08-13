"""Utilities for circuit composition by layer."""
import pandas as pd
import numpy as np
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field, document_fields
from neuro_dmt.validations.circuit.composition.by_layer.validation_report \
    import CompositionReport


@document_fields
class CompositionPhenomenonValidation:
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
        """Is a measurement with p-value p valid?

        Parameters
        ------------------------------------------------------------------------
        p :: Float #p value of an experimental measurement.
        """
        if np.isnan(p):
            return Verdict.NA
        if p > self.p_value_threshold:
            return Verdict.PASS
        if p <= self.p_value_threshold:
            return Verdict.FAIL
        return Verdict.INCONCLUSIVE

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
