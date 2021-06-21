from sklearn.base import BaseEstimator, TransformerMixin
from dukto.pipe import Pipe


def SkTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, pipe: Pipe):
        self.pipe = pipe

    def fit(self):
        return self

    def transform(self):
        return self.pipe.run()
