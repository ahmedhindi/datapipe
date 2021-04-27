import pandas as pd
from typing import List
import time


class Pipe:
    def __init__(
        self,
        data: pd.DataFrame,
        pipeline: List = [],
        mode: str = "dev",
        suffix: str = "",
        run_test_cases: bool = False
    ):
        """
        pipeline
        """
        self.pipeline = pipeline
        self.data = data
        self.mode = mode
        self._pipeline_funcs: List = []
        self.logs: str = ""
        self.run_test_cases = run_test_cases

    def run(self):
        new_data = self.data.copy()
        for proc in self.pipeline:
            # TODO: timing and logging
            if self.run_test_cases:
                proc.test(mode=self.mode)
            t0 = time.time()
            proc.run(data=new_data, mode=self.mode)
            time_to_finish = round((time.time()-t0), 3)
            # print(
            #     f"running {proc.name} ... finished in {round((time.time()-t0), 3)} sec"
            # )
            self._pipeline_funcs.append(f"""
            Columns: {proc.name}
            Time to finish: {time_to_finish}
            """)
        return new_data

    def __repr__(self):
        return f"""
        Mode: {self.mode} 
        input data shape: {self.data.shape} 
        {"".join(self._pipeline_funcs)}
        """
