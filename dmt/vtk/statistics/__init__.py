"""Statistical methods, and judges."""
from abc import ABC, abstractmethod
import numpy as np
import scipy.stats
from scipy.special import erf
from dmt.vtk.utils.collections import Record

def pooled(pvalues):
    """Pool pvalues and return a Record."""
    return Record(__list__ = pvalues,
                  pooled = FischersPooler.eval(pvalues))

class StatisticalTest(object):
    """A statistical test base class"""

    @abstractmethod
    def eval(self, *args, **kwargs):
        """A common statistical test, should
        return a floating point number (p-value) between 0 and 1.
        Many StatisticalTool implementations should be wrappers around scipy."""
        pass

    def pvalue(self, X, Y):
        """P-Value comparing X and Y.
        Parameters
        ----------
        @X, @Y :: pandas.DataFrame<label, mean, var, std>
        ------------------------------------------
        We could have tried to be more flexible in data we accept as X and Y---
        but that would require writing a lot of exception catching, in order to
        help the user write their logic. To simplify, we explicitly assume that
        the user is familiar with the Python package Pandas. As a result, we do
        not have to worry about exceptions in the data formats sent around. We
        can rely on Pandas to provide meaningful exceptions."""

        combined_stdev = np.sqrt(X.var + Y.var)
        zscore = np.abs(X.mean Y.mean) / combined_stdev
        return 1.0 - erf(zscore)


class PValPooler(StatisticalTool):
    """Statistical tool to handled pools of multiple p-values."""
    pass


class ChiSqFuncTest(StatisticalTest):
    """Test with chi square.
    We use this class as a module!
    Check the probability that a histogram is statistically
    consistent with a PDF
    """
    @classmethod
    def eval(cls, x, freq_observed, std, pdf):
        """
        Parameters
        ----------
        @x :: Float#represents value of a stochastic variable X
        @freq :: Float#(frequency) represents count/freq of a histogram/density
        @std  :: Float#represents standard deviation of X
        @pdf  :: Callable#Probability Distribution Function, pdf(x) = PDF[X = x]
        Return
        ------
        p-value
        """
        delta    = pdf(x) - freq_observed
        residues = (delta/std) ** 2
        chisq    = np.sum(residues)
        return 1. - scipy.stats.chi2.cdf(chisq, len(x))


class ChiSqTest(StatisticalTest):
    """
    Theory
    ------
    If the random variables X_i, i=1,...,n are 
    IID normally distributed, then the sum of their squares
    follows a chi-squared distribution
    with n-1 degrees of freedom"""

    @classmethod
    def eval(cls, freq_expected, freq_observed, std):
        delta = freq_expected - freq_observed
        residues = (delta/std)**2
        chisq = numpy.sum(residues)
        return 1. - scipy.stats.chi2.cdf(chisq, len(freq_observed))


class TwoNormalsTest(StatisticalTest):
    """Chance that two observations are statistically consistent"""

    @classmethod
    def eval(cls, mean1, std1, mean2, std2):
        """
        Parameters
        ----------
        @mean1, @std1 :: Float#statistics of random variate X1
        @mean2, @std2 :: Float#statistics of random variate X2"""

        diff = np.abs(mean1 - mean2)
        stderr = sqrt(std1**2 + std2**2)
        return 1. - erf(diff/stderr/sqrt(2))


class ZTest(StatisticalTest):
    """Chance for the distance of the sample to the mean of the data,
    to be explained by the std of this same data."""
    @classmethod
    def eval(cls, sample, data):
        """Return
        -----------
        p-value"""
        z_value = (sample - data.mean)/data.std
        p_value = 1. - 0.5*(1. + erf(np.abs(z_value)/2**0.5))
        #it makes sense here to assume a 2 sided-pvalue
        #result may deviate in both directions
        p_value = 2*p_value
        return p_value


class ttest(StatisticalTest):
    """Famous Student's t-test"""
    @classmethod
    def eval(cls, model_mean, sample_mean, sample_std, n_sample):
        """Parameters
        -----------------
        @model_mean :: Float#model mean we test against, obtained in a model
        @sample_mean :: Float#mean of a sample from an experiment
        @sample_std :: Float#standard deviation of the experimental sample
        @n_sample :: Float#sample size"""

        sample_mean = np.array(sample_mean)
        sample_std = np.array(sample_std)
        model_mean = np.array(model_mean)

        tt = (sample_mean - model_mean)/(sample_std/np.sqrt(n_sample))
        pval = np.array([scipy.stats.t.sf(np.abs(tt[i]), n_sample-1)*2
                         for i in range(len(tt))])
        cls.statistic = tt
        return pval


class twosamplettest(StatisticalTest):
    """Two sided ttest"""
    @classmethod
    def eval(cls,
             sample_mean_1, sample_std_1, sample_size_1
             sample_mean_2, sample_std_2, sample_size_2):
        """
        Parameters
        ----------
        They are self-explanatory
        -------------------------
        Return
        ----------
        Two sided p-value
        -----------------
        """
        sample_mean_1 = np.array(sample_mean_1)
        sample_mean_2 = np.array(sample_mean_2)
        sample_std_1  = np.array(sample_std_1)
        sample_std_2  = np.array(sample_std_2)
        pooled_std = np.sqrt( sample_std_1 ** 2 / sample_size_1 +
                              sample_std_2 ** 2 / sample_size_2 )

        nume = ( sample_std_1 ** 2 / sample_size_1 +
                 sample_std_2 ** 2 / sample_size_2 ) ** 2
        deno = ( (sample_std_1 ** 2 / sample_size_1)**2 / (sample_size_1 - 1) +
                 (sample_std_2 ** 2 / sample_size_2)**2 / (sample_size_2 - 1) )
        dof  = nume / deno

        tt = (sample_mean_1 - sample_mean_2) / pooled_std
        pval = np.array([scipy.stats.t.sf(np.abs(tt[i]), dof[i]) * 2
                         for i in range(len(tt))])
        cls.statistic = tt
        cls.p_value   = pval
        return pval

class onesamplettest(StatisticalTest):
    """Used when comparing sampled estimate of mean and std,
    with another estimate for which no sample size is known --- but a standard
    error is available. It is equivalent to a the twosamplettest where the
    pooled standard deviation includes a sum of standard error, and degrees of
    freedom is the same of as twosamplettest with second sample size goes to
    infinity (most conservative estimate)
    """

    @classmethod
    def eval(cls,
             sample_mean_1, sample_stddev_1, sample_size_1,
             sample_mean_2, sample_stderr_2):
        """Parameters
        ---------------
        @sample_stddev_1 :: Float#standard deviation for sample 1
        @sample_stderr_2 :: Float#standard error for sample 2
        ----------------------------------------------------------
        Note
        ----
        No sample size for the second sample."""

        sample_mean_1 = np.array(sample_mean_1)
        sample_mean_2 = np.array(sample_mean_2)
        sample_stddev_1 = np.array(sample_stddev_1)
        sample_stderr_2 = np.array(sample_stderr_2)

        pooled_std = np.sqrt( sample_stddev_1 ** 2 / sample_size_1 +
                              sample_stderr_2 ** 2)

        nem = ( sample_stddev_1 ** 2 / sample_size_1) ** 2
        den = ( sample_stddev_1 ** 2 / sample_size_1) ** 2 / (sample_size_1 - 1)
        dof = nem / den

        tt = (sample_mean_2 - sample_mean_1) / pooled_std
        pval = np.array([scipy.stats.t.sf(np.abs(tt[i], dof[i]) * 2)
                         for i in range(len(tt)))]

        cls.statistics = tt
        cls.p_value = pval
        return pval


class FischersPooler(PValPooler):
    """Pool by Fischer's method.
    Pool a list of p-values. According to Fischer's method,
    a combined p-value follows a chi2 distribution with 2n degrees
    of freedom, where n is the number of p-values we want to pool."""

    @classmethod
    def eval(cls, p_values):
        p_values = np.array(p_values)
        logarray = np.log(p_values)
        chisq = -2. * np.sum(logarray)
        pooled_p_value = 1. - scipy.stats.chi2.cdf(chisq, 2 * len(p_values))

        cls.statistic = chisq
        cls.p_value = pooled_p_value
        return pooled_p_value


class MinimumPvaluePooler(PValPooler):
    """Pool p-values such that there combined,
    pooled value is the same as the smallest p value."""
    @classmethod
    def eval(cls, p_values):
        p_values = np.array(p_values)
        return np.min(p_values)






