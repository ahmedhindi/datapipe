# Dukto
data pre-processing pipeline library.


### usecase
```python
from dukto import Pipe, Processor
hight = processor(name='hight', dev=lambda x*2, prod=lambda x:x*3)
weight = processor(name='weight, ev=lambda x*2, prod=lambda x:x*8)

pipeline  = Pipe(data=df, pipeline=[hight, weight])

pipeline.run()
```
