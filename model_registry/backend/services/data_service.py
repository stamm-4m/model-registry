import pandas as pd


def load_sample(path=None):
    if path:
        return pd.read_csv(path)
    return pd.DataFrame({'x':[1,2,3],'y':[3,1,2]})
