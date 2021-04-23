from typing import List, Callable, Union, Dict
from pydantic import validate_arguments


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
        test: bool = False,
        suffix: str = "",
    ):
        self.dev = dev
        self.prod = prod if prod else dev
        self.name = name
        self.new_name = new_name if new_name else name
        self.test = test
        self.suffix = suffix

    @staticmethod
    def run_functions(data, name, functions):
        temp = data[name].copy()
        if isinstance(functions, list):
            for f in functions:
                temp = f(temp)
            return temp
        return functions(temp)

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
        print(">>>", self.name)
        for name in self.name:
            print("name", name)
            if mode == "dev":
                data[self.new_name[name] + self.suffix] = Processor.run_functions(
                    data, name, self.dev
                )
            else:
                data[self.new_name[name] + self.suffix] = Processor.run_functions(
                    data, name, self.prod
                )
        return data
