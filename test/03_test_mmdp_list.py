
import unittest
from collections import deque

from MMDP.tabuList import tabuList


class TestTabuList(unittest.TestCase):

    def setUp(self):
        
        self.list = tabuList(2,1)
        
        self.assertEqual(len(self.list.move_list), 0)
        self.assertEqual(len(self.list.tabu_list), 0)
        self.assertEqual(self.list._max_tenure, 1)


    def test_check_tabu(self):

        #Check if tabu can be correctly found in the list
        self.list.move_list = deque([(1,2), (1,4)], maxlen=2)
        self.assertTrue(self.list.check_tabu((4,1)))
        self.assertFalse(self.list.check_tabu((1,3)))


    def test_append_tabu(self):

        #Check if tabu move is appended
        self.list.append_tabu_list((1,2))
        self.assertEqual(len(self.list.tabu_list), 1)
        self.assertEqual(len(self.list.move_list), 1)
        self.assertEqual(self.list.tabu_list, deque([[(1,2), 0]], maxlen=2))
        self.assertEqual(self.list.move_list, deque([(1,2)], maxlen=2))

        self.list.append_tabu_list((3,1))
        self.assertEqual(len(self.list.tabu_list), 2)
        self.assertEqual(len(self.list.move_list), 2)
        self.assertEqual(self.list.tabu_list, deque([[(1,2), 0], [(1,3), 0]], maxlen=2))
        self.assertEqual(self.list.move_list, deque([(1,2), (1,3)], maxlen=2))

        #Check if tabu is renewed if the same move is appended
        self.list.append_tabu_list((2,1))
        self.assertEqual(len(self.list.tabu_list), 2)
        self.assertEqual(len(self.list.move_list), 2)
        self.assertEqual(self.list.tabu_list, deque([[(1,3), 0], [(1,2), 0]], maxlen=2))
        self.assertEqual(self.list.move_list, deque([(1,3), (1,2)], maxlen=2))

        #Check if list is kept at maxlen
        self.list.append_tabu_list((1,4))
        self.assertEqual(len(self.list.tabu_list), 2)
        self.assertEqual(len(self.list.move_list), 2)
        self.assertEqual(self.list.tabu_list, deque([[(1,2), 0], [(1,4), 0]], maxlen=2))
        self.assertEqual(self.list.move_list, deque([(1,2), (1,4)], maxlen=2))


    def test_increment_tabu(self):

        #Check if tabu can be incremented
        self.list.tabu_list = deque([[(1,2), 0]], maxlen=2)
        self.list.increment_tabu_tenure()

        self.assertEqual(self.list.tabu_list, deque([[(1,2), 1]], maxlen=2))


    def test_remove_expired(self):

        #Check if can remove expired tabus
        self.list.tabu_list = deque([[(1,2), 2], [(1,4), 1]], maxlen=2)
        self.list.move_list = deque([(1,2), (1,4)], maxlen=2)
        self.list.remove_expired_tabus()

        self.assertEqual(self.list.tabu_list, deque([[(1,4), 1]], maxlen=2))
        self.assertEqual(self.list.move_list, deque([(1,4)], maxlen=2))

    
    def test_adaptive(self):

        #Check if tabu list and tenure are resized
        self.list.tabu_list = deque([[(1,2), 1], [(1,4), 1]], maxlen=2)
        self.list.move_list = deque([(1,2), (1,4)], maxlen=2)
        self.list.adaptive_size(3)

        self.assertEqual(self.list.tabu_list, deque([[(1,2), 1], [(1,4), 1]], maxlen=3))
        self.assertEqual(self.list.move_list, deque([(1,2), (1,4)], maxlen=3))
        self.assertEqual(self.list._max_tenure, 3)