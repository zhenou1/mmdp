
from .initSol import initialise_matrix, initialise_headings
from .statsUpdate import *
from .dropAddTS import dropAddTS
from copy import deepcopy
import sys


def load_curr_subset(subset_file, ind_dict):

    """
    This function loads in currently existing subset. subset_file should be the a text file of id of the subset members.
    """

    subset_id = []

    with open(subset_file) as f:
        for i in f.readlines():
            subset_id.append(i.strip())

    #Reverse look up of indices of the existing subset id in the distance matrix
    rev_dict = {v: k for k, v in ind_dict.items()}
    curr_subset = [rev_dict[k] for k in subset_id]

    return curr_subset


def expand_init(distance_matrix, curr_subset, subset_size, bilevel):

    """
    This function constructs an expanded initial solution to be modified later in main search, using the existing subset
    as the basis, following the same greedy constructive method used in init_sol.py
    """

    #Initialise iter values for all elements and iteration counter
    iter_values = [0] * len(distance_matrix)
    iterations = 1
    #Set iteration counter for existing subset elements as infinite to avoid being dropped
    for curr in curr_subset:
        iter_values[curr] = float('inf')
    
    #Initialise summed distance using the existing subset
    init_sum = 0
    for i in curr_subset:
        for j in curr_subset:
            init_sum += distance_matrix[i,j]/2

    #Separate the expanded solution
    expanded_init = deepcopy(curr_subset)

    #Before reaching the expanded size, repeat the same greedy constructive algorithm as constructing initial solution from scratch
    while len(expanded_init) < len(curr_subset) + subset_size:

        min_dist_to_s = float('-inf')
        temp_selection = None

        for i in range(0, len(distance_matrix)):

            if i in expanded_init:
                continue

            max_min_dist = float('inf')

            for j in expanded_init:
                if distance_matrix[i,j] < max_min_dist:
                    max_min_dist = distance_matrix[i, j]

            if max_min_dist > min_dist_to_s:

                min_dist_to_s = max_min_dist
                temp_selection = i
                print('MAX MIN ADD ' + str(temp_selection))

            elif bilevel and max_min_dist == min_dist_to_s:

                if init_sum + sum(distance_matrix[i, j] for j in expanded_init) > init_sum + sum(distance_matrix[temp_selection, j] for j in expanded_init):
                    print('BREAKING TIE: adding ' + str(i) + ' will give a sum ' + str(init_sum + sum(distance_matrix[i, j] for j in expanded_init)) + ' rather than '
                          + str(temp_selection) + ' giving sum ' + str(init_sum + sum(distance_matrix[temp_selection, j] for j in expanded_init)))
                    temp_selection = i

        init_sum += sum(distance_matrix[temp_selection, j] for j in expanded_init)
        expanded_init += [temp_selection]

        iter_values[temp_selection] = iterations
        iterations += 1

        print('Adding '+ str(temp_selection))

    return expanded_init, iter_values, iterations


def expandSubset(sim_file, heading_file, subset_file, subset_size, bilevel):

    distance_matrix = initialise_matrix(sim_file)
    ind_dict = initialise_headings(heading_file)
    curr_subset = load_curr_subset(subset_file, ind_dict)
    expanded_init, iter_values, iterations = expand_init(distance_matrix, curr_subset, subset_size, bilevel)
    min_dist, sum_dist, min_dist_count = initialise_stats(distance_matrix, expanded_init)

    best_expand, best_min, best_sum = dropAddTS(distance_matrix, expanded_init, iter_values, iterations, min_dist, sum_dist, min_dist_count, subset_size, bilevel)

    print('Best expanded solution: ', best_expand)
    print('Best min: ', best_min)
    print('Best sum: ', best_sum)

    headings = [ind_dict[k] for k in best_expand]

    sim_list = []

    for i in range(len(best_expand)):
        for j in range(i+1, len(best_expand)):
            sim_list.append(1 - distance_matrix[best_expand[i], best_expand[j]])

    return headings, sim_list

if __name__ == '__main__':
    expandSubset(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])