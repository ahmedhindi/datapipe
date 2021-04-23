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
            print(
                f"running {proc.name} ... finished in {round((time.time()-t0), 3)} sec"
            )
        return new_data
