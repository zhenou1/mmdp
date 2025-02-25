

import unittest, json, os, tempfile
import numpy as np
from MDP.TSMA import *
from MDP.Solution import Solution
from MDP.Move import Move


class TestTSMA(unittest.TestCase):


    def setUp(self):

        #Set a fixed random seed for reproducibility in tests
        np.random.seed(42)

        #Create a temporary heading json file for testing
        self.headings = ['Seq1', 'Seq2', 'Seq3', 'Seq4', 'Seq5']

        #Create temporary similarity matrices file for testing
        self.sim_mat = np.array([
            [0, 0.2, 0.4, 0.3, 0.1],
            [0.2, 0, 0.6, 0.7, 0.5],
            [0.4, 0.6, 0, 0.5, 1.0],
            [0.3, 0.7, 0.5, 0, 0.8],
            [0.1, 0.5, 1.0, 0.8, 0]
        ])

        self.super_size = 5
        self.subset_size = 3

        self.temp_dir = tempfile.mkdtemp()
        self.sim_file = os.path.join(self.temp_dir, 'sim_mat.npy')
        self.head_file = os.path.join(self.temp_dir, 'headings.json')
        np.save(self.sim_file, self.sim_mat)
        with open(self.head_file, 'w') as f:
            json.dump(self.headings, f)

        self.val = [0, 1, 1, 0, 1]
        self.sol = Solution(self.val)
        self.delta = [0.122, 2.05, 100.295, -6.833, 99.745]
        self.dist_mat =  np.array([
            [0, 0.2, 0.4, 0.3, 0.1],
            [0.2, 0, 0.6, 0.7, 0.5],
            [0.4, 0.6, 0, 0.5, 0.99],
            [0.3, 0.7, 0.5, 0, 0.8],
            [0.1, 0.5, 0.99, 0.8, 0]
        ])


    def tearDown(self):

        #Clean up temporary files
        os.remove(self.sim_file)
        os.remove(self.head_file)
        os.rmdir(self.temp_dir)


    def test_initialise_matrix(self):

        #Test matrix initialization
        dist_mat = initialise_matrix(self.sim_file)

        #Check return type
        self.assertIsInstance(dist_mat, np.ndarray)

        #Check diagonal elements
        for i in range(len(dist_mat)):
            self.assertTrue(np.isnan(dist_mat[i, i]))

        #Check a few values to ensure distance transformation
        self.assertAlmostEqual(dist_mat[0, 1], 0.2)
        self.assertAlmostEqual(dist_mat[2, 4], 0.99)
        self.assertAlmostEqual(dist_mat[3, 1], 0.7)


    def test_initialise_headings(self):

        #Test headings initialization
        ind_dict = initialise_headings(self.head_file)

        #Test if dictionary maps correctly
        for i in range(len(self.headings)):
            self.assertEqual(ind_dict[i], self.headings[i])


    def test_random_sol(self):

        #Test if number of 1s can be correctly produced
        arr = random_solution(self.super_size, self.subset_size)
        self.assertEqual(len(arr), 5)
        self.assertEqual(sum(arr), 3)

        #Test binary values
        for value in arr:
            self.assertIn(value, [0, 1])

        #Test randomization
        random_sol = [random_solution(self.super_size, self.subset_size) for _ in range(30)]
        unique_sol = [set(tuple(r)) for r in random_sol]
        self.assertGreater(len(unique_sol), 1)


    def test_delta(self):

        #Test delta calculation
        delta = initialise_delta(self.dist_mat, self.sol)

        self.assertAlmostEqual(round(delta[0],3), 0.122)
        self.assertAlmostEqual(delta[1], 2.05)


    def test_sep_ind(self):

        #Test if indices can be separated correctly
        set_ind, non_ind = sep_indices(self.val)
        self.assertEqual(set_ind, [1, 2, 4])
        self.assertEqual(non_ind, [0, 3])


    def test_score(self):

        #Test if scores are returned correctly
        test = MEnzDPTabuSearch(self.sol, self.subset_size, self.subset_size, 200, 10, opt_tuple=[self.dist_mat, self.delta])
        score, sim_list = test._score(self.sol, True)

        self.assertAlmostEqual(score, -100.59)
        self.assertAlmostEqual(sim_list, [0.6, 0.5, 0.99])


    def test_neighbourhood(self):

        #Test neighbourhood creation
        test = MEnzDPTabuSearch(self.sol, self.subset_size, self.subset_size, 200, 10, opt_tuple=[self.dist_mat, self.delta])
        neighbourhood = test._create_neighbourhood()

        self.assertEqual(len(neighbourhood), 6)
        self.assertAlmostEqual(neighbourhood[0].path, [2,0])
        self.assertAlmostEqual(neighbourhood[0].new_sol.val, [1,1,0,0,1])
        self.assertAlmostEqual(neighbourhood[1].path, [4,0])
        self.assertAlmostEqual(neighbourhood[1].new_sol.val, [1,1,1,0,0])


    def test_post_swap(self):

        #Test post swap changes
        test = MEnzDPTabuSearch(self.sol, self.subset_size, self.subset_size, 200, 10, opt_tuple=[self.dist_mat, self.delta])
        new_sol = Solution([1,1,0,0,1])
        move = Move(self.sol, new_sol, [2,0])
        test._post_swap_change(move)

        self.assertAlmostEqual(round(self.delta[0],3), -0.189)
        self.assertAlmostEqual(round(self.delta[2],3), -99.028)
        self.assertAlmostEqual(round(self.delta[1],3), 0.400)
        self.assertAlmostEqual(round(self.delta[3],3), -6.062)


    def test_main(self):

        #Test the flow of the main function
        results_list, sim_list = compute_MDP_tabu(self.sim_file, self.head_file, self.subset_size)

        self.assertEqual(results_list, [['Seq1', 'Seq2', 'Seq5']])
        for i in range(len(sim_list)):
            self.assertAlmostEqual(sim_list[i], [0.2,0.1,0.5][i], places=2)