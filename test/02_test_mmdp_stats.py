
import unittest
import numpy as np
from collections import deque

from MMDP.statsUpdate import *


class TestStatsUpdate(unittest.TestCase):

    def setUp(self):

        #Create temporary similarity matrices file for testing
        self.sim_mat = np.array([
            [0, 0.2, 0.4, 0.7, 0.1],
            [0.2, 0, 0.6, 0.3, 0.5],
            [0.4, 0.6, 0, 0.3, 0.9],
            [0.7, 0.3, 0.3, 0, 0.8],
            [0.1, 0.5, 0.9, 0.8, 0]
        ])
        

    def test_initialise_stats(self):

        solution = [1, 2, 4]
        min_dist, sum_dist, min_dist_count = initialise_stats(self.sim_mat, solution)

        #Check size of the stat lists
        self.assertEqual(len(min_dist.keys()), len(self.sim_mat))
        self.assertEqual(len(sum_dist.keys()), len(self.sim_mat))
        self.assertEqual(len(min_dist_count.keys()), len(self.sim_mat))

        #Check a few values to ensure the function works correctly
        self.assertAlmostEqual(min_dist[0], 0.1)
        self.assertAlmostEqual(sum_dist[2], 1.5)
        self.assertEqual(min_dist_count[3], 2)

    
    def test_drop_update(self):

        solution = [2, 4, 1]
        drop_elem = 2
        min_dist = {0: 0.1, 1: 0.5, 2: 0.6, 3: 0.3, 4: 0.5}
        sum_dist = {0: 0.7, 1: 1.1, 2: 1.5, 3: 1.4, 4: 1.4}
        min_dist_count = {0: 1, 1: 1, 2: 1, 3: 2, 4: 1}
        drop_min_dist, drop_sum_dist, drop_min_dist_count = drop_update(self.sim_mat, solution, min_dist, sum_dist, min_dist_count, drop_elem)

        #Check size of the stat lists
        self.assertEqual(len(drop_min_dist.keys()), len(self.sim_mat))
        self.assertEqual(len(drop_sum_dist.keys()), len(self.sim_mat))
        self.assertEqual(len(drop_min_dist_count.keys()), len(self.sim_mat))

        #Check a few values to ensure the function works correctly
        self.assertAlmostEqual(drop_min_dist[0], 0.1)
        self.assertAlmostEqual(drop_sum_dist[2], 1.5)
        self.assertEqual(drop_min_dist_count[3], 1)


    def test_add_update(self):

        add_elem = 3
        min_dist = {0: 0.1, 1: 0.5, 2: 0.6, 3: 0.3, 4: 0.5}
        sum_dist = {0: 0.3, 1: 0.5, 2: 1.5, 3: 1.1, 4: 0.5}
        min_dist_count = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}
        add_min_dist, add_sum_dist, add_min_dist_count = add_update(self.sim_mat, min_dist, sum_dist, min_dist_count, add_elem)

        #Check size of the stat lists
        self.assertEqual(len(add_min_dist.keys()), len(self.sim_mat))
        self.assertEqual(len(add_sum_dist.keys()), len(self.sim_mat))
        self.assertEqual(len(add_min_dist_count.keys()), len(self.sim_mat))

        #Check a few values to ensure the function works correctly
        self.assertAlmostEqual(add_min_dist[0], 0.1)
        self.assertAlmostEqual(add_sum_dist[2], 1.8)
        self.assertEqual(add_min_dist_count[3], 1)


    def test_create_neighborhood(self):

        #Check if function drops the oldest element
        solution = [2, 4, 1]
        min_dist = {0: 0.1, 1: 0.5, 2: 0.6, 3: 0.3, 4: 0.5}
        min_options = {3: 0.3, 0: 0.1}
        iter_values = [0, 3, 1, 0, 2]

        drop_elem, sort_options = create_neighborhood(solution, min_dist, iter_values, max_streak=0, plateau=10)
        self.assertEqual(drop_elem, 2)
        self.assertEqual(sort_options, min_options)


    def test_search_add_elem(self):

        solution = [2, 4]
        sort_options = {1: 0.3, 3: 0.3}
        sum_dist = {0: 0.3, 1: 0.5, 2: 1.5, 3: 1.1, 4: 0.5}

        #Check if bilevel is interpreted correctly
        add_elem_1 = search_add_elem(sort_options, sum_dist, solution, bilevel=False)
        self.assertIn(add_elem_1, {1, 3})

        add_elem_2 = search_add_elem(sort_options, sum_dist, solution, bilevel=True)
        self.assertEqual(add_elem_2, 3)


    def test_obj_values(self):

        min_dist = {0: 0.1, 1: 0.5, 2: 0.6, 3: 0.3, 4: 0.5}
        sum_dist = {0: 0.7, 1: 1.1, 2: 1.5, 3: 1.4, 4: 1.4}
        solution = [2, 4, 1]
        min_pair, sum_pair = obj_values(min_dist, sum_dist, solution)

        #Check if function returns right value
        self.assertEqual(min_pair, 0.5)
        self.assertAlmostEqual(sum_pair, 2)

    
    def test_adaptive(self):

        #Test base size initialisation
        base_size, _ = adaptive_tabu_size(plateau=5, max_size=10, min_size=3, base_size=3, no_gain=0, iterations=4, max_streak=0)
        self.assertEqual(base_size, 3)

        #Test no gain increase
        base_size, _ = adaptive_tabu_size(plateau=5, max_size=10, min_size=3, base_size=4, no_gain=1, iterations=5, max_streak=0)
        self.assertEqual(base_size, 5)

        #Test improve reset
        base_size, _ = adaptive_tabu_size(plateau=5, max_size=10, min_size=3, base_size=5, no_gain=0, iterations=54, max_streak=0)
        self.assertEqual(base_size, 3)

        #Test plateau reset
        base_size, max_streak = adaptive_tabu_size(plateau=5, max_size=10, min_size=3, base_size=10, no_gain=10, iterations=50, max_streak=6)
        self.assertEqual(base_size, 3)
        self.assertEqual(max_streak, 0)

        #Test maximum size
        base_size, max_streak = adaptive_tabu_size(plateau=5, max_size=7, min_size=3, base_size=7, no_gain=4, iterations=8, max_streak=0)
        self.assertEqual(base_size, 7)
        self.assertEqual(max_streak, 1)


    def test_asp_by_default(self):

        sort_options = {1: 0.3, 3: 0.3}
        drop_elem = 1
        tabu_list = deque([[(1,2), 4], [(1,4), 3], [(4,5), 0]], maxlen=3)
        add_elem = aspiration_by_default(sort_options, drop_elem, tabu_list)
        self.assertEqual(add_elem, 2)

        sort_options = {1: 0.3, 3: 0.3}
        drop_elem = 4
        tabu_list = deque([[(1,2), 4], [(1,4), 3], [(4,5), 0]], maxlen=3)
        add_elem = aspiration_by_default(sort_options, drop_elem, tabu_list)
        self.assertEqual(add_elem, 1)

