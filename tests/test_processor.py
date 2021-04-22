
import pandas as pd
from dukto.pipe import Pipe
from dukto.processor import Processor


def test_basic_functionality():
    data = pd.DataFrame(
        {"first": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "second": [1, 2, 3, 4, 5, 6, 7, 8, 9]}
    )

    first = Processor(name="first", dev=[lambda x: x * 2, lambda x: x * 5])
    second = Processor(name="second", dev=lambda x: x * 2)

    pipeline = Pipe(data=data, pipeline=[first, second], mode="dev")
    pipeline.run()

    prod = pd.DataFrame(
        {"first": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "second": [1, 2, 3, 4, 5, 6, 7, 8, 9]}
    )

    first1 = Processor(name="first", dev=[
                       lambda x: x * 3], prod=lambda x: x - 5)
    second1 = Processor(name="second", dev=lambda x: x * 2)

    pipeline1 = Pipe(data=data, pipeline=[first1, second1], mode="prod")
    pipeline1.run()
