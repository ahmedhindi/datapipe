"""

usecase
    hight = processor(name='hight', dev=lambda x*2, prod=lambda x:x*3)
    weight = processor(name='weight, ev=lambda x*2, prod=lambda x:x*8)

    pipeline  = Pipe(data=df, pipeline=[hight, weight])

    pipeline.run()
"""


import pandas as pd
from typing import List, Dict
import time


class Pipe:
    def __init__(
        self,
        data: pd.DataFrame,
        pipeline: List = [],
        mode: str = "dev",
        suffix: str = "",
    ):
        """
        pipeline
        """
        self.pipeline = pipeline
        self.data = data
        self.mode = mode
        self._pipeline_funcs: str = ""
        self.logs: str = ""

    def run(self):
        new_data = self.data.copy()
        for proc in self.pipeline:
            # TODO: timing and logging
            t0 = time.time()
            proc.run(data=new_data, mode=self.mode)
            print(f"running {proc.name} finished in {round((time.time()-t0), 3)} sec")
        return new_data


class Processor:
    def __init__(
        self, name: str, dev, prod=None, new_name: str = None, test: bool = False
    ):
        self.dev = dev
        self.prod = prod if prod else dev
        self.name = name
        self.new_name = new_name if new_name else name
        self.test = test

    @staticmethod
    def run_functions(data, name, functions):
        temp = data[name].copy()
        if isinstance(functions, list):
            for f in functions:
                temp = f(temp)
            return temp
        return functions(temp)

    def run(self, data, mode):
        if mode == "dev":
            data[self.new_name] = Processor.run_functions(data, self.name, self.dev)
        else:
            data[self.new_name] = Processor.run_functions(data, self.name, self.prod)
        return data


# data = pd.DataFrame(
#     {"first": [1, 2, 3, 4, 5, 6, 7, 8, 9], "second": [1, 2, 3, 4, 5, 6, 7, 8, 9]}
# )

# first = Processor(name="first", dev=[lambda x: x * 2, lambda x: x * 5])
# second = Processor(name="second", dev=lambda x: x * 2)


# pipeline = Pipe(data=data, pipeline=[first, second], mode="dev")
# pipeline.run()


# prod = pd.DataFrame(
#     {"first": [1, 2, 3, 4, 5, 6, 7, 8, 9], "second": [1, 2, 3, 4, 5, 6, 7, 8, 9]}
# )

# first1 = Processor(name="first", dev=[lambda x: x * 3], prod=lambda x: x - 5)
# second1 = Processor(name="second", dev=lambda x: x * 2)


# pipeline1 = Pipe(data=data, pipeline=[first1, second1], mode="prod")
# pipeline1.run()
