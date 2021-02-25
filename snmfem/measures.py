import numpy as np
from snmfem.conf import log_shift

def spectral_angle(v1, v2):
    """
    Calculates the angle between two spectra. They have to have the same dimension.
    :v1: first spectrum (np.array 1D)
    :v2: second spectrum (np.array 1D)
    """

    if len(v1.shape)==1:
        if v1.shape != v2.shape:
            raise ValueError("v1 and v2 should have the same shape.")
        v1_u = v1 / np.linalg.norm(v1)
        v2_u = v2 / np.linalg.norm(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)) * 180 / np.pi
    else:
        if v1.shape[1] != v2.shape[1]:
            raise ValueError("The second dimensions of v1 and v2 should be the same.")
        v1_u = v1 / np.sqrt(np.sum((v1**2), axis=1, keepdims=True))
        v2_u = v2 / np.sqrt(np.sum((v2**2), axis=1, keepdims=True))
        return np.arccos(np.clip(v1_u @ v2_u.T, -1.0, 1.0)) * 180 / np.pi


def mse(map1, map2):
    """Mean square error.

    Calculates the mean squared error between two 2D arrays. They have to have the same dimension.
    :map1: (np.array 2D) first array
    :map2: (np.array 2D) second array
    """
    summed_vec1 = map1@np.ones((map1.shape[1],))
    summed_vec2 = map2@np.ones((map2.shape[1],))
    diff_matr = (summed_vec1[:,np.newaxis] - summed_vec2[np.newaxis,:])**2
    return diff_matr


# This function will find the best matching endmember for each true spectrum.
# This is useful since the A and P matrice are initialized at random.
# This function works but can probably greatly improved
def find_min_angle(true_vectors, algo_vectors):
    # This function calculates all the possible angles between endmembers and true spectra
    # For each true spectrum a best matching endmember is found
    # The function returns the angles of the corresponding pairs
    angle_matr = spectral_angle(true_vectors,algo_vectors)
    ordered_angles = unique_min(angle_matr,[])
    #unique minimum angles are ordered
    return ordered_angles
    
def unique_min (matr,angles) : 
    # Recursive way to find the minimum values in a matrice, line by line.
    # For each line, the column of the min is removed at every iteration. This ensures that a min is found for each column once.
    # the input matrix should be n_comps*n_comps
    if matr.size==0 :
        return angles
    else :
        ind_min = np.argmin(matr[0,:])
        angles.append(np.min(matr[0,:]))
        reduced1 = np.delete(matr,ind_min,axis = 1)
        reduced2 = np.delete(reduced1,0,axis = 0)
        return unique_min(reduced2,angles)


# This function works but can probably greatly improved
def find_min_MSE(true_maps, algo_maps):
    # This function calculates all the possible MSE between abundances and true maps
    # For each true map a best matching abundance is found
    # The function returns the MSE of the corresponding pairs
    mse_matr = mse(true_maps,algo_maps)
    ordered_maps = unique_min(mse_matr,[])
    return ordered_maps


# This function gives the residuals between the model determined by snmf and the data that were fitted
def residuals(data, model):
    X_sum = data.sum(axis=0).sum(axis=0)
    model_sum = (
        model.get_phase_map(0).sum() * model.get_phase_spectrum(0)
        + model.get_phase_map(1).sum() * model.get_phase_spectrum(1)
        + model.get_phase_map(2).sum() * model.get_phase_spectrum(2)
    )
    return X_sum - model_sum


def KLdiv(X, D, A, eps=log_shift, safe=True):
    """
    Compute the generalized KL divergence.

    \sum_{ji} X_{ij} \log (X / D A)_{ij} + (D A - X)_{ij}
    """
    if safe:
        # Allow for very small negative values!
        assert(np.sum(A<-log_shift/2)==0)
        assert(np.sum(D<-log_shift/2)==0)
    
    DA = D @ A
    x_lin = np.sum(DA) - np.sum(X)
    x_log = np.sum(X*np.log((X+ eps) / (DA + eps)))
    return x_lin + x_log

def KLdiv_loss(X, D, A, eps=log_shift, safe=True):
    """
    Compute the loss based on the generalized KL divergence.

    \sum_{ji} X_{ij} \log (D A)_{ij} + (D A)_{ij}

    This does not contains all the term of the KL divergence, only the ones
    depending on D and A.
    """
    if safe:
        # Allow for very small negative values!
        assert(np.sum(A<-log_shift/2)==0)
        assert(np.sum(D<-log_shift/2)==0)
    
    DA = D @ A
    x_lin = np.sum(DA)
    x_log = np.sum(X*np.log(DA + eps))
    return x_lin - x_log

def log_reg(A, mu, epsilon):
    """
    Compute the regularization loss: \sum_ij mu_i \log(A_{ij})
    """
    if not(np.isscalar(mu)):
        mu = np.expand_dims(mu, axis=1)
    return np.sum(mu* np.log(A+epsilon))


