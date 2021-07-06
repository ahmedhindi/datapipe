# dukto

`dukto means pipeline in`[esperanto](https://en.wikipedia.org/wiki/Esperanto)

`duckto` is a simple package that aims to create a single pipeline to handle data `cleaning`, `extraction` and `transformation` and tracks and logs sensible stats about all steps in the pipeline.

### Installation

### `pip install duckto`

### Let's go though an example of a data cleaning task using [UFC](https://en.wikipedia.org/wiki/Ultimate_Fighting_Championship) data.


```python
import pandas as pd
import numpy as np

from dukto.pipe import Pipe
from dukto.processor import ColProcessor, MultiColProcessor, Transformer

from feature_engine.encoding import CountFrequencyEncoder
from feature_engine.imputation import MeanMedianImputer, CategoricalImputer
```


```python
data  = pd.read_csv('data/ufc.csv', index_col=0)
```

### a sample of the data


```python
data.shape
```




    (5923, 21)




```python
data.columns
```




    Index(['agg_dob_first', 'agg_dob_second', 'agg_height_first',
           'agg_height_second', 'agg_reach_first', 'agg_reach_second',
           'agg_stand_first', 'agg_stand_second', 'agg_str_acc_first',
           'agg_str_acc_second', 'agg_weight_first', 'date_card',
           'first_fighter_res', 'first_sig_str_', 'first_sig_str_percentage',
           'first_total_str', 'method', 'second_sig_str_percentage',
           'second_total_str', 'time', 'type'],
          dtype='object')




```python
p = lambda x:print(x.to_markdown())
```


```python
p(data.iloc[:5, range(0, 13, 2)])
```

    |    | agg_dob_first   | agg_height_first   | agg_reach_first   | agg_stand_first   | agg_str_acc_first   | agg_weight_first   | first_fighter_res   |
    |---:|:----------------|:-------------------|:------------------|:------------------|:--------------------|:-------------------|:--------------------|
    |  0 | 19-Jul-87       | 6' 4"              | 84"               | Orthodox          | 57%                 | 205 lbs.           | W                   |
    |  1 | 7-Mar-88        | 5' 5"              | 66"               | Southpaw          | 51%                 | 125 lbs.           | W                   |
    |  2 | 16-Jan-92       | 6' 5"              | 80"               | Orthodox          | 55%                 | 265 lbs.           | L                   |
    |  3 | 16-Feb-91       | 5' 8"              | 70"               | Orthodox          | 41%                 | 145 lbs.           | L                   |
    |  4 | 7-Feb-85        | 6' 3"              | 79"               | Orthodox          | 50%                 | 260 lbs.           | W                   |
    



#### In dukto we have 3 main types of Processors `ColProcessor`, `MultiColProcessor`, and `Transformer`
#### To run these we need a `Pipe`

# `ColProcessor`

### applies function/s to a column/s
#### usage:
##### In some cases the computation is going to be applied on one column without the need of accessing other columns or rows. 
##### Examples: changing the type, extracting digits from strings, multiplying by a scalar .. 

# some arguments
- `funcs` (callable or list): in function or function you'll apply to the columns 
- `name`  (str or list): the name or names of the columns you'll be applying the functions on
- `new_name` (dict): if you want to rename the new column you can use a dict to map the old names to the new ones,
- `drop` (bool): if true it'll drop the old columns,
- `funcs_test` (dict): test cases for the output of that processor given and input example {'1h:30min', 1.5} (if that's the expected output of your funcs)
- `suffix` (str): text added at the end of the column name example if suffix="_new"  col_name -> col_name_new


#### Some cleaning functions that we will use in our examples.


```python
def convert_foot_to_cm(r):
    if isinstance(r, str) and "'" in r:
        foot, inches = r.split("'")
        inches = int(foot)*12 + int(inches.replace('"', ''))
        return inches*2.54
    return np.nan

def convert_inch_to_cm(r):
    if isinstance(r,str) and '"' in r:
        return int(r.replace('"', '')) * 2.54
    return np.nan

def num_of_num_to_perc(r):
    if isinstance(r,str) and 'of' in r:
        thr, landed = map(int, r.split('of'))
        if landed > 0:
            return thr / landed 
    return np.nan

def pounds_to_kg(r):
    if isinstance(r, str) and 'lbs' in r:
        return int(r.split(' ')[0]) * 0.4535
    return r
```


```python
single_pipe = [
    ColProcessor(name=['agg_height_first','agg_height_second'], 
                 funcs=[convert_foot_to_cm], funcs_test={"6'2\"":187.96}, suffix='_new'),
    
    ColProcessor(name=['agg_reach_first','agg_reach_second'], 
                 funcs=[convert_inch_to_cm], funcs_test={'70"': 177.80}, suffix='_new'),
    
    ColProcessor(name=['second_total_str', 'first_total_str'], 
                 funcs=[num_of_num_to_perc], suffix='_%%_new', funcs_test={'50 of 100':0.5}),
    
    ColProcessor(name=['agg_dob_first', 'agg_dob_second', 'date_card'], 
                 funcs=[pd.to_datetime]),
    
    ColProcessor(name='agg_weight_first', new_name={"agg_weight_first":'weight_class'}, 
                 funcs=[pounds_to_kg], suffix='_new', drop=True)
]
```

## `MultiColProcessor`

### applies a function that takes and returns a pandas DataFrame
### this class is used to add columns based on other column/s

#### usage:
##### In some cases the computation is going to be applied on more than one column. 
##### Examples: adding column a and b to create c or dropping some columns if they contain the word java.

# some arguments
- `funcs`  (list): function or function you'll apply 
- `name`  (str) : in this case it's optional and only useful for logging purpose and easy debugging



#### Some cleaning functions that we will use in our examples.


```python
def add_ages(df):
    df['first_fighter_age_new'] = df['date_card'] - df['agg_dob_first']
    df['second_fighter_age_new'] = df['date_card'] - df['agg_dob_second']
    return df

def ages_in_years(df):
    df[['first_fighter_age_new', 'second_fighter_age_new']] = df[['first_fighter_age_new', 'second_fighter_age_new']].applymap(lambda x:x/np.timedelta64(1, 'Y'))
    return df
```


```python
multi_pipe = [
    MultiColProcessor(name=['first_fighter_age_new', 'second_fighter_age_new'], 
                      funcs=[add_ages, ages_in_years]),
             ]
```

## `Transformer`

### Applies a `feature_engine` and "`sklearn`" after using [SklearnTransformerWrapper](https://feature-engine.readthedocs.io/en/1.1.x/wrappers/Wrapper.html)  style transformers to a column/s 

#### usage:
##### Applying transformations on a column/s  
##### Examples: `Missing data imputation`, `Categorical variable encoding`, `Discretisation`, `Variable transformation`, `Outlier capping or removal`, `Variable combination`, `Variable selection`.

# some arguments
- `transformers` (list  or Callable): list of transformers.
- `name` (str) : in this case it's optional and only useful for logging purposes and easy debugging.


```python
### selecting columns numarical cols to use as an inpu to the transformers
new_cols_func = lambda x: [i for i in x if (('new' in i) and ('weight' not in i))]

trans_pipe  = [
    Transformer(name_from_func=new_cols_func, 
                transformers=[MeanMedianImputer], imputation_method='median'),    
    MultiColProcessor(funcs=[lambda x:x.assign(weight_class_new=x.weight_class_new.astype(str))]), # i needed to add this there becouse CategoricalImputer expects a strtype 
    Transformer(name=['weight_class_new'], 
                transformers=[CategoricalImputer,CountFrequencyEncoder]),
]
```

## Pipe

### Runs the pipeline sequentially


- `data`: pandas DataFrame,
- `pipeline` (list): list of all Processors(`ColProcessor`, `MultiColProcessor` and `Transformer`)
- `run_test_cases` (bool): if true all test cases will run,
- `mode` (str) : "fit_transform" can be fit_transform or transform in case you want to apply the pipe on [train vs test](https://stackoverflow.com/questions/23838056/what-is-the-difference-between-transform-and-fit-transform-in-sklearn) data separately.

## Running


```python
from copy import deepcopy as c
```


```python
pipeline = single_pipe+multi_pipe+trans_pipe
pipe = Pipe(data=data.copy(), pipeline=c(pipeline), run_test_cases=False, mode='fit_transform')
res = pipe.run()
```

    Runningconvert_foot_to_cm(agg_height_first)
    Runningconvert_foot_to_cm(agg_height_second)
    Runningconvert_inch_to_cm(agg_reach_first)
    Runningconvert_inch_to_cm(agg_reach_second)
    Runningnum_of_num_to_perc(second_total_str)
    Runningnum_of_num_to_perc(first_total_str)
    Runningto_datetime(agg_dob_first)
    Runningto_datetime(agg_dob_second)
    Runningto_datetime(date_card)
    Runningpounds_to_kg(agg_weight_first)
    added columns ['second_fighter_age_new', 'first_fighter_age_new']... deleted columns []
    [<class 'feature_engine.imputation.mean_median.MeanMedianImputer'>] <class 'type'>
    

## Running with `test`


```python
pipe = Pipe(data=data.copy(), pipeline=c(pipeline), run_test_cases=True, mode='fit_transform')
res = pipe.run()
```

    Runningconvert_foot_to_cm(agg_height_first)
    Runningconvert_foot_to_cm(agg_height_second)
    Runningconvert_foot_to_cm(in)
    ColProcessor (agg_height_first, agg_height_second) test cases PASSED! 😎
    Runningconvert_inch_to_cm(agg_reach_first)
    Runningconvert_inch_to_cm(agg_reach_second)
    Runningconvert_inch_to_cm(in)
    ColProcessor (agg_reach_first, agg_reach_second) test cases PASSED! 😎
    Runningnum_of_num_to_perc(second_total_str)
    Runningnum_of_num_to_perc(first_total_str)
    Runningnum_of_num_to_perc(in)
    ColProcessor (second_total_str, first_total_str) test cases PASSED! 😎
    Runningto_datetime(agg_dob_first)
    Runningto_datetime(agg_dob_second)
    Runningto_datetime(date_card)
    Runningto_datetime(in)
    ColProcessor (agg_dob_first, agg_dob_second, date_card) test cases NOT FOUND.
    Runningpounds_to_kg(agg_weight_first)
    Runningpounds_to_kg(in)
    ColProcessor (agg_weight_first)             test cases NOT FOUND.
    added columns ['second_fighter_age_new', 'first_fighter_age_new']... deleted columns []
    Multi test not implemented yet
    [<class 'feature_engine.imputation.mean_median.MeanMedianImputer'>] <class 'type'>
    transformer test not implemented yet
    

## Using Transform


```python
fitted_pipe = pipe.pipeline
```


```python
transform_pipe = Pipe(data=data.head(20), pipeline=fitted_pipe, run_test_cases=False, mode='transform')
```


```python
res2 = transform_pipe.run()
```

    Runningconvert_foot_to_cm(agg_height_first)
    Runningconvert_foot_to_cm(agg_height_second)
    Runningconvert_inch_to_cm(agg_reach_first)
    Runningconvert_inch_to_cm(agg_reach_second)
    Runningnum_of_num_to_perc(second_total_str)
    Runningnum_of_num_to_perc(first_total_str)
    Runningto_datetime(agg_dob_first)
    Runningto_datetime(agg_dob_second)
    Runningto_datetime(date_card)
    Runningpounds_to_kg(agg_weight_first)
    added columns ['second_fighter_age_new', 'first_fighter_age_new']... deleted columns []
    [MeanMedianImputer(variables=['agg_height_first_new', 'agg_height_second_new',
                                 'agg_reach_first_new', 'agg_reach_second_new',
                                 'second_total_str_%%_new',
                                 'first_total_str_%%_new', 'first_fighter_age_new',
                                 'second_fighter_age_new'])] <class 'feature_engine.imputation.mean_median.MeanMedianImputer'>
    

# after 


```python
p(res.head(5)[[i for i in res.columns if 'new' in i]])
```

    |    |   agg_height_first_new |   agg_height_second_new |   agg_reach_first_new |   agg_reach_second_new |   second_total_str_%%_new |   first_total_str_%%_new |   weight_class_new |   first_fighter_age_new |   second_fighter_age_new |
    |---:|-----------------------:|------------------------:|----------------------:|-----------------------:|--------------------------:|-------------------------:|-------------------:|------------------------:|-------------------------:|
    |  0 |                 193.04 |                  193.04 |                213.36 |                 195.58 |                  0.452471 |                 0.629412 |            92.9675 |                 32.5592 |                  30.1197 |
    |  1 |                 165.1  |                  175.26 |                167.64 |                 172.72 |                  0.397059 |                 0.695122 |            56.6875 |                 31.924  |                  31.1136 |
    |  2 |                 195.58 |                  182.88 |                203.2  |                 187.96 |                  0.666667 |                 0.636364 |           120.178  |                 28.0635 |                  26.1552 |
    |  3 |                 172.72 |                  170.18 |                177.8  |                 180.34 |                  0.547009 |                 0.391892 |            65.7575 |                 28.978  |                  28.5098 |
    |  4 |                 190.5  |                  177.8  |                200.66 |                 185.42 |                  0.805195 |                 0.465517 |           117.91   |                 35.0014 |                  36.5346 |
    

# After Transformed


```python
p(res2.head(5)[[i for i in res.columns if 'new' in i]])
```

    |    |   agg_height_first_new |   agg_height_second_new |   agg_reach_first_new |   agg_reach_second_new |   second_total_str_%%_new |   first_total_str_%%_new |   weight_class_new |   first_fighter_age_new |   second_fighter_age_new |
    |---:|-----------------------:|------------------------:|----------------------:|-----------------------:|--------------------------:|-------------------------:|-------------------:|------------------------:|-------------------------:|
    |  0 |                 193.04 |                  193.04 |                213.36 |                 195.58 |                  0.452471 |                 0.629412 |            92.9675 |                 32.5592 |                  30.1197 |
    |  1 |                 165.1  |                  175.26 |                167.64 |                 172.72 |                  0.397059 |                 0.695122 |            56.6875 |                 31.924  |                  31.1136 |
    |  2 |                 195.58 |                  182.88 |                203.2  |                 187.96 |                  0.666667 |                 0.636364 |           120.178  |                 28.0635 |                  26.1552 |
    |  3 |                 172.72 |                  170.18 |                177.8  |                 180.34 |                  0.547009 |                 0.391892 |            65.7575 |                 28.978  |                  28.5098 |
    |  4 |                 190.5  |                  177.8  |                200.66 |                 185.42 |                  0.805195 |                 0.465517 |           117.91   |                 35.0014 |                  36.5346 |
    

# Before


```python
p(data.head(5))
```

    |    | agg_dob_first   | agg_dob_second   | agg_height_first   | agg_height_second   | agg_reach_first   | agg_reach_second   | agg_stand_first   | agg_stand_second   | agg_str_acc_first   | agg_str_acc_second   | agg_weight_first   | date_card   | first_fighter_res   | first_sig_str_   | first_sig_str_percentage   | first_total_str   | method               | second_sig_str_percentage   | second_total_str   | time   | type   |
    |---:|:----------------|:-----------------|:-------------------|:--------------------|:------------------|:-------------------|:------------------|:-------------------|:--------------------|:---------------------|:-------------------|:------------|:--------------------|:-----------------|:---------------------------|:------------------|:---------------------|:----------------------------|:-------------------|:-------|:-------|
    |  0 | 19-Jul-87       | 26-Dec-89        | 6' 4"              | 6' 4"               | 84"               | 77"                | Orthodox          | Southpaw           | 57%                 | 50%                  | 205 lbs.           | 8-Feb-20    | W                   | 104 of 166       | 62%                        | 107 of 170        | Decision - Unanimous | 44%                         | 119 of 263         | 5:00   | belt   |
    |  1 | 7-Mar-88        | 28-Dec-88        | 5' 5"              | 5' 9"               | 66"               | 68"                | Southpaw          | Orthodox           | 51%                 | 35%                  | 125 lbs.           | 8-Feb-20    | W                   | 40 of 65         | 61%                        | 57 of 82          | KO/TKO               | 30%                         | 27 of 68           | 1:03   | belt   |
    |  2 | 16-Jan-92       | 13-Dec-93        | 6' 5"              | 6' 0"               | 80"               | 74"                | Orthodox          | Southpaw           | 55%                 | 55%                  | 265 lbs.           | 8-Feb-20    | L                   | 7 of 11          | 63%                        | 7 of 11           | KO/TKO               | 66%                         | 10 of 15           | 1:59   | nan    |
    |  3 | 16-Feb-91       | 6-Aug-91         | 5' 8"              | 5' 7"               | 70"               | 71"                | Orthodox          | Orthodox           | 41%                 | 46%                  | 145 lbs.           | 8-Feb-20    | L                   | 17 of 60         | 28%                        | 29 of 74          | Decision - Split     | 48%                         | 64 of 117          | 5:00   | nan    |
    |  4 | 7-Feb-85        | 28-Jul-83        | 6' 3"              | 5' 10"              | 79"               | 73"                | Orthodox          | Orthodox           | 50%                 | 39%                  | 260 lbs.           | 8-Feb-20    | W                   | 20 of 50         | 40%                        | 27 of 58          | Decision - Unanimous | 41%                         | 62 of 77           | 5:00   | nan    |
    


```python

```
