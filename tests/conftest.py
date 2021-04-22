import pandas as pd
import pytest


@pytest.fixture(scope="module")
def simple_data():
    rng = list(range(1, 10))
    return pd.DataFrame({"first": rng, "second": rng})
