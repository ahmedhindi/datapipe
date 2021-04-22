import pandas as pd
from typing import List, Dict, Callable, Union, Type
import time

procfunction = Union[Callable, List[Callable]]


class Processor:
    def __init__(
        self, name: str, dev: procfunction, prod: procfunction = None, new_name: str = None, test: bool = False
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
            data[self.new_name] = Processor.run_functions(
                data, self.name, self.dev)
        else:
            data[self.new_name] = Processor.run_functions(
                data, self.name, self.prod)
        return data
