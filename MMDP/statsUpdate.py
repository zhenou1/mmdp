
from copy import deepcopy
import numpy as np
import random


def initialise_stats(distance_matrix, solution):

    """
    This function calculates the minimum distance for every element in superset to solution elements,
    its distance sums to all solution elements, and number of solution elements having it as the closest point
    """

    min_dist = {}
    sum_dist = {}
    min_dist_count = {}

    for i in range(len(distance_matrix)):

        #Get a list of distances from the element i to all solution elements
        dis_to_solu = [distance_matrix[i, j] for j in solution if i != j]

        min_dist[i] = min(dis_to_solu)
        sum_dist[i] = round(sum(dis_to_solu), 10)
        min_dist_count[i] = dis_to_solu.count(min_dist[i])

    return min_dist, sum_dist, min_dist_count


def drop_update(distance_matrix, solution, min_dist, sum_dist, min_dist_count, drop_elem):

    """
    This function updates min_dist, sum_dist, min_dist_count after dropping an element from the solution
    """

    for i in range(len(distance_matrix)):

        #Consider everything in the superset except for the dropped element
        if i == drop_elem:
            continue
        
        #sum_dist of any point in the superset will need to remove the distance from them to the dropped element
        sum_dist[i] = round(sum_dist[i] - distance_matrix[i, drop_elem], 10)

        #No need to modify min_dist or min_dist_count if distance between dropped element and i is bigger than min_dist (the dropped element is not the closest point in the solution for i)
        #If the dropped element is the closest point
        if min_dist[i] == distance_matrix[i, drop_elem]:
            #Decrement min_dist_count if there is more than one closest point to i in the solution
            if min_dist_count[i] > 1:
                min_dist_count[i] = min_dist_count[i] - 1
            #If the dropped element is the only closest point to i, need to recalculated min_dist and min_dist_count for i
            else:
                new_sol = deepcopy(solution)
                new_sol.remove(drop_elem)
                dis_to_solu = [distance_matrix[i, j] for j in new_sol if i != j]
                min_dist[i] = min(dis_to_solu)
                min_dist_count[i] = dis_to_solu.count(min_dist[i])
    
    return min_dist, sum_dist, min_dist_count


def add_update(distance_matrix, min_dist, sum_dist, min_dist_count, add_elem):

    """
    This function updates min_dist, sum_dist, min_dist_count after adding an element to the solution
    """

    for i in range(len(distance_matrix)):

        #Consider everything in the superset except for the added element
        if i == add_elem:
            continue
        
        #sum_dist of any point in the superset will need to add the distance from them to the added element
        sum_dist[i] = round(sum_dist[i] + distance_matrix[i, add_elem], 10)

        #No need to modify min_dist or min_dist_count if distance from i to added point is bigger than min_dist (added point is not the closest to i in solution)
        #If distance from i to added point is the same as min_dist, increment min_dist_count by 1
        if distance_matrix[i, add_elem] == min_dist[i]:
            min_dist_count[i] += 1
        #If distance from i to added point is smaller than min_dist, initialise min_dist_count to 1 and update min_dist
        elif distance_matrix[i, add_elem] < min_dist[i]:
            min_dist_count[i] = 1
            min_dist[i] = distance_matrix[i, add_elem]

    return min_dist, sum_dist, min_dist_count


def create_neighborhood(solution, min_dist, iter_values, max_streak, plateau):

    """
    This function returns the oldest element indices in solution and the sorted options of non-solution indices to be exchanged
    """

    cls = 50

    #Separate drop and add neighborhoods
    sol_iter = {i:iter_values[i] for i in solution}
    min_dist_options = {k: min_dist[k] for k in min_dist if k not in solution}

    #Get the oldest point in solution to drop
    drop_elem = [i for i in sol_iter.keys() if sol_iter[i] == min(sol_iter.values())][0]

    #If tabu list stays at maximum size for plateau iterations, randomly selects an add element from neighbourhood
    if max_streak >= plateau:
        sort_options = dict(random.sample(min_dist_options.items(), cls))

    else:
        #If not, selects add element normally considering move gains
        sort_options = dict(sorted(min_dist_options.items(), key=lambda item: item[1], reverse=True)[:cls])

    return drop_elem, sort_options


def search_add_elem(sort_options, sum_dist, solution, bilevel):

    """
    This function returns the element to be added
    """

    #Get the index of the point maximizing the min_dist from any point in solution
    max_min_value = next(iter(sort_options.values()))
    max_min_ind = []

    for k,v in sort_options.items():
        if v == max_min_value and k not in solution:
            max_min_ind.append(k)
        else:
            break

    #This is for tie-breaking when there are multiple elements in max_min_ind list, temp_selection will be the one giving bigger sum_dist
    if bilevel:
        for k in max_min_ind:
            if k in sum_dist and sum_dist[k] == max([sum_dist[key] for key in max_min_ind]):
                add_elem = k
                break
    #If the bi-level model is not in use, the algorithm picks a random element that maximize the min_dist to add
    else:
        add_elem = np.random.choice(max_min_ind, 1).item()
    
    return add_elem


def obj_values(min_dist, sum_dist, solution):

    """
    This function is the main objective function of the bi-level maxsum problem
    """

    #Get dictionaries of min pairwise and summed pairwise distances for all solution elements
    pair_dist = {k: min_dist[k] for k in solution if k in min_dist}
    pair_sum_dist = {k: sum_dist[k] for k in solution if k in sum_dist}

    #The objective value is the sum of the minimum pairwise distance and the summed pairwise distances of the solution set
    min_pair = min(pair_dist.values())
    sum_pair = round(sum(pair_sum_dist.values())/2, 10) #Because each pair dist will be added twice: sum_pair_a = dist[a,b]+dist[a,c], sum_pair_b = dist[b,a]+dist[b,c]

    return min_pair, sum_pair

def adaptive_tabu_size(plateau, max_size, min_size, base_size, no_gain, iterations, max_streak):

    """
    This function is returns adaptive tabu list size
    """

    #The tabu list increments by 1 every iteration of no gain
    if no_gain > 0 and base_size < max_size:
        return min(max_size, base_size + 1), 0
    
    #If improvements have been made, tabu list resets
    if iterations > base_size + 1 and no_gain == 0:
        return min_size, 0
    
    #If tabu list reaches max size, allow till plateau+1 iterations and reset
    if base_size == max_size:
        max_streak += 1
        if (max_streak - plateau) >= 1:
            return min_size, 0
    
    return base_size, max_streak


def aspiration_by_default(neighbourhood, drop_elem, tabu_list):

    """
    If all neighbours considered are tabu, return the oldest tabu on the list for execution
    """

    neighbour = [k for k in neighbourhood.keys()]
    for i in neighbour:
        if drop_elem > i:
            old_tabu = max((n for n in tabu_list if n[0][1] == drop_elem), key=lambda x: x[1], default=None)
            add_elem = old_tabu[0][0]
        else:
            old_tabu = max((n for n in tabu_list if n[0][0] == drop_elem), key=lambda x: x[1], default=None)
            add_elem = old_tabu[0][1]

    return add_elem