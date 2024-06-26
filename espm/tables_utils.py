r""" The :mod:`espm.table_utils` module implements some methods to manipulate the tables produces by the emtables package.

Using this module it is possible to load the tables and to import custom k-factors into the tables.

.. note::

    The emtables package can be found here: https://github.com/adriente/emtables

"""

import json
from pathlib import Path
from espm.conf import DB_PATH, SYMBOLS_PERIODIC_TABLE, SIEGBAHN_TO_IUPAC
import re
import numpy as np
import espm.utils as u

def load_table (db_name) :
    r"""
    Load the table and metadata of a json table generated by emtables.

    Parameters
    ----------
    db_name : str
        The file name of the table to load.
    
    Returns
    -------
    table : dict
        The table of the cross sections.
    metadata : dict
        The metadata of the table.

    Notes
    -----
    Call espm.conf.DB_PATH to get the folder of the tables.
    """
    db_path = DB_PATH / Path(db_name)
    with open(db_path,"r") as f :
        json_dict = json.load(f)
    return json_dict["table"], json_dict["metadata"]

def import_k_factors(table,mdata,k_factors_names,k_factors_values,ref_name) : 
    r"""
    Modify the X-ray emission cross-sections of the input table using the k-factors input, i.e. imposing cross-sections ratios to correspond to the k-factors.
    The metadata are modified too to keep track of the modifications.

    Parameters
    ----------
    table : dict
        The table of the X-ray emission cross sections.
    mdata : dict
        The metadata of the table.
    k_factors_names : list
        The list of the names of the k-factors to import. It has to correspond to the nomenclature of the hyperspy X-ray lines.
    k_factors_values : list
        The list of the values of the k-factors to import. It has to have the same length and ordering as k_factors_names.
    ref_name : str
        The name of the X-ray line to use as a reference for the k-factors. It has to correspond to the nomenclature of the hyperspy X-ray lines.
    
    Returns
    -------
    new_table : dict
        The modified table of the X-ray emission cross sections.
    new_mdata : dict
        The modified metadata of the table.
    """

    with open(SYMBOLS_PERIODIC_TABLE,"r") as f : 
        SPT = json.load(f)["table"]

    with open(SIEGBAHN_TO_IUPAC,"r") as f : 
        STI = json.load(f)

    for i,name in enumerate(k_factors_names) : 
        if name == ref_name : 
            mr = re.match(r"([A-Z][a-z]?)_(.*)",name)
            ref_at_num = SPT[mr.group(1)]["number"]
            ref_lines =  STI[mr.group(2)]
            ref_sig_vals = []
            for l in ref_lines :
                if l in table[str(ref_at_num)] : 
                    ref_sig_vals.append(table[str(ref_at_num)][l]["cs"])
            ref_sig_val = np.mean(ref_sig_vals)
            ref_k_val = k_factors_values[i]

    for i,name in enumerate(k_factors_names) : 
        m0 = re.match(r"([A-Z][a-z]?)_(.*)",name)
        if m0 : 
            at_num = SPT[m0.group(1)]["number"]
            lines =  STI[m0.group(2)]
            for line in lines : 
                new_k = k_factors_values[i]/ref_k_val
                if line in table[str(at_num)] : 
                    sig_val = table[str(at_num)][line]["cs"]
                    new_value = ref_sig_val*new_k/sig_val
                    new_table, new_mdata = modify_table_lines(table,mdata,[at_num],line,new_value)
    return new_table,new_mdata
            

def modify_table_lines (table, mdata, elements, line, coeff) :
    r"""
    Modify the cross section of the lines of the selected elements in the input table.

    Parameters
    ----------
    table : dict
        The table of the X-ray emission cross sections.
    mdata : dict
        The metadata of the table.
    elements : list
        The list of the atomic numbers of the elements to modify.
    line : str
        The regex of the line to modify. It has to correspond to IUPAC notation.
    coeff : float
        The coefficient to multiply the cross section of the selected lines.
    
    Returns
    -------
    new_table : dict
        The modified table of the X-ray emission cross sections.
    new_mdata : dict
        The modified metadata of the table.

    Notes
    -----
    X-ray line regex examples :  input "L" will modify all the L lines, input "L3" will modifiy all the L3 lines,
    input "L3M2" will modify the "L3M2" line. 
    """ 
    if mdata["lines"] :
        for elt in elements : 
            for key in table[str(elt)].keys() :
                if re.match(r"^{}".format(line),key) : 
                    table[str(elt)][key]["cs"] *=coeff
                    if "modifications" in mdata : 
                        mdata["modifications"][str(elt) + "_" + key] = coeff
                    else : 
                        mdata["modifications"] = {}
                        mdata["modifications"][str(elt) + "_" + key] = coeff
                        
    else :
        print("You need to enable line notation")
    return table, mdata

def save_table (filename, table, mdata) : 
    r"""
    Saves a table and its metadata in a json file.
    The structure of the json file is compliant with espm.
    """
    d = {}
    d["table"] = table
    d["metadata"] = mdata
    with open(filename,"w") as f :
        json.dump(d,f,indent = 4)
        
def get_k_factor (table, mdata, element, line, range = 0.5, ref_elt = "14", ref_line = "KL3", ref_range = 0.5) : 
    r"""
    Obtain the k-factor of a line from an emtables, X-ray emission cross section table.

    Parameters
    ----------
    table : dict
        The table of the X-ray emission cross sections.
    mdata : dict
        The metadata of the table.
    element : int
        The atomic number of the element to use.
    line : str
        The regex of the line to use. It has to correspond to IUPAC notation.
    range : float
        The energy range to use for the integration of the cross section of the line. For example, if range = 0.5, the integration will be done between the energy of the line - 0.5 and the energy of the line + 0.5. We do so that when you select the "KL3" line, it integrates around it and make it correspond to the K-alpha bunch of lines.
    ref_elt : int
        The atomic number of the element to use as a reference for the k-factor. The default reference line is Si "KL3" with an integration range of 0.5.
    ref_line : str
        The regex of the line to use as a reference for the k-factor. It has to correspond to IUPAC notation.
    ref_range : float
        The energy range to use for the integration of the cross section of the reference line.
    
    Returns
    -------
    k_factor : float
        The k-factor of the line. It does not take into account the absorption correction.
    """
    ref_cs = 0.0
    cs = 0.0
    if mdata["lines"] :
        ref_en = table[str(ref_elt)][ref_line]["energy"]
        for key in table[str(ref_elt)].keys() :
            en = table[str(ref_elt)][key]["energy"]
            if (en < ref_en + ref_range) and (en > ref_en - ref_range) : 
                ref_cs += table[str(ref_elt)][key]["cs"]

        elt_en = table[str(element)][line]["energy"]
        for key in table[str(element)].keys() :
            en = table[str(element)][key]["energy"]
            if (en < elt_en + range) and (en > elt_en - range) : 
                cs += table[str(element)][key]["cs"]
        
    else :
        print("You need to enable line notation")

    return cs/ref_cs