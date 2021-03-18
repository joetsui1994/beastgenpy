##Functions for making dictionaries containing predictors and other things required for GLMs

from Bio import SeqIO
from geopy import distance
from collections import defaultdict
import csv
import numpy as np
import statistics

def make_vector(matrix, dim):
    indices = np.triu_indices(dim,1) #get indices of top triangle, moved right by one to leave out diagonal
    upper = matrix[indices] #Create matrix of top triangle
    lowerprep = np.transpose(matrix) #Transpose matrix, so that lower triangle will be read in the desired order
    lower = lowerprep[indices] #Use same indices, but gets lower triangle of original matrix this time

    #turn arrays into strings so there are no commas 
    below_diag = np.array2string(lower, formatter = {'float':lambda lower: "%.1f" % lower}) 
    above_diag = np.array2string(upper, formatter = {'float': lambda upper: "%.1f" % upper})

    vector = above_diag + below_diag #make one vector that is the top triangle read horizontally, and lower triangle read vertically
    vector = vector.replace("]["," ").replace("[","").replace("]","")
    
    return vector

def process_directional_predictors(trait_name, predictor_file):

    ##process folder, make sure 
    #format needs to be a column with a trait value and then one column per predictor value. Separate csvs for different traits
    predictor_list = []
    predictor_dict = defaultdict(dict)
    with open(predictor_file) as f:
        data = csv.DictReader(f)
        headers = data.fieldnames
        for i in headers:
            if i != trait_name:
                predictor_list.append(i)

        for predictor in predictor_list:
            inner_dict = {}
            for line in data:
                inner_dict[line[trait_name]] = float(line[predictor])

            predictor_dict[predictor] = inner_dict

    sorted_predictor_values = defaultdict(list)
    for predictor, values_set in predictor_dict.items():
        ordered_values = sorted(values_set.items())
        for i in ordered_values:
            sorted_predictor_values[predictor].append(i[1])

    ## now going to make a matrix ##
    predictor_dict = {}
    for predictor, values in sorted_predictor_values.items():
        dim = len(values)
        frommatrix = np.zeros((dim,dim)) 
        tomatrix = np.zeros((dim,dim))

        key_from = f'{predictor}_origin'
        key_to = f'{predictor}_destination'

        for i, option in enumerate(values):
            frommatrix[i,:] = option
            tomatrix[:,i] = option
        
        from_value = make_vector(frommatrix, dim)  
        to_value = make_vector(tomatrix,dim)

        predictor_dict[key_from] = from_value
        predictor_dict[key_to] = to_value

    return predictor_dict



def make_twoway_REmatrices(trait_options_dict):

    re_matrices = defaultdict(dict)

    for trait, options in trait_options_dict.items():
        trait_rand_design = {}

        #Create nxn matrices of zeros ready for populating
        dim = len(options)
        frommatrix = np.zeros((dim,dim)) 
        tomatrix = np.zeros((dim,dim))

        #These loops make from and to matrices for each trait, and then passes them through the function to get random effect vector
        for i, option in enumerate(options):
            key_from = f'{option}_from'
            key_to = f'{option}_to'
            if i == 0:
                frommatrix[i] = 1.0
                frommatrix[i,i] = 0.0

                tomatrix[:,i] = 1.0
                tomatrix[i,i] = 0.0
                
            else:
                frommatrix[i] = 1.0
                frommatrix[i-1] = 0.0
                frommatrix[i,i] = 0.0
                
                tomatrix[:,i] = 1.0
                tomatrix[:,i-1] = 0.0
                tomatrix[i,i] = 0.0
 
            trait_rand_design[key_from] = make_vector(frommatrix, dim)
            trait_rand_design[key_to] = make_vector(tomatrix,dim)

        re_matrices[trait] = trait_rand_design

    return re_matrices

def calculate_binomial_likelihoods(trait_options_dict):

    bin_probs  = {}
    
    for trait, options in trait_options_dict.items():
        n = len(options)
        p = 1 - (0.5**(1/n))
        bin_probs[trait] = p
    
    return bin_probs
