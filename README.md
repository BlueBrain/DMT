We present a framework and library to help with analyzing models and
validating them against empirical data.

# Philosophy

DMT decouples scientific computer models from *in-silico* analyses, such
that any analysis can be run on any model to which it is applicable, and
any model can be analyzed by all applicable analyses.

# Usage

``` pythons
from dmt_core import AdapterInterface 

class SomeValueAnalysisInterface(AdapterInterface):

    def get_somevalue(self):
    pass

@AnAnalysisInterface()
def SomeValueAnalysis(adapter):
    model_prediction = adapter.get_somevalue()
    threshold = 123456
    report = dict(
    measurement=model_prediction,
    verdict=model_prediction > threshold)
    return report
```

then

``` python
from models import MyModel, TheirModel
from analyses import SomeValueAnalysis

class InvalidAdapter():
   pass

class MyModelAdapter():

   def __init__(model):
       self._model = model

   def get_somevalue(self):
       return self.model.something / self.model.someotherthing

class TheirModelAdapter():

   def __init__(model):
       self._model = model

   def get_somevalue(self):
       return theirmodel.get_somevalue('someparameter')

# produces a report
report_mine = SomeValueAnalysis(MyModelAdapter(MyModel()))
# produces a report
report_theirs = SomeValueAnalysis(TheirModelAdapter(TheirModel()))
# raises an informative error
SomeValueAnalysis(InvalidAdapter())
```

# Installation

Place `dmt` and `neuro_dmt` somewhere in your path.
