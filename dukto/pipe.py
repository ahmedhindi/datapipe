import pandas as pd
from typing import List, Union
import time
from dukto.processor import ColProcessor, MultiColProcessor, Transformer


piplinetype = Union[ColProcessor, MultiColProcessor, Transformer]


class Pipe:
    # TODO Validate the args using pydantic
    def __init__(
        self,
        data: pd.DataFrame,
        pipeline: List[piplinetype] = [],
        pipe_suffix: str = "",
        run_test_cases: bool = False,
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

    def run(self):
        new_data = self.data.copy()
        for proc in self.pipeline:
            # TODO: timing and logging
            # TODO:refactor this disgusting function
            if self.run_test_cases:
                proc.test()
            t0 = time.time()
            proc.run(data=new_data)
            time_to_finish = round((time.time() - t0), 3)
            # print(
            #     f"running {proc.name} ... finished in {round((time.time()-t0), 3)} sec"
            # )
            self._pipeline_funcs.append(
                f"""
            Columns: {proc.name}
            Time to finish: {time_to_finish}
            """
            )
        return new_data

    def __repr__(self):
        return f"""
        input data shape: {self.data.shape} 
        {"".join(self._pipeline_funcs)}
        """
