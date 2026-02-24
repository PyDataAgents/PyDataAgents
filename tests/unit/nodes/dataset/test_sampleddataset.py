import numpy as np
from sktime.datasets import load_UCR_UEA_dataset

def test_000():
    
    X, y = load_UCR_UEA_dataset(name="Wine")
    
    d = X.to_dict(orient="list")
    
    li = np.array(list(d.values())).reshape(-1).tolist()
    print(li)    