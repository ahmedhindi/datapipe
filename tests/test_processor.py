from dukto.processor import Processor
from dukto.pipe import Pipe


def test_single_processor(simple_data):
    first = Processor(name="first", dev=[lambda x: x * 2, lambda x: x * 5])
    pipeline = Pipe(data=simple_data, pipeline=[first], mode="dev")
    assert (pipeline.run()["first"] == (simple_data["first"] * 10)).all()


def test_multi_processor(simple_data):
    first = Processor(name="first", dev=[lambda x: x * 3], prod=lambda x: x - 5)
    second = Processor(name="second", dev=lambda x: x * 2 + 2)

    pipeline = Pipe(data=simple_data, pipeline=[first, second], mode="dev")
    assert (pipeline.run()["first"] == ((simple_data["first"] * 3))).all()
    assert (pipeline.run()["second"] == (simple_data["second"] * 2 + 2)).all()


def test_dev_prod(simple_data):
    """
    test the production and development
    """
    first = Processor(name="first", dev=[lambda x: x * 3], prod=lambda x: x - 5)
    second = Processor(name="second", dev=lambda x: x * 2 + 2)

    # dev pipeline
    dev_pipeline = Pipe(data=simple_data, pipeline=[first, second], mode="dev")
    assert (dev_pipeline.run()["first"] == ((simple_data["first"] * 3))).all()
    assert (dev_pipeline.run()["second"] == (simple_data["second"] * 2 + 2)).all()

    # prod_pipeline
    prod_pipeline = Pipe(data=simple_data, pipeline=[first, second], mode="prod")
    assert (prod_pipeline.run()["first"] == ((simple_data["first"] - 5))).all()
    assert (prod_pipeline.run()["second"] == (simple_data["second"] * 2 + 2)).all()


def test_multi_cols(simple_data):
    """
    test the production and development
    """
    suffix = "_new"
    first = Processor(
        name=["first", "second"], dev=[lambda x: x * 3], prod=lambda x: x - 5, suffix=suffix,
    )

    # dev pipeline
    dev_pipeline = Pipe(data=simple_data, pipeline=[first], mode="dev")
    assert (dev_pipeline.run()["first" + suffix] == ((simple_data["first"] * 3))).all()
    assert (dev_pipeline.run()["second" + suffix] == ((simple_data["second"] * 3))).all()


def test_tests():
    # TODO : add test cases to testing
    pass
