
import pandas as pd
from dukto import Processor, Pipe


def make_simple_data():
    return pd.DataFrame(
        {"first": [1, 2, 3, 4, 5, 6, 7, 8, 9],
         "second": [1, 2, 3, 4, 5, 6, 7, 8, 9]}
    )


def test_single_processor():
    first = Processor(name="first", dev=[lambda x: x * 2, lambda x: x * 5])
    pipeline = Pipe(data=make_simple_data(), pipeline=[first], mode="dev")
    assert (pipeline.run()['first'] == (make_simple_data()['first']*10)).all()


def test_multi_processor():
    first = Processor(name="first", dev=[
                      lambda x: x * 3], prod=lambda x: x - 5)
    second = Processor(name="second", dev=lambda x: x * 2+2)

    pipeline = Pipe(data=make_simple_data(), pipeline=[
                    first, second], mode="dev")
    assert (pipeline.run()['first'] == (
        (make_simple_data()['first']*3))).all()
    assert (pipeline.run()['second'] == (
        make_simple_data()['second']*2+2)).all()


def test_dev_prod():
    """
    test the production and development 
    """
    first = Processor(name="first", dev=[
                      lambda x: x * 3], prod=lambda x: x - 5)
    second = Processor(name="second", dev=lambda x: x * 2+2)

    # dev pipeline
    dev_pipeline = Pipe(data=make_simple_data(), pipeline=[
        first, second], mode="dev")
    assert (dev_pipeline.run()['first'] == (
        (make_simple_data()['first']*3))).all()
    assert (dev_pipeline.run()['second'] == (
        make_simple_data()['second']*2+2)).all()

    # prod_pipeline
    prod_pipeline = Pipe(data=make_simple_data(), pipeline=[
        first, second], mode="prod")
    assert (prod_pipeline.run()['first'] == (
        (make_simple_data()['first']-5))).all()
    assert (prod_pipeline.run()['second'] == (
        make_simple_data()['second']*2+2)).all()
