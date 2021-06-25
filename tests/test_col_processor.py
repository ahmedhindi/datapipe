import numpy as np
import pandas as pd
from dukto.pipe import Pipe
from dukto.processor import ColProcessor, MultiColProcessor, Transformer
from hypothesis.extra.pandas import column, columns, data_frames, indexes, range_indexes, series
from hypothesis.strategies import datetimes, floats, integers, text
from pytest import fixture

from utils import convert_foot_to_cm, convert_inch_to_cm, num_of_num_to_perc, pounds_to_kg


@fixture()
def sample_data():
    return pd.read_csv("tests/data/test_ufc.csv")


def test_fixture(sample_data):
    assert len(sample_data) > 0
    assert len(sample_data.shape) == 2


def test_colprocessor_one_col_one_func_and_rename(sample_data):
    """
    one col and one func
    """
    single_pipe = [
        ColProcessor(
            name="agg_weight_first",
            new_name={"agg_weight_first": "weight_class"},
            funcs=pounds_to_kg,
            suffix="_new",
            drop=True,
        ),
    ]
    pipe = Pipe(data=sample_data, pipeline=single_pipe, run_test_cases=False)
    res = pipe.run()
    assert "weight_class_new" in res.columns
    assert res.weight_class_new.dtype == float
    assert res.weight_class_new.isna().sum() == 2


def test_colprocessor_one_col_n_funcs(sample_data):
    single_pipe = [
        ColProcessor(
            name="agg_weight_first",
            new_name={"agg_weight_first": "weight_class"},
            funcs=[pounds_to_kg, lambda x: int(x) if not np.isnan(x) else 0],
            suffix="_new",
            drop=True,
        ),
    ]
    pipe = Pipe(data=sample_data, pipeline=single_pipe, run_test_cases=False)
    res = pipe.run()
    assert "weight_class_new" in res.columns
    print(res.weight_class_new)
    assert res.weight_class_new.dtype == np.int64
    assert res.weight_class_new.isna().sum() == 0


def test_many_processors_case(sample_data):
    single_pipe = [
        ColProcessor(
            name=["agg_height_first", "agg_height_second"],
            funcs=[convert_foot_to_cm],
            suffix="_new",
        ),
        ColProcessor(
            name=["agg_reach_first", "agg_reach_second"], funcs=[convert_inch_to_cm], suffix="_new",
        ),
        ColProcessor(
            name=["second_total_str", "first_total_str"],
            funcs=[num_of_num_to_perc],
            suffix="_%%_new",
        ),
        ColProcessor(name=["agg_dob_first", "agg_dob_second", "date_card"], funcs=[pd.to_datetime]),
        ColProcessor(
            name="agg_weight_first",
            new_name={"agg_weight_first": "weight_class"},
            funcs=[pounds_to_kg, lambda x: int(x) if not np.isnan(x) else 0],
            suffix="_new",
            drop=True,
        ),
    ]

    pipe = Pipe(data=sample_data, pipeline=single_pipe, run_test_cases=False)
    res = pipe.run()
    assert all(
        [
            pd.api.types.is_numeric_dtype(i)
            for i in res[[i for i in res.columns if "new" in i]].dtypes.values
        ]
    )
    assert res[[i for i in res.columns if "new" in i]].isna().sum().sum() == 11


def test_simple_multicolprocessor():
    pass


def test_advanced_multicolprocessor():
    pass


def test_simple_transformer():
    pass


def test_advanced_transformer():
    pass
