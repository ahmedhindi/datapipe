from typing import List, Callable, Union, Dict, Any
from pydantic import validate_arguments
import pandas as pd

procfunction = Union[Callable, List[Callable]]
colnames = Union[str, List[str]]
newnames = Union[Dict[str, str], str]


class Processor:
    @validate_arguments
    def __init__(
        self,
        name: colnames,
        dev: procfunction,
        prod: procfunction = None,
        new_name: newnames = None,
        dev_test: Dict[Any, Any] = {},
        prod_test: Dict[Any, Any] = {},
        run_test_cases: bool = False,
        suffix: str = "",

    ):
        self.dev = dev
        self.prod = prod if prod else dev
        self.name = name
        self.new_name = new_name if new_name else name
        self.dev_test = dev_test
        self.prod_test = prod_test if prod_test else dev_test
        self.suffix = suffix
        self.run_test_cases = run_test_cases

    @staticmethod
    def run_functions(data, name, functions):
        temp = data[name].copy()
        if isinstance(functions, Callable):
            functions = [functions]
        elif not isinstance(functions, List):
            raise TypeError(
                'dev and prod arguments can only be of type str and list')
        for f in functions:
            try:
                temp = f(temp)
            except Exception:
                temp = temp.apply(f)
        return temp

    def types(self):
        # if new_name is not provided  use name(s)
        if self.new_name == self.name:
            self.new_name = {n: n for n in self.name}

        # make sure if name is a list new_name is a dict
        if isinstance(self.name, List) and isinstance(self.new_name, str):
            raise TypeError(
                f"""if you're applying the processor to many columns
                new_name should be of type dict not {type(self.new_name)}
                Example(new_name={{"name":"new_name"}})"""
            )

        if isinstance(
            self.name, str
        ):  # check if name is string and if so turn it into a list
            self.name = [self.name]

        # check if new name is a string and if so turn into a dict
        if isinstance(self.new_name, str):
            self.new_name = {self.new_name: self.new_name}

        # update new_name and use the name for the missing new_name(s)
        if isinstance(self.new_name, dict):
            not_in = set(self.name) - set(self.new_name.keys())
            self.new_name.update({n: n for n in not_in})

    def run(self, data, mode):
        self.types()

        for name in self.name:
            # print("name", name)
            if mode == "dev":
                data[self.new_name[name] + self.suffix] = Processor.run_functions(
                    data, name, self.dev
                )
            elif mode == 'prod':
                data[self.new_name[name] + self.suffix] = Processor.run_functions(
                    data, name, self.prod
                )
            else:
                raise ValueError(
                    f'mode can take two values `prod` amd `dev` we got {mode}')
        return data

    def test(self, mode):
        # TODO: refactor this function
        # TODO: show the failing cases
        #         # test if dev
        if self.dev_test and mode == 'dev':
            data = pd.Series(data=self.dev_test).to_frame().reset_index()
            data.columns = ['in', 'out']
            mismatches = data[data['out'] !=
                              Processor.run_functions(data, 'in', self.dev)]
            if mismatches.empty:  # if empty them all cases matched
                print(
                    f"{Processor.name_formatter(self.name)} dev test cases.. PASSED!")
            else:
                print(
                    f"{Processor.name_formatter(self.name)} dev test cases.. Failed! :(")
                print(mismatches)

        # test if prod
        elif self.prod_test and mode == 'prod':
            data = pd.Series(data=self.prod_test).to_frame().reset_index()
            data.columns = ['in', 'out']
            mismatches = data[data['out'] !=
                              Processor.run_functions(data, 'in', self.prod)]
            if mismatches.empty:  # if empty them all cases matched
                print(
                    f"{Processor.name_formatter(self.name)} prod test cases.. PASSED!")
            else:
                print(
                    f"{Processor.name_formatter(self.name)}prod test cases.. Failed! :(")
                mismatches['in_types'] = mismatches['in'].dtypes
                mismatches['out_types'] = mismatches['out'].dtypes
                print(mismatches)
                raise AssertionError(
                    f'test cases for {Processor.name_formatter(self.name)} did not pass')

    @staticmethod
    def name_formatter(name):
        return f"({', '.join(name) if isinstance(name, list) else name})"

    def __repr__(self):
        return f"Processor({', '.join(self.name)})"
