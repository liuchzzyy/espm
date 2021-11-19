from pathlib import Path
import hyperspy.misc.eds.ffast_mac as macs
import numpy as np

# Path of the base
BASE_PATH = Path(__file__).parent

# Path of the db
DB_PATH = BASE_PATH / Path("Data/")

NUMBER_PERIODIC_TABLE = DB_PATH / Path("periodic_table_number.json")

SYMBOLS_PERIODIC_TABLE = DB_PATH / Path("periodic_table_symbols.json")

DEFAULT_SDD_EFF = "SDD_efficiency.txt"

# Path of the generated datasets
DATASETS_PATH = BASE_PATH.parent / Path("generated_datasets")
# Ensure that the folder DATASETS_PATH exists
DATASETS_PATH.mkdir(exist_ok=True, parents=True)

RESULTS_PATH = BASE_PATH.parent / Path("results")
# Ensure that the folder DATASETS_PATH exists
RESULTS_PATH.mkdir(exist_ok=True, parents=True)

SCRIPT_CONFIG_PATH = BASE_PATH.parent / Path("scripts/config/")

HSPY_MAC = macs.ffast_mac

DEFAULT_EDXS_PARAMS = {
    "Det" : DEFAULT_SDD_EFF,
    "Abs" : {
            "thickness" : 100.0e-7,
            "toa" : 22,
            "density" : None,
            "atomic_fraction" : False
    }
}

DEFAULT_PHASE_PARAMS = [{"b0" : 1e-9 , "b1" : 1e-7, "elements_dict" :  {"14": 1.0},"scale" : 1.0},{"b0" : 7e-8 , "b1" : 3e-8, "elements_dict" :  {"79": 1.0},"scale" : 0.5}]

DEFAULT_SYNTHETIC_DATA_DICT = {
    "data_folder" : "default_synth_data",
    "model_parameters" : {
    "e_offset" : 0.200,
    "e_size" : 1980,
    "e_scale" : 0.01,
    "width_slope" : 0.01,
    "width_intercept" : 0.065,
    "db_name" : "default_xrays.json",
    "E0" : 200,
    "params_dict" : {
        "Abs" : {
            "thickness" : 100.0e-7,
            "toa" : 22,
            "density" : None,
            "atomic_fraction" : False
            },
    "Det" : DEFAULT_SDD_EFF,
        }
    },
    "phases_parameters" : DEFAULT_PHASE_PARAMS,
    "shape_2d" : (80,80),
    "weight_type" : "sphere",
    "weights_params" : {},
    "N" : 100,
    "densities" : [2.33,19.3],
    "model" : "EDXS"
}

log_shift = 1e-14
dicotomy_tol = 1e-10
seed_max = 4294967295

POS_ARGS = {
    "input_file" : ["input_file",{"help" : "str : Name of the file containing the data."}],
    "method" : ["method",{"choices":  ["NMF","SmoothNMF","SKNMF","MCRLLM"], "help" : "str : Name of the estimator for the decomposition"}],
    "g_type" : ["g_type", {"choices" : ["bremsstrahlung","no_brstlg", "identity"], "default" : "bremsstrahlung", "help" : "str : method to generate the G matrix from the metadata"}],
    "k" : ["k",{"type" : int,"help" : "int : expected number of phases"}]
}

EVAL_ARGS = {
    "output_file" : ["-of","--output_file",{"default" : "dump.npz", "help" : "str : Name of the npz file where the data are stored"}],
    "simulated" : ["-sim", "--simulated", {"action" : "store_true", "help" : "None : Activate to use the ground truth stored in the spim object. It will produce errors if no ground truth is available."}],
    "fixed_P_json" : ["-fpjs","--fixed_P_json",{"default" : "None", "help" : "str : Name of the json file containing the dictionnary to build fixed_P"}]
}

ESTIMATOR_ARGS = {
    # Common parameters
    "max_iter" : ["-mi","--max_iter",{"type" : int, "default" : 10000, "help" : "int : Max number of iterations for the algorithm"},None],
    "verbose" : ["-v","--verbose",{"action" : "store_false", "help" : "None : Activate to prevent display details about the algorithm"},None],
    "init" : ["-i","--init",{"choices" : ["random","nndsvd","nndsvda","nndsvdar","custom"],"default" : "nndsvdar", "help" : "str : Initialisation method"}, None],
    "random_state" : ["-rs","--random_state",{"type" : int,"default" : 42, "help" : "int : seed for the random initialisations"}, None],
    "tol" : ["-t", "--tol", {"type" : float, "default" : 1e-6, "help" : "float : Stopping criterion"}, None],
    "normalize" : ["-n", "--normalize", {"action" : "store_true", "help" : "None : Activate the normalization of the data, it is mostly useful for having stable values of lambda_L among datasets."}, None],

    # SNMFEM parameters
    "mu" : ["-mu","--mu",{"type" : float,"default" : 0.0, "help" : "float : strenght of the log regularization"},["NMF","SmoothNMF"]],
    "force_simplex" : ["-fs","--force_simplex",{"action" : "store_false", "help" : "None : Activate simplex constraint"},["NMF","SmoothNMF"]],
    "lambda_L" : ["-l","--lambda_L",{"type" : float, "default" : 0.0,"help":"float : strengh of the Laplacian reg"},["SmoothNMF"]],
    "l2" : ["-l2","--l2",{"action" : "store_true","help" : "None : Sets the loss function to frobenius when activated"}, ["NMF","SmoothNMF"]],
    "accelerate" : ["-acc","--accelerate",{"action" : "store_true","help" : "None : Sets the algorithm type to the accelerated one"}, ["SmoothNMF"]],
    "linesearch" : ["-ls","--linesearch",{"action" : "store_true","help" : "None : activates the linesearch for the accelerated algorithm"}, ["SmoothNMF"]],

    # Scikit parameters
    # "beta_loss" : ["-bl","--beta_loss",{"choices" : ["frobenius","kullback-leibler"], "default" : "frobenius", "help" : "str : Type of loss to be optimized"},["SKNMF"]],
    # "solver" : ["-s", "--solver", {"choices" : ["mu", "cd"], "default" : "mu", "help" : "str : Type of updates for the optimization"},["SKNMF"]],
    # "alpha" : ["-a", "--alpha",{"type" : float, "default" : 0.0, "help" : "float : strength of the regularization L1, L2 or both depending on the value of l1_ratio"}, ["SKNMF"]],
    # "l1_ratio" : ["-l1","--l1_ratio",{"type" : float, "default" : 1.0, "help" : "float : ratio between L1 and L2 regularization, 1.0 is full L1 regularization"},["SKNMF"]],
    # "regularization" : ["-r","--regularization",{"choices" : ["both","components","transformation"], "default" : "components", "help" : "str : determines on what the regularization is applied, W, H or both"},["SKNMF"]],

    # # MCR
    # "mcr_method" : ["-mm","--mcr_method",{"action" : "store_false","help" : "None : to be written"},["MCRLLM"]]
}
