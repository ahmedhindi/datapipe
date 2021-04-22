import pandas as pd
from pytest import fixture


@fixture(scope='module')
def simple_data():
    return pd.DataFrame(
        {"first": [1, 2, 3, 4, 5, 6, 7, 8, 9],
         "second": [1, 2, 3, 4, 5, 6, 7, 8, 9]}
    )
