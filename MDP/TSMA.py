from __future__ import print_function

from .tabuSearch import TabuSearch
from .Solution import Solution
from .Move import Move

from copy import deepcopy
import numpy as np
import json


class MEnzDPTabuSearch(TabuSearch):


    def _score(self, sol, use_sim=False):

        score = 0
        mat = self.opt_tuple[0]
        sim_list = []

        (set_indices, _) = sep_indices(sol.val)

        for i in range(0, len(set_indices)):
            for j in range(i + 1, len(set_indices)):
                sim = ((1 - mat[set_indices[i], set_indices[j]])) - (mat[set_indices[i], set_indices[j]]/(1 - mat[set_indices[i], set_indices[j]]))

                score += sim

                sim_list.append(mat[set_indices[i], set_indices[j]])

        if use_sim:
            return score, sim_list
        else:
            return score


    def _create_neighbourhood(self):

        curr_sol = self.curr_sol
        mat = self.opt_tuple[0]
        delta = self.opt_tuple[1]

        (set_indices, non_indices) = sep_indices(curr_sol.val)

        #Create non tabu indice lists
        set_indices_nontabu = []
        non_indices_nontabu = []

        for i in set_indices:
            if not i in self.tabu_list.element_list:
                set_indices_nontabu += [i]

        for i in non_indices:
            if not i in self.tabu_list.element_list:
                non_indices_nontabu += [i]

        #Arbitrary candidate list number
        cls_num = 10
        neighbourhood = []

        #Sort the delta and get the indices of the largest, e.g. cls_num = 10 - keep the indices of elements with biggest 10 deltas
        temp_vals = [(delta[i], i) for i in set_indices]
        temp_vals.sort(reverse=True)
        s_cls = [i for _, i in temp_vals[:cls_num]]

        temp_vals = [(delta[i], i) for i in non_indices]
        temp_vals.sort(reverse=True)
        n_cls = [i for _, i in temp_vals[:cls_num]]

        #Also sort the delta and indices for the non tabu indices to ensure the neighbourhood never gets empty
        temp_vals = [(delta[i], i) for i in set_indices_nontabu]
        temp_vals.sort(reverse=True)
        s_cls_nontabu = [i for _, i in temp_vals[:cls_num]]

        temp_vals = [(delta[i], i) for i in non_indices_nontabu]
        temp_vals.sort(reverse=True)
        n_cls_nontabu = [i for _, i in temp_vals[:cls_num]]

        #alpha is a list with each element in the form of ([i,j], move_gain)
        alpha = []

        #Calculate the move gains for each combinations of swaps, according to the equation delta(i)+delta(j)-dij, here penalty term is included
        for i in s_cls:
            for j in n_cls:
                alpha += [([i, j], delta[i] + delta[j] - ((1 - mat[i, j]))*1.0 - (mat[i, j]/(1 - mat[i, j])))]

        temp_val = float('-inf')
        temp_choice = 0

        for i in alpha:
            if i[1] > temp_val:
                temp_val = i[1]
                temp_choice = i

        #Update the values of 1 and 0, and total score according to above
        #As i (temp_choice[0][0]) is from solution candidate list and j from non-solution, values of 0 and 1 are exchanged
        neighbour = deepcopy(curr_sol)
        neighbour.val[temp_choice[0][0]] = 0
        neighbour.val[temp_choice[0][1]] = 1
        neighbour.fitness = self._score(neighbour)
        path = [temp_choice[0][0], temp_choice[0][1]]
        move = Move(curr_sol, neighbour, path)
        neighbourhood.append(move)

        alpha = []

        #Calculate the move gains for combinations of nontabu swaps
        for i in s_cls_nontabu:
            for j in n_cls_nontabu:
                alpha += [([i, j], delta[i] + delta[j] - ((1 - mat[i, j]))*1.0 - (mat[i, j]/(1 - mat[i, j])))]

        temp_val = float('-inf')
        temp_choice = 0

        for i in alpha:
            if i[1] > temp_val:
                temp_val = i[1]
                temp_choice = i

        #Update the values of 1 and 0, and total score according to above
        #As i (temp_choice[0][0]) is from solution candidate list and j from non-solution, values of 0 and 1 are exchanged
        neighbour = deepcopy(curr_sol)
        neighbour.val[temp_choice[0][0]] = 0
        neighbour.val[temp_choice[0][1]] = 1
        neighbour.fitness = self._score(neighbour)
        path = [temp_choice[0][0], temp_choice[0][1]]
        move = Move(curr_sol, neighbour, path)
        neighbourhood.append(move)

        #neighbourhood is a list of Move objects that has old_sol, new_sol, and the [i,j] move that change between the 2 solutions
        #Here, the neighbourhood is only 2 moves: best from the s_cls and n_cls swap, if it's tabu and no aspiration, it gets removed; best from the nontabu swaps
        return neighbourhood


    def _post_swap_change(self, move):

        mat = self.opt_tuple[0]
        delta = self.opt_tuple[1]
        indices = move.path
        temp_sol = move.new_sol

        (set_indices, non_indices) = sep_indices(temp_sol.val)

        delta[indices[0]] = - (delta[indices[0]]) + (1 - mat[indices[0], indices[1]]) + (mat[indices[0], indices[1]]/(1 - mat[indices[0], indices[1]]))   #+penalty
        delta[indices[1]] = - (delta[indices[1]]) + (1 - mat[indices[0], indices[1]]) - (mat[indices[0], indices[1]]/(1 - mat[indices[0], indices[1]])) #-penalty


        for i in range(0, len(delta)):
            if i in indices:
                continue
            if i in set_indices:
                delta[i] = delta[i] + (1 - mat[indices[0], i]) - (1 - mat[i, indices[1]])- ((mat[indices[0], i])/(1 - mat[indices[0], i])) + ((mat[i, indices[1]])/(1 - mat[i, indices[1]]))
                continue
            if i in non_indices:
                delta[i] = delta[i] - (1 - mat[indices[0], i]) + (1 - mat[i, indices[1]])+ ((mat[indices[0], i])/(1 - mat[indices[0], i])) - ((mat[i, indices[1]])/(1 - mat[i, indices[1]]))
                continue

        self.opt_tuple[1] = delta


def initialise_matrix(sim_file):

    """
    This function switches the similarity matrices (.npy) into distance matrices
    """

    #Load in similarity matrix
    distance_matrix = np.load(sim_file)

    #Change all diagnol values into nan
    for i in range(0, len(distance_matrix)):
        distance_matrix[i][i] = np.nan
        for j in range(i+1, len(distance_matrix)):
            #Change all values of 1 to 0.99 to aid the calculations in penalty terms
            if distance_matrix[i][j] == 1:
                distance_matrix[i][j] = 0.99
                distance_matrix[j][i] = 0.99

    return np.asarray(distance_matrix)


def initialise_headings(heading_file):

    """
    This function switches the heading files (.json) into a dictionary with indices
    """

    #Load in heading file
    with open(heading_file) as heading:
        headings = json.loads(heading.read())

    ind_dict = {}

    #Match the indices with each heading
    for i in range(0, len(headings)):
        ind_dict[i] = headings[i]

    return ind_dict


def random_solution(length, num_picked):

    """
    This produces the intial random solution set for swapping later
    length is the total number of elements in the superset, num_picked is the number of elements to include in the solution subset
    The output of this function is a list of 0s and 1s in random order
    """

    arr = np.array([0] * (length - num_picked) + [1] * num_picked)
    np.random.shuffle(arr)
    return list(arr)


def initialise_delta(mat, sol):

    """
    This delta is the summary value of how much a certain item in the solution or non-solution set varies with the items in the solution set
    mat is the identity matrix, sol is the list of 0s and 1s (solution)
    """

    delta = [0] * len(sol.val)
    (set_indices, non_indices) = sep_indices(sol.val) #separate indices according to the values of 0s and 1s

    for i in set_indices:
        for j in set_indices:
            if i == j:
                continue
            if mat[i, j] == 1:
                continue
            #delta(i) = sum of minus dij for both i,j belong to solution set
            #The sum of the distances times 0.5 because the same values will be added twice for a matrix
            delta[i] += (- (1 - mat[i, j]))*0.5 + (mat[i, j]/(1 - mat[i, j])) #This is the penalty term


    for i in non_indices:
        for j in set_indices:
            if i == j:
                continue
            if mat[i, j] == 1:
                continue
            #delta(i) = sum of dij for i belong in non-solution set and j belong in solution set
            delta[i] += ((1 - mat[i, j]))*0.5 - (mat[i, j]/(1 - mat[i, j])) #This is the penalty term

    return delta


def sep_indices(val):

    """
    Separate the indices of elements in solution set (value of 1) from those in non-solution set (value of 0)
    """

    set_indices = []
    non_indices = []

    for i in range(0, len(val)):
        if val[i] == 1:
            set_indices += [i]
        else:
            non_indices += [i]

    return (set_indices, non_indices)


def compute_MDP_tabu(mat, head, k):

    head = initialise_headings(head)
    mat = initialise_matrix(mat)

    seq_len = len(head)

    ini_sol = Solution(random_solution(seq_len, k))
    #print(ini_sol.val)
    print("Initialising Delta")
    delta = initialise_delta(mat, ini_sol)
    #print(delta)
    results_list = []
    #Decrease tabu list size for small subsets to avoid empty neighbourhood
    subset_size = min(k, 50)
    test = MEnzDPTabuSearch(ini_sol, subset_size, subset_size, 20000, max_wait=2000, opt_tuple=[mat, delta])

    best, score = test.run()
    #print(best.val)
    _, sim_list = test._score(best, True)
    #print(sim_list)

    initial_picked_set = [i for i in range(len(best.val)) if best.val[i] == 1]
    results_list = sorted([head[x] for x in initial_picked_set])
    print('Best score: ', score)

    return results_list, sim_list
