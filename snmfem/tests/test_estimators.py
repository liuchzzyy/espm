from sklearn.utils.estimator_checks import check_estimator
from snmfem.estimators import NMF
import numpy as np

def test_NMF () : 
    estimator = NMF(n_components= 5,max_iter=200,force_simplex = True,mu = 1.0, epsilon_reg = 1.0)
    check_estimator(estimator)