"""Test develop Measurement."""
import numpy as np
import pandas as pd
from dmt.vtk import measurement

def test_summary_statistic():
    """Test measurement.summary_statistic."""
    df = pd.DataFrame(dict(layer=4*[1,2,3],
                           gayer=6*['a', 'b'],
                           x=np.random.random(12),
                           y=np.random.random(12)))

    print(measurement.summary_statistic(df,
                                        parameter_columns = ['layer', 'gayer'],
                                        measurement_columns=['x', 'y']))

    print(measurement.summary_statistic(df,
                                        parameter_columns=['layer', 'gayer'],
                                        measurement_columns=['x']))

    print(measurement.summary_statistic(df,
                                        parameter_columns=['layer'],
                                        measurement_columns=['x']))

