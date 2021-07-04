import time
from typing import List, TypeVar, Union

import pandas as pd
from pydantic import validate_arguments

from dukto.processor import ColProcessor, MultiColProcessor, Transformer

# import pandas

piplinetype = Union[ColProcessor, MultiColProcessor, Transformer]
# pandas.core.frame.pd.DataFrame = TypeVar("pandas.core.frame.pd.DataFrame")
# Dataframe = pd.pd.DataFrame


class Pipe:
    # @validate_arguments
    def __init__(
        self,
        data: pd.DataFrame,
        pipeline: List[piplinetype] = [],
        pipe_suffix: str = "",
        run_test_cases: bool = False,
        mode: str = "fit_transform",
    ):
        """
        pipeline
        """
        self.pipeline = pipeline
        self.data = data
        self._pipeline_funcs: List = []
        self.logs: str = ""
        self.run_test_cases = run_test_cases
        # TODO: add a suffix to the pipeline () if the suffix for the processor is _avg and the suffix for the pipeline is _num the result should be name_avg_num
        self.pipe_suffix = pipe_suffix
        self.mode = mode

    def run(self):
        new_data = self.data.copy()
        for proc in self.pipeline:
            # TODO: timing and logging
            # TODO:refactor this disgusting function
            new_data = proc.run(data=new_data, mode=self.mode)
            if self.run_test_cases:
                proc.test()
            # self._pipeline_funcs.append(
            #     f"""
            # Columns: {proc.name}
            # Time to finish: {time_to_finish}
            # """
            # )
        return new_data

    def __repr__(self):
        return f"""
        input data shape: {self.data.shape} 
        {"".join(self._pipeline_funcs)}
        """
