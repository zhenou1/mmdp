
import unittest, tempfile, os, json
import numpy as np

from MMDP.Expand import *
from MMDP.initSol import initialise_headings


class TestExpand(unittest.TestCase):


    def setUp(self):

        #Create a temporary files for testing
        self.id = ['Seq1', 'Seq3']
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
        self.id_file = os.path.join(self.temp_dir, 'subset.txt')
        self.head_file = os.path.join(self.temp_dir, 'headings.json')
        with open(self.id_file, 'w') as f:
            for i in self.id:
                f.write(i+'\n')

        with open(self.head_file, 'w') as f:
            json.dump(self.headings, f)

        self.ind_dict = initialise_headings(self.head_file)


    def tearDown(self):

        #Clean up temporary files
        os.remove(self.id_file)
        os.remove(self.head_file)
        os.rmdir(self.temp_dir)


    def test_load_subset(self):

        #Test loading of existing subsets
        curr_subset = load_curr_subset(self.id_file, self.ind_dict)
        self.assertEqual(curr_subset, [0, 2])

    
    def test_expand_init(self):

        #Test initialise expanded initial solution
        subset_size = 3
        curr_subset = [0,2]
        expanded_init, iter_values, iterations = expand_init(self.sim_mat, curr_subset, subset_size, bilevel=True)
    
        self.assertEqual(len(expanded_init), subset_size)
        self.assertEqual(len(iter_values), len(self.sim_mat))

        #Check iterations have been stored properly in iter_values according to solution
        for i, val in enumerate(iter_values):
            if i in expanded_init:
                self.assertGreater(val, 0)
            elif i in curr_subset:
                self.assertEqual(val, float('inf'))
            else:
                self.assertEqual(val, 0)

        max_iter = [x for x in sorted(set(iter_values), reverse=True) if x != float('inf')][0]
        self.assertEqual(iterations, max_iter+1)