from .collection import TermCollection
from . import Term


class data(TermCollection):
    samples = Term('samples', 'individual samples of a measurement')
    mean = Term('mean', 'the mean of some samples')
    std = Term('std', 'the standard deviation in some samples')
    nsamples = Term('nsamples', 'the number of samples')
    terms =(
        samples,
        mean,
        std,
        nsamples)
