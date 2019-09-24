from dmt.tk.utils.singleton import Singleton
from . import Term


class data(Singleton):
    samples = Term('samples', 'individual samples of a measurement')
    mean = Term('mean', 'the mean of some samples')
    std = Term('std', 'the standard deviation in some samples')
    nsamples = Term('nsamples', 'the number of samples')
