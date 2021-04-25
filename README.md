# Dukto
data pre-processing pipeline library.


### use cases 
* Creating simple data pipelines using an intuitive interface.
* Handling the differences  between development data and the data available in production.  


### example
- development data `dev`. 
- production data `prod`. 

```python
>>> dev.head(3)
```

|    | name                 | chem_grade   |   phy_grade |   bio_grade |   age | height   | grade   |
|---:|:---------------------|:-------------|------------:|------------:|------:|:---------|:--------|
|  0 | Anjelica Mccrossen   | 40/60        |          50 |          52 |    17 | 55in     | 9th     |
|  1 | Billie-Rose Garofolo | 8/60         |          98 |          66 |    15 | 57in     | 9th     |
|  2 | Cyrita Reesor        | 47/60        |          46 |          35 |    18 | 56in     | 9th     |

----
```python
>>> prod.head(3)
```

|    | name            | chem_grade   |   phy_grade |   bio_grade | age   | height   | grade    |
|---:|:----------------|:-------------|------------:|------------:|:------|:---------|:---------|
|  0 | Jalyiah Darcey  | 26/60        |          77 |          17 | 17    | 156cm    | Freshman |
|  1 | Eunita Beahm    | 11/60        |          56 |          67 | 184m  | 164cm    | Freshman |
|  2 | Guluzar Bernand | 42/60        |          97 |          65 | 18    | 157cm    | Freshman |

---

notes about the data
- age: in some cases is in months and it ends with `m` in these cases otherwise it's in years.(the goal is to be all in years and as a numeric type)
- chem_grades: a string object 'grade/total grade'. (The goal is to be a numeric grade out of 100 like `phy_grade`, `phy_grade`) 
- phy_grade, bio_grade: (The goal is to convert from str to int) 
- height: in the `dev` DataFrame the height is `inches` and in the `prod` it's in cm (the goal is to normalize that and make it all in `cm`)

---

We start by importing the `processor` and the 'Pipe' class.
and then creating a list of all out Processors.
parameters for `Processor`:
	
- name: (str or List) contains the name of the column you're trying to modify or work on or a list of them.
- dev: a function or a list of functions you'll run for this column/columns.
- prod: a function or a list of functions you'll run for this column/columns. if not provided `dev` will be used.
- new_name: create a new column with `new_name` (if the parameter `name` is a List new_name should be a dict mapping original names to the new_names {'old_name': 'new_name'}) 
- suffix: suffix for the name or the new_name if provided
	
	

 
```python
from dukto import Processor, Pipe
# helper function for the grade processor
def grade_prod_mapper(g):
    return {'Freshman':"9th",'Sophomore':"10th",'Junior':'11th','Senior':"12th"}[g]

pipeline = [Processor(name='chem_grade', 
                      dev=lambda x:(int(x.split('/')[0])/60)*100, ),
            Processor(name=['phy_grade', 'bio_grade'], 
                      dev=lambda x:int(x)),
            Processor(name='age', 
                      dev=lambda x:int(x[:-1])/12 if 'm' in x else int(x)),
            Processor(name='height', 
                      dev=lambda x:float(x[:-2])*2.54, 
                      prod= lambda x:float(x[:-2])),
            Processor(name='grade', 
                      dev=lambda x:int(x[:-2]),
                      prod=[grade_prod_mapper, lambda x:int(x[:-2])], suffix='_new')
           ]
```

### Creating running the pipeline for `dev`.


##### Parameters for `Pipe()`
- data: pandas DataDrame
- pipeline: List of `Processor`s
- mode: `dev` if you want to run the `dev` function else `prod`
```python
dev_pipe = Pipe(data=dev, pipeline=pipeline,mode='dev')
clean_dev = dev_pipe.run()
clean_dev.head(3)
```
|    | name                 |   chem_grade |   phy_grade |   bio_grade |   age |   height | grade   |   grade_new |
|---:|:---------------------|-------------:|------------:|------------:|------:|---------:|:--------|------------:|
|  0 | Anjelica Mccrossen   |      66.6667 |          50 |          52 |    17 |   139.7  | 9th     |           9 |
|  1 | Billie-Rose Garofolo |      13.3333 |          98 |          66 |    15 |   144.78 | 9th     |           9 |
|  2 | Cyrita Reesor        |      78.3333 |          46 |          35 |    18 |   142.24 | 9th     |           9 |

### Running it for the `prod` data.

```python
prod_pipe = Pipe(data=prod, pipeline=pipeline,mode='prod')
clean_prod = prod_pipe.run()
clean_prod.head(3)
```


|    | name            |   chem_grade |   phy_grade |   bio_grade |     age |   height | grade    |   grade_new |
|---:|:----------------|-------------:|------------:|------------:|--------:|---------:|:---------|------------:|
|  0 | Jalyiah Darcey  |      43.3333 |          77 |          17 | 17      |      156 | Freshman |           9 |
|  1 | Eunita Beahm    |      18.3333 |          56 |          67 | 15.3333 |      164 | Freshman |           9 |
|  2 | Guluzar Bernand |      70      |          97 |          65 | 18      |      157 | Freshman |           9 |



