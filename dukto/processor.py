"""
! TODO:
    we should have diffrent modes of running one for fit_transform and the other is for transforming
    in case we used fitting we should learn about the distributions of the data
    ideas:
        I-
            1- add mode parameter to the transformers and pass the through
            the Pipe class
            2-incase of fit we should use fit_tras... other wide we should use transform

        II- turn the pipeline into an sklearn style transformer
        

"""


from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd
from pandera.typing import DataFrame
from pydantic import validate_arguments

from dukto.base_processor import BaseProcessor
from dukto.cus_types import col_names, new_names, proc_function
from dukto.logger import logger

from sklearn.utils.validation import check_is_fitted
import inspect


def is_fitted(model):
    """Checks if model object has any attributes ending with an underscore"""
    return 0 < len(
        [k for k, v in inspect.getmembers(model) if k.endswith("_") and not k.startswith("__")]
    )


class ColProcessor(BaseProcessor):
    @validate_arguments
    def __init__(
        self,
        name: col_names,
        funcs: proc_function,
        new_name: new_names = None,
        funcs_test: Dict[Any, Any] = {},
        run_test_cases: bool = False,
        suffix: str = "",
        drop: bool = False,
    ):
        self.funcs = funcs if isinstance(funcs, list) else [funcs]
        self.name = [name] if isinstance(name, str) else name
        self.new_name = new_name if new_name else name
        self.funcs_test = funcs_test
        self.suffix = suffix
        self.run_test_cases = run_test_cases
        self.drop = drop

    def run_functions(self, data: DataFrame, name: str):
        temp_series = data[name].copy(deep=True)
        for func in self.funcs:
            print(f"Running{func.__name__}({name})")
            temp_series = temp_series.apply(func)
        return temp_series.values

    def types(self):
        # if new_name is not provided  use name(s)
        if self.new_name == self.name:
            self.new_name = {n: n for n in self.name}

        # make sure if name is a list new_name is a dict
        # if isinstance(self.name, List) and isinstance(self.new_name, str):
        #     raise TypeError(
        #         f"""if you're applying the ColProcessor to many columns
        #         new_name should be of type dict not {type(self.new_name)}
        #         Example(new_name={{"name":"new_name"}})"""
        #     )

        if isinstance(self.name, str):  # check if name is string and if so turn it into a list
            self.name = [self.name]

        # check if new name is a string and if so turn into a dict
        if isinstance(self.new_name, str):
            self.new_name = {self.new_name: self.new_name}

        # update new_name and use the name for the missing new_name(s)
        if isinstance(self.new_name, dict):
            not_in = set(self.name) - set(self.new_name.keys())
            self.new_name.update({n: n for n in not_in})

    # @log_step
    def run(self, data: DataFrame, **kwargs) -> DataFrame:
        self.types()

        for n in self.name:
            new_name = self.new_name[n] if isinstance(self.new_name, dict) else self.new_name
            data[new_name + self.suffix] = self.run_functions(data, n)

        return data.drop(self.name, axis=1) if self.drop else data

    def test_res_printer(self, res: Optional[int] = None) -> None:
        class_name = self.__class__.__name__
        cols = ColProcessor.name_formatter(self.name)
        if res == None:  # no tests
            print(f"{class_name: <2} {cols: <30} test cases NOT FOUND.")
        elif res == 0:  # failed
            print(f"{class_name: <2} {cols: <30} test cases Failed! 😒")
        elif res == 1:
            print(f"{class_name: <2} {cols: <30} test cases PASSED! 😎")

    def test(self):
        # TODO: {"input": np.nan}  doesn't work
        # TODO: refactor this function
        # TODO: show the failing cases
        # TODO: tests fail if we changed the name of the Column (try to run the test in the pipe after the run mathod)
        data = pd.Series(data=self.funcs_test).to_frame().reset_index()
        data.columns = ["in", "out"]
        out_val = self.run_functions(data, "in")
        mismatches = data[data["out"] != out_val]
        if not self.funcs_test:
            self.test_res_printer()
        elif mismatches.empty:  # if empty them all cases matched
            self.test_res_printer(res=1)
        else:
            self.test_res_printer(res=0)
            print("=>", mismatches)

    @staticmethod
    def name_formatter(name):
        return f"({', '.join(name) if isinstance(name, list) else name})"

    def __repr__(self):
        return f"ColProcessor({', '.join(self.name)})"


class MultiColProcessor(BaseProcessor):
    ## TODO: add testing
    @validate_arguments
    def __init__(self, funcs: List, funcs_test: Dict = {}, name: Union[List, str] = ""):
        self.funcs = funcs
        self.funcs_test = funcs_test
        self.name = [name] if isinstance(name, str) else name

    # @log_step
    def run(self, data: DataFrame, **kwargs) -> DataFrame:
        self.__before = set(data.columns.unique())
        for f in self.funcs:
            data = data.pipe(f)
        self.__after = set(data.columns.unique())
        self.col_mutations(self.__before, self.__after)
        return data

    def test(self):
        print("Multi test not implemented yet")

    @staticmethod
    def col_mutations(before, after):
        # added_cols
        added = [i for i in after if i not in before]
        deleted_cols = [i for i in before if i not in after]
        print(f"added columns {added}... deleted columns {deleted_cols}")

    def __repr__(self):
        return f"MultiColProcessor({', '.join(self.name)})"


class Transformer(BaseProcessor):
    # TODO: add testing
    # TODO: name_from_func use suffix to select columns
    # example: name_from_func=lambda x:[i for i in x if '_new' in i]
    @validate_arguments
    def __init__(
        self,
        transformers: Union[List, Callable],
        name: Union[str, List, None] = None,
        name_from_func: Optional[Callable] = None,
        mode: str = "fit_transform",
        **kwargs,
        # TODO add parser for kwargs in case there's more than one Transformer
    ):
        """
        Transformer Class.

        Parameters
        ----------
        transformers : Union[List, Callable]
            sklearn or feature-engine style transformers 
        name : Union[str, List, None], optional
            name
        name_from_func : Optional[Callable], optional
            [description], by default None
        modes : str, optional
            can be transform, or fit_transform. 
        """ """"""
        self.transformers = [transformers] if isinstance(transformers, Callable) else transformers
        self.name = [name] if isinstance(name, str) else name
        self.name_from_func = name_from_func
        self.mode = mode
        self.kwargs = kwargs

    def run(self, data: DataFrame, mode, **kwargs) -> DataFrame:
        if self.name_from_func:
            self.name = self.name_from_func(data.columns.tolist())
        for ind, t in enumerate(self.transformers):
            if mode.lower() == "fit_transform":
                trans = t(variables=self.name, **self.kwargs)
            elif mode.lower() == "transform":
                trans = t
            else:
                raise ValueError("mode can only be fit_transform or transform")

            if mode == "fit_transform":
                data = trans.fit_transform(X=data)
                self.transformers[ind] = trans
            elif mode == "transform":
                if is_fitted(trans):
                    data = trans.transform(X=data)
                else:
                    print(f"The transformer {trans} wasn't fitted. fit_transform was used")
                    data = trans.fit_transform(X=data)

        return data

    def test(self):
        print("transformer test not implemented yet")

    def __repr__(self):
        # TODO add more informative repr and __str__ cuz this shit sucks
        return f"Transformer()"
