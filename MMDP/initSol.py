
import numpy as np
import json


def initialise_matrix(sim_file):

    """
    This function switches the similarity matrices (.npy) into distance matrices
    """

    #Load in similarity matrix
    similarity_matrix = np.load(sim_file)

    #Change all diagnol values into 1
    for i in range(0, len(similarity_matrix)):
        similarity_matrix[i][i] = 1

    #Convert similarity matrix to distance matrix
    distance_matrix = 1 - similarity_matrix

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


def constructive_alg(distance_matrix, subset_size, bilevel):

    """
    This function takes in the distance matrix and subset size and return the initial solution of the mmdp through greedy
    The set returned by the function will contain indices of elements
    """

    #Check bilevel condition
    if not isinstance(bilevel, bool):
        raise ValueError('Invalid input: bilevel input must be True/False')

    #Choose the initial point in the matrix that maximizes the sum of distances towards all the other points
    init_point = np.argmax(np.sum(distance_matrix, axis=1))
    init_sol = [init_point]

    #Initialise iter values for all elements and also the initial point
    iter_values = [0] * len(distance_matrix)
    iter_values[init_point] = 1

    #Initialise the sum distance of the solution set, in this case since there is only one point in the solution, it's 0
    init_sum = 0

    #Initialise iteration counter
    iterations = 2

    while len(init_sol) < subset_size:

        #Initialise mininimum inter distance of the set and point to be appended to solution set
        min_dist_to_s = float('-inf')
        temp_selection = None

        #Go through the whole matrix
        for i in range(0, len(distance_matrix)):
            
            #If the indice is already in the set, pass
            if i in init_sol:
                continue

            #Reset the max_min_dist of the set to infinite everytime when selecting the next candidate to add
            max_min_dist = float('inf')

            #Set the max_min_dist to the distance between elements in and outside solution set
            for j in init_sol:
                if distance_matrix[i,j] < max_min_dist:
                    max_min_dist = distance_matrix[i, j]

            #If min_dist_to_s is smaller than max_min_dist, min_dist_to_s takes value of max_min_dist
            #So our min_dist of the set keeps increasing until i runs through all len(distance_matrix), the i that give the biggest min_dist is the temp_selection
            if max_min_dist > min_dist_to_s:

                min_dist_to_s = max_min_dist
                temp_selection = i
                print('MAX MIN ADD ' + str(temp_selection))
            
            #This is the tie-breaking rule, if max_min_dist equals min_dist_to_s, change temp_selection to the point that gives a higher sum distance
            #This tie-breaking rule only applies if the bi-level model is in use
            elif bilevel and max_min_dist == min_dist_to_s:

                if init_sum + sum(distance_matrix[i, j] for j in init_sol) > init_sum + sum(distance_matrix[temp_selection, j] for j in init_sol):
                    print('BREAKING TIE: adding ' + str(i) + ' will give a sum ' + str(init_sum + sum(distance_matrix[i, j] for j in init_sol)) + ' rather than '
                          + str(temp_selection) + ' giving sum ' + str(init_sum + sum(distance_matrix[temp_selection, j] for j in init_sol)))
                    temp_selection = i

        #Append temp_selection to solution set and update sum distance
        init_sum += sum(distance_matrix[temp_selection, j] for j in init_sol)
        init_sol += [temp_selection]

        #Update the iter values of the added item and increment iter counter
        iter_values[temp_selection] = iterations
        iterations += 1

        print('Adding '+ str(temp_selection))

    return init_sol, iter_values, iterations
