
from copy import deepcopy

from .initSol import *
from .statsUpdate import *
from .tabuList import tabuList


def dropAddTS(distance_matrix, solution, iter_values, iterations, min_dist, sum_dist, min_dist_count, subset_size, bilevel):

    """
    This is the main algorithm to perform DropAddTS
    """
    
    #Initialise no_gain, max_no_gain and max_steps
    no_gain = 0
    max_no_gain = 2000
    max_steps = 50000
    plateau = 200
    max_streak = 0
    super_size = distance_matrix.shape[0]
    max_size = round(super_size*0.5)
    min_size = round(subset_size*0.5)
    base_size = min_size
    tabu_list = tabuList(base_size, base_size)

    #Initialise best solution and best score
    best_solution = []

    #While exit criterion is not reached
    for i in range(0, max_steps):

        #Calculate the score of the solution before dropping
        min_pair, sum_pair = obj_values(min_dist, sum_dist, solution)

        #If no best solution yet, set the current solution as the best
        if len(best_solution) == 0:
            best_solution = deepcopy(solution)
            best_min = min_pair
            best_sum = sum_pair

        tabu_list.increment_tabu_tenure()
        tabu_list.remove_expired_tabus()

        drop_elem, sort_options = create_neighborhood(solution, min_dist, iter_values, max_streak, plateau)
        #Keep a copy of neighbourhood in case of aspiration by default
        default_asp = deepcopy(sort_options)

        #Choose the oldest point in solution to drop
        new_sol = deepcopy(solution)
        new_sol.remove(drop_elem)

        #Create min_dist, sum_dist, min_dist_count for each point in the superset after dropping the element
        min_dist, sum_dist, min_dist_count = drop_update(distance_matrix, solution, min_dist, sum_dist, min_dist_count, drop_elem)

        while True:

            #Check if neighbourhood is empty
            if len(sort_options.keys()) != 0:
                add_elem = search_add_elem(sort_options, sum_dist, new_sol, bilevel)

                #Add the potential point to new_sol, update all stats and calculate the objective value of the new_sol
                new_sol.append(add_elem)
                temp_min_dist = deepcopy(min_dist)
                temp_sum_dist = deepcopy(sum_dist)
                temp_min_dist_count = deepcopy(min_dist_count)
                temp_min_dist, temp_sum_dist, temp_min_dist_count = add_update(distance_matrix, temp_min_dist, temp_sum_dist, temp_min_dist_count, add_elem)
                new_min, new_sum = obj_values(temp_min_dist, temp_sum_dist, new_sol)

                if tabu_list.check_tabu((drop_elem, add_elem)):
                    print('TABU')
                    if new_min > best_min:
                        tabu_list.append_tabu_list((drop_elem, add_elem))
                        best_solution = deepcopy(new_sol)
                        best_min = deepcopy(new_min)
                        best_sum = deepcopy(new_sum)

                        no_gain = 0
                        print('NO GAIN UPDATED: ', no_gain)
                        print(f'Iter {iterations} ASPIRATION MIN: ', best_min)
                        break
                    
                    elif bilevel and (new_min == best_min and new_sum > best_sum):
                        print('BILEVEL!')
                        tabu_list.append_tabu_list((drop_elem, add_elem))
                        best_solution = deepcopy(new_sol)
                        best_min = deepcopy(new_min)
                        best_sum = deepcopy(new_sum)

                        no_gain = 0
                        print('NO GAIN UPDATED: ', no_gain)
                        print(f'Iter {iterations} ASPIRATION SUM: ', best_sum)
                        break

                    else:
                        del sort_options[add_elem]
                        new_sol.remove(add_elem)
                        print('NO ASPIRATION. CONTINUE')
                        continue

                else:
                    tabu_list.append_tabu_list((drop_elem,add_elem))
                    print('NOT TABU')
                    if bilevel:
                        print('BILEVEL!')
                        if new_min > best_min or (new_min == best_min and new_sum > best_sum):
                            best_solution = deepcopy(new_sol)
                            best_min = deepcopy(new_min)
                            best_sum = deepcopy(new_sum)

                            no_gain = 0

                            if new_min > best_min:
                                print('NO GAIN UPDATED: ', no_gain)
                                print(f'Iter {iterations} New Best Min: ', best_min)
                            else:
                                print('NO GAIN UPDATED: ', no_gain)
                                print(f'Iter {iterations} New Best Sum: ', best_sum)
                        else:
                            no_gain += 1
                            print('NO GAIN UPDATED: ', no_gain)
                        
                        break

                    else:
                        if new_min > best_min:
                            print('MMD!')
                            best_solution = deepcopy(new_sol)
                            best_min = deepcopy(new_min)
                            best_sum = deepcopy(new_sum)

                            no_gain = 0
                            print('NO GAIN UPDATED: ', no_gain)
                            print(f'Iter {iterations} New Best Min: ', best_min)
                        else:
                            no_gain += 1
                            print('NO GAIN UPDATED: ', no_gain)
                            
                        break

            #In case of empty neighbourhood, aspiration by default invokes the oldest tabu move
            else:
                add_elem = aspiration_by_default(default_asp, drop_elem, tabu_list.tabu_list)
                new_sol.append(add_elem)
                temp_min_dist = deepcopy(min_dist)
                temp_sum_dist = deepcopy(sum_dist)
                temp_min_dist_count = deepcopy(min_dist_count)
                temp_min_dist, temp_sum_dist, temp_min_dist_count = add_update(distance_matrix, temp_min_dist, temp_sum_dist, temp_min_dist_count, add_elem)

                tabu_list.append_tabu_list((drop_elem,add_elem))
                print('ASPIRATION BY DEFAULT!')

                break
        
        if no_gain == max_no_gain:
            print(max_no_gain, ' ITERATIONS WITHOUT IMPROVEMENT, STOPPING')
            break
    
        solution = new_sol
        min_dist = temp_min_dist
        sum_dist = temp_sum_dist
        min_dist_count = temp_min_dist_count

        #Update the iter_values of added element
        iter_values[drop_elem] = iterations
        iter_values[add_elem] = iterations

        iterations += 1
        base_size, max_streak = adaptive_tabu_size(plateau, max_size, min_size, base_size, no_gain, iterations, max_streak)
        tabu_list.adaptive_size(base_size)
        print('tabu list size: ', base_size)

        print('Iter: ', iterations)
        print('Best Min: ', best_min)
        print('Best Sum: ', best_sum)

    print('REACHED MAX STEPS')
    return best_solution, best_min, best_sum


def computeSubset(sim_file, heading_file, subset_size, bilevel):

    distance_matrix = initialise_matrix(sim_file)
    ind_dict = initialise_headings(heading_file)
    init_sol, iter_values, iterations = constructive_alg(distance_matrix, subset_size, bilevel)
    min_dist, sum_dist, min_dist_count = initialise_stats(distance_matrix, init_sol)

    best_solution, best_min, best_sum = dropAddTS(distance_matrix, init_sol, iter_values, iterations, min_dist, sum_dist, min_dist_count, subset_size, bilevel)
    
    print('Best solution: ', best_solution)
    print('Best min: ', best_min)
    print('Best sum: ', best_sum)

    headings = [ind_dict[k] for k in best_solution]

    sim_list = []

    for i in range(len(best_solution)):
        for j in range(i+1, len(best_solution)):
            sim_list.append(1 - distance_matrix[best_solution[i], best_solution[j]])

    return headings, sim_list

