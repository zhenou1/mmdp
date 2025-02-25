
import unittest, os, tempfile, json
import numpy as np

from MMDP.initSol import *


class TestInitSol(unittest.TestCase):

    def setUp(self):

        #Create a temporary heading json file for testing
        self.headings = ['Seq1', 'Seq2', 'Seq3', 'Seq4', 'Seq5']

        #Create temporary similarity matrices file for testing
        self.sim_mat = np.array([
            [0, 0.2, 0.4, 0.3, 0.1],
            [0.2, 0, 0.6, 0.7, 0.5],
            [0.4, 0.6, 0, 0.5, 0.9],
            [0.3, 0.7, 0.5, 0, 0.8],
            [0.1, 0.5, 0.9, 0.8, 0]
        ])

        self.temp_dir = tempfile.mkdtemp()
        self.sim_file = os.path.join(self.temp_dir, 'sim_mat.npy')
        self.head_file = os.path.join(self.temp_dir, 'headings.json')
        np.save(self.sim_file, self.sim_mat)
        with open(self.head_file, 'w') as f:
            json.dump(self.headings, f)


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

        #Check diagonal elements are 0
        for i in range(len(dist_mat)):
            self.assertEqual(dist_mat[i, i], 0)

        #Check a few values to ensure distance transformation
        self.assertAlmostEqual(dist_mat[0, 1], 0.8)
        self.assertAlmostEqual(dist_mat[1, 2], 0.4)
        self.assertAlmostEqual(dist_mat[3, 1], 0.3)


    def test_initialise_headings(self):

        #Test headings initialization
        ind_dict = initialise_headings(self.head_file)

        #Test if dictionary maps correctly
        for i in range(len(self.headings)):
            self.assertEqual(ind_dict[i], self.headings[i])


    def test_basic_func(self):

        subset_size = 3
        solution, iter_values, iterations = constructive_alg(self.sim_mat, subset_size, bilevel=False)

        #Check size of solution and iter_values
        self.assertEqual(len(solution), subset_size)
        self.assertEqual(len(iter_values), len(self.sim_mat))

        #Check iterations have been stored properly in iter_values according to solution
        for i, val in enumerate(iter_values):
            if i in solution:
                self.assertGreater(val, 0)
            else:
                self.assertEqual(val, 0)

        self.assertEqual(iterations, max(iter_values)+1)


    def test_bilevel(self):

        subset_size = 3
        sol_with_bi, _, _ = constructive_alg(self.sim_mat, subset_size, bilevel=True)
        sol_without_bi, _, _ = constructive_alg(self.sim_mat, subset_size, bilevel=False)

        #Check if bilevel is controling the output
        self.assertEqual(len(sol_with_bi), subset_size)
        self.assertEqual(len(sol_without_bi), subset_size)

        self.assertNotEqual(sol_with_bi, sol_without_bi)

    