We present a framework and library to help with analyzing models and
validating them against empirical data.

# Philosophy

DMT decouples scientific computer models from *in-silico* analyses, such
that any analysis can be run on any model to which it is applicable, and
any model can be analyzed by all applicable analyses.

# Usage

``` python
from dmt import AdapterInterface 

class SomeValueAnalysisInterface(AdapterInterface):
    """
    Methods documented in this class must be provided
    by an adapter.
    """
    def get_somevalue(self, model):
      """
      Get some value for a model.
      """
      raise NotImplementedError

def some_value_analysis(model, adapter, threshold=123456):
  """
  Analysis for a model using a given adapter.
  An analysis may be a simple function.
  """
    model_prediction = adapter.get_somevalue(model)
    report = dict(
        measurement=model_prediction,
        verdict=model_prediction > threshold)
    return report
```

then

``` python
from models import MyModel, TheirModel
from analyses import SomeValueAnalysis

my_model = MyModel()
their_model = TheirModel()

class InvalidAdapter():
   pass

class MyModelAdapter():

   def get_somevalue(self, model):
       return model.something / model.someotherthing

class TheirModelAdapter():

   def get_somevalue(self, model):
       return model.get_somevalue('someparameter')

# produces a report
report_mine = some_value_analysis(my_model, MyModelAdapter())
# produces a report
report_theirs = some_value_analysis(their_model, TheirModelAdapter())
# raises an informative error
some_value_analysis(InvalidAdapter())
```

# Installation

Download the repository, `cd` to it's directory, and

    pip install  .
    
# Funding & Acknowledgment
 
The development of this software was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government's ETH Board of the Swiss Federal Institutes of Technology.
 
Copyright © 2020-2022 Blue Brain Project/EPFL
