from typing import List, Callable, Union, Dict, Any
from pydantic import validate_arguments
import pandas as pd
from dukto.cus_types import col_names, proc_function, new_names


# TODO: create and ABC class for the main args and the run methode


class ColProcessor:
    @validate_arguments
    def __init__(
        self,
        name: col_names,
        funcs: proc_function,
        new_name: new_names = None,
        funcs_test: Dict[Any, Any] = {},
        run_test_cases: bool = False,
        suffix: str = "",
    ):
        self.funcs = funcs
        self.name = name
        self.new_name = new_name if new_name else name
        self.funcs_test = funcs_test
        self.suffix = suffix
        self.run_test_cases = run_test_cases

    @staticmethod
    def run_functions(data: pd.DataFrame, name: str, functions: Union[Callable, List[Callable]]):
        temp = data[name].copy()
        if isinstance(functions, Callable):
            functions = [functions]
        elif not isinstance(functions, List):
            raise TypeError("funcs argument can only be of type str and list")
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
                f"""if you're applying the ColProcessor to many columns
                new_name should be of type dict not {type(self.new_name)}
                Example(new_name={{"name":"new_name"}})"""
            )

        if isinstance(self.name, str):  # check if name is string and if so turn it into a list
            self.name = [self.name]

        # check if new name is a string and if so turn into a dict
        if isinstance(self.new_name, str):
            self.new_name = {self.new_name: self.new_name}

        # update new_name and use the name for the missing new_name(s)
        if isinstance(self.new_name, dict):
            not_in = set(self.name) - set(self.new_name.keys())
            self.new_name.update({n: n for n in not_in})

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        self.types()

        for name in self.name:
            data[self.new_name[name] + self.suffix] = ColProcessor.run_functions(
                data, name, self.funcs
            )

        return data

    def test(self):
        # TODO: refactor this function
        # TODO: show the failing cases
        #         # test if dev
        data = pd.Series(data=self.funcs_test).to_frame().reset_index()
        data.columns = ["in", "out"]
        mismatches = data[data["out"] != ColProcessor.run_functions(data, "in", self.funcs)]
        if mismatches.empty:  # if empty them all cases matched
            print(f"{ColProcessor.name_formatter(self.name)}  test cases.. PASSED!")
        else:
            print(f"{ColProcessor.name_formatter(self.name)}  test cases.. Failed! :(")
            print(mismatches)

    @staticmethod
    def name_formatter(name):
        return f"({', '.join(name) if isinstance(name, list) else name})"

    def __repr__(self):
        return f"ColProcessor({', '.join(self.name)})"


class MultiColProcessor:
    ## TODO: add testing
    def __init__(self, funcs: List, funcs_test: Dict, name: str = ""):
        self.funcs = funcs
        self.funcs_test = funcs_test
        self.name = name

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        for f in self.funcs:
            temp = data.pipe(f)
        return temp


class Transformer:
    # TODO: add testing
    def __init__(self, name: Union[str, List], transformers: Union[List, Callable]):
        self.transformers = [transformers] if isinstance(transformers, Callable) else transformers
        self.name = [name] if isinstance(name, str) else name

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        for t in self.transformers:
            trans = t(variables=self.name)
            temp = trans.fit_transform(X=data)
            # print(temp)
        return temp


# from dukto.processor import Processor
# from dukto.pipe import Pipe

# # helper function for the grade processor
# def grade_prod_mapper(g):
#     return {'Freshman':"9th",'Sophomore':"10th",'Junior':'11th','Senior':"12th"}[g]

# pipeline = [Processor(name='chem_grade',
#                       dev=lambda x:(int(x.split('/')[0])/60)*100, ),
#             Processor(name=['phy_grade', 'bio_grade'],
#                       dev=lambda x:int(x)),
#             Processor(name='age',
#                       dev=lambda x:int(x[:-1])/12 if 'm' in x else int(x)),
#             Processor(name='height',
#                       dev=lambda x:float(x[:-2])*2.54,
#                       prod= lambda x:float(x[:-2])),
#             Processor(name='grade',
#                       dev=lambda x:int(x[:-2]),
#                       prod=[grade_prod_mapper, lambda x:int(x[:-2])], suffix='_new')
#            ]


# # we have 3 kinds of Processors
# 1 - ColProcessor:
#     ColProcessor(name=['grade', 'age'],
#                       dev=lambda x:int(x[:-2]),
#                       prod=[grade_prod_mapper, lambda x:int(x[:-2])], suffix='_new')


# 2 - MultiColProcessor:
#     # doesn't take the name argument. it takes list of functions
#     def extract_features3and4(df):
#         df['feature3'] = df.feature1 + df.feature2
#         df['feature4'] = df.feature3 ** 2
#         return df

#     MultiColProcessor(funcs=[extract_features3and4])

# 2 - Transformers
#     # takes transformers with fit transform methodes
#     from feature_engine.selection import DropFeatures
#     feature_engine.selection import DropDuplicateFeatures

#     Trasformers([DropFeatures, DropDuplicateFeatures], )
