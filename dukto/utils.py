from sklearn.base import BaseEstimator, TransformerMixin

# from dukto.pipe import Pipe


get_class_name = lambda c: str(c.__class__).split(".")[-1][:-2]


# def SkTransformer(BaseEstimator, TransformerMixin):
#     def __init__(self, pipe: Pipe):
#         self.pipe = pipe

#     def fit(self):
#         return self

#     def transform(self):
#         return self.pipe.run()
