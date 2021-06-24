import pandas as pd
import numpy as np


def convert_foot_to_cm(r):
    if isinstance(r, str) and "'" in r:
        foot, inches = r.split("'")
        inches = int(foot) * 12 + int(inches.replace('"', ""))
        return inches * 2.54
    return np.nan


def convert_inch_to_cm(r):
    if isinstance(r, str) and '"' in r:
        return int(r.replace('"', "")) * 2.54
    return np.nan


def num_of_num_to_perc(r):
    if isinstance(r, str) and "of" in r:
        thr, landed = map(int, r.split("of"))
        if landed > 0:
            return thr / landed
    return np.nan


def pounds_to_kg(r):
    if isinstance(r, str) and "lbs" in r:
        return int(r.split(" ")[0]) * 0.4535
    return r
