#!/usr/bin/env python3

from MMDP.dropAddTS import computeSubset
from MMDP.Expand import expandSubset
from MDP.TSMA import compute_MDP_tabu

import matplotlib.pyplot as plt
import numpy as np

##################

import argparse

class CustomFormatter(argparse.RawTextHelpFormatter):
    pass

parser = argparse.ArgumentParser(description="Solve Diversity Problems for protein sequence and structure datasets", formatter_class=CustomFormatter)
parser.add_argument('-hd', '--heading', help="Path to the heading json file", type=str, required=True)
parser.add_argument('-d', '--similarity', help="Path to the similarity npy file", type=str, required=True)
parser.add_argument('-e', '--expand', help="Path to the subset id txt file", type=str, required=False)
parser.add_argument('-k', '--subset_size', help='Subset size', type=int, required=True)
parser.add_argument('-s', '--solver', type=int, choices=[0, 1, 2, 3], default=0, required=False,
                    help="Solver(s) to use (default: 0): \n"
                    " 0 - Solve all three problems\n"
                    " 1 - MaxSum diversity problem \n"
                    " 2 - MaxMin diversity problem \n"
                    " 3 - Bi-level MaxSum diversity problem\n")
parser.add_argument('-m', '--measure', type=int, choices=[0, 1, 2, 3], default=0, required=False,
                    help="Measure(s) to use (default: 0): \n"
                    " 0 - Use all three measures\n"
                    " 1 - Sequence Pairwise Identity\n"
                    " 2 - Sequence Pairwise Similarity\n"
                    " 3 - Structural Similarity")

args = parser.parse_args()
_HEADPATH = args.heading
_SIMPATH = args.similarity
_IDPATH = args.expand
_K = args.subset_size
_SOLVER = args.solver
_MEASURE = args.measure

##################


solver_mapping = {0: 'all', 1 : 'mdp', 2 : 'mmd', 3 : 'mmdp'}
solver_method = {
            1: {'func': lambda: compute_MDP_tabu(_SIMPATH, _HEADPATH, _K), 'prefix': 'mdp_subset'},
            2: {'func': lambda: expandSubset(_SIMPATH, _HEADPATH, _IDPATH, _K, False) if _IDPATH else computeSubset(_SIMPATH, _HEADPATH, _K, False),
                'prefix': 'mmd_expand' if _IDPATH else 'mmd_subset'},
            3: {'func': lambda: expandSubset(_SIMPATH, _HEADPATH, _IDPATH, _K, True) if _IDPATH else computeSubset(_SIMPATH, _HEADPATH, _K, True),
                'prefix': 'mmdp_expand' if _IDPATH else 'mmdp_subset'}
        }

measure_mapping = {0: 'all', 1 : 'id', 2 : 'sim', 3 : 'str'}
measure_method = {
        'id': 'Sequence Identity',
        'sim': 'Sequence Similarity',
        'str': 'Structural Similarity'
    }


def plot_res(sim_list, solver_title, measure_title):

    """
    Plot distribution of subset similarities
    """

    #Skip if 'all'
    if solver_title == 'all' or measure_title == 'all':
        return
    
    file_title = f'{solver_title}_{_K}_{measure_title}_dist.pdf'
    measure = measure_method.get(measure_title, '')

    fig, axs = plt.subplots()
    plt.hist(sim_list, bins=np.linspace(0, 1, num=20), histtype='step')
    plt.ylim(0, 5000)
    plt.title(f"Solution Similarity Distribution: K={_K}, Solver={solver_title.upper()}, Measure={measure}", fontsize=10, fontweight='bold', wrap=True)

    mean = round(np.mean(sim_list), 3)
    std = round(np.std(sim_list), 3)
    min = round(np.min(sim_list), 3)
    max = round(np.max(sim_list), 3)
    sum = round(np.sum(np.fromiter((1-i for i in sim_list), dtype=float)), 3)

    plt.text(0, 4000, f"Average: {mean}±{std} \nMin: {min} \nMax: {max} \nSum distance: {sum}")

    plt.savefig(file_title)
    plt.close()


def main():

    if _K != 0:

        for solver, details in solver_method.items():

            #Map modes to solver functions
            if _SOLVER == 0 or _SOLVER == solver:
                headings, sim_list = details['func']()
                data_to_write = headings

                for mode, measure in measure_mapping.items():
                    if _MEASURE == 0 or _MEASURE == mode:
                        #Skip creaing 'all' files
                        if solver == 0 or mode == 0:
                            continue

                        with open(f"{details['prefix']}_{_K}_{measure}.txt",'w') as f:
                            for i in data_to_write:
                                f.write(i+'\n')

                        plot_res(sim_list, solver_mapping[solver], measure)


if __name__ == '__main__':
    main()
