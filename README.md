```python
%load_ext autoreload
%autoreload 2
```

    The autoreload extension is already loaded. To reload it, use:
      %reload_ext autoreload
    


```python
from dukto.pipe import Pipe
from dukto.processor import ColProcessor, MultiColProcessor, Transformer
import pandas as pd
import numpy as np
from feature_engine.encoding import CountFrequencyEncoder
from feature_engine.imputation import MeanMedianImputer, CategoricalImputer
```


```python
data  = pd.read_csv('data/ufc.csv', index_col=0)
```

# ColProcessor
### applies function/s to a column/s  


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

## MultiColProcessor

## applies a function that takes and returns a pandas DataFrame
## this class is used to add columns based on other column/s


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

## Transformer

### applies a feature_engine style transformer to a column/s


```python

new_cols_func = lambda x: [i for i in x if (('new' in i) and ('weight' not in i))]

trans_pipe  = [
    Transformer(name_from_func=new_cols_func, 
                transformers=[MeanMedianImputer]),
    
    MultiColProcessor(funcs=[lambda x:x.assign(weight_class_new=x.weight_class_new.astype(str))]),
    
    Transformer(name=['weight_class_new'], 
                transformers=[CategoricalImputer,CountFrequencyEncoder]),
]
```


```python
pipeline = single_pipe+multi_pipe+trans_pipe
```


```python
pipeline
```




    [ColProcessor(agg_height_first, agg_height_second),
     ColProcessor(agg_reach_first, agg_reach_second),
     ColProcessor(second_total_str, first_total_str),
     ColProcessor(agg_dob_first, agg_dob_second, date_card),
     ColProcessor(agg_weight_first),
     MultiColProcessor(first_fighter_age_new, second_fighter_age_new),
     Transformer(),
     MultiColProcessor(),
     Transformer()]




```python
pipe = Pipe(data=data, pipeline=pipeline, run_test_cases=True)
```


```python
res = pipe.run()
```

    ColProcessor (agg_height_first, agg_height_second) test cases PASSED! 😎
    ColProcessor (agg_reach_first, agg_reach_second) test cases PASSED! 😎
    ColProcessor (second_total_str, first_total_str) test cases PASSED! 😎
    ColProcessor (agg_dob_first, agg_dob_second, date_card) test cases NOT FOUND.
    ColProcessor (agg_weight_first)             test cases NOT FOUND.
    Multi test not implemented yet
    transformer test not implemented yet
    Multi test not implemented yet
    transformer test not implemented yet
    

# after 


```python
res[[i for i in res.columns if 'new' in i]].head(3)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>agg_height_first_new</th>
      <th>agg_height_second_new</th>
      <th>agg_reach_first_new</th>
      <th>agg_reach_second_new</th>
      <th>second_total_str_%%_new</th>
      <th>first_total_str_%%_new</th>
      <th>weight_class_new</th>
      <th>first_fighter_age_new</th>
      <th>second_fighter_age_new</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>193.04</td>
      <td>193.04</td>
      <td>213.36</td>
      <td>195.58</td>
      <td>0.452471</td>
      <td>0.629412</td>
      <td>454</td>
      <td>32.559190</td>
      <td>30.119715</td>
    </tr>
    <tr>
      <th>1</th>
      <td>165.10</td>
      <td>175.26</td>
      <td>167.64</td>
      <td>172.72</td>
      <td>0.397059</td>
      <td>0.695122</td>
      <td>382</td>
      <td>31.923996</td>
      <td>31.113575</td>
    </tr>
    <tr>
      <th>2</th>
      <td>195.58</td>
      <td>182.88</td>
      <td>203.20</td>
      <td>187.96</td>
      <td>0.666667</td>
      <td>0.636364</td>
      <td>96</td>
      <td>28.063547</td>
      <td>26.155226</td>
    </tr>
  </tbody>
</table>
</div>



# Before


```python
data.head(3)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>agg_dob_first</th>
      <th>agg_dob_second</th>
      <th>agg_height_first</th>
      <th>agg_height_second</th>
      <th>agg_reach_first</th>
      <th>agg_reach_second</th>
      <th>agg_stand_first</th>
      <th>agg_stand_second</th>
      <th>agg_str_acc_first</th>
      <th>agg_str_acc_second</th>
      <th>...</th>
      <th>date_card</th>
      <th>first_fighter_res</th>
      <th>first_sig_str_</th>
      <th>first_sig_str_percentage</th>
      <th>first_total_str</th>
      <th>method</th>
      <th>second_sig_str_percentage</th>
      <th>second_total_str</th>
      <th>time</th>
      <th>type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>19-Jul-87</td>
      <td>26-Dec-89</td>
      <td>6' 4"</td>
      <td>6' 4"</td>
      <td>84"</td>
      <td>77"</td>
      <td>Orthodox</td>
      <td>Southpaw</td>
      <td>57%</td>
      <td>50%</td>
      <td>...</td>
      <td>8-Feb-20</td>
      <td>W</td>
      <td>104 of 166</td>
      <td>62%</td>
      <td>107 of 170</td>
      <td>Decision - Unanimous</td>
      <td>44%</td>
      <td>119 of 263</td>
      <td>5:00</td>
      <td>belt</td>
    </tr>
    <tr>
      <th>1</th>
      <td>7-Mar-88</td>
      <td>28-Dec-88</td>
      <td>5' 5"</td>
      <td>5' 9"</td>
      <td>66"</td>
      <td>68"</td>
      <td>Southpaw</td>
      <td>Orthodox</td>
      <td>51%</td>
      <td>35%</td>
      <td>...</td>
      <td>8-Feb-20</td>
      <td>W</td>
      <td>40 of 65</td>
      <td>61%</td>
      <td>57 of 82</td>
      <td>KO/TKO</td>
      <td>30%</td>
      <td>27 of 68</td>
      <td>1:03</td>
      <td>belt</td>
    </tr>
    <tr>
      <th>2</th>
      <td>16-Jan-92</td>
      <td>13-Dec-93</td>
      <td>6' 5"</td>
      <td>6' 0"</td>
      <td>80"</td>
      <td>74"</td>
      <td>Orthodox</td>
      <td>Southpaw</td>
      <td>55%</td>
      <td>55%</td>
      <td>...</td>
      <td>8-Feb-20</td>
      <td>L</td>
      <td>7 of 11</td>
      <td>63%</td>
      <td>7 of 11</td>
      <td>KO/TKO</td>
      <td>66%</td>
      <td>10 of 15</td>
      <td>1:59</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>3 rows × 21 columns</p>
</div>




```python

```
