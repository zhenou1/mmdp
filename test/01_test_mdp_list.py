
import unittest
from collections import deque

from MDP.tabuList import TabuList
from MDP.Move import Move


class TestList(unittest.TestCase):

    def setUp(self):

        self.list = TabuList(3,1)

        self.assertEqual(len(self.list.tabu_list), 0)
        self.assertEqual(len(self.list.element_list), 0)
        self.assertEqual(self.list._max_tenure, 1)


    def test_tabu_move(self):
        
        self.list.element_list = deque([1,2,4], maxlen=3)
        move_1 = Move([2,3,4], [2,3,1], [1,4])
        move_2 = Move([1,2,4], [2,3,4], [2,3])
        move_3 = Move([2,3,4], [2,4,5], [3,5])

        self.assertTrue(self.list.is_move_tabu(move_1))
        self.assertTrue(self.list.is_move_tabu(move_2))
        self.assertFalse(self.list.is_move_tabu(move_3))


    def test_append(self):

        self.list.tabu_list = deque([[2,0]], maxlen=3)
        self.list.element_list = deque([2], maxlen=3)
        
        #Check if move is appended
        self.list.append_tabu_list([1,4])
        self.assertEqual(len(self.list.tabu_list), 3)
        self.assertEqual(len(self.list.element_list), 3)
        self.assertEqual(self.list.tabu_list, deque([[2,0], [1,0], [4,0]], maxlen=3))
        self.assertEqual(self.list.element_list, deque([2,1,4], maxlen=3))

        #Check if list is kept at maxlen
        self.list.append_tabu_list([1,3])
        self.assertEqual(len(self.list.tabu_list), 3)
        self.assertEqual(len(self.list.element_list), 3)
        self.assertEqual(self.list.tabu_list, deque([[1,0], [4,0], [3,0]], maxlen=3))
        self.assertEqual(self.list.element_list, deque([1,4,3], maxlen=3))

        #Check if tabu can be appended again
        self.list.append_tabu_list([3,4])
        self.assertEqual(len(self.list.tabu_list), 3)
        self.assertEqual(len(self.list.element_list), 3)
        self.assertEqual(self.list.tabu_list, deque([[1,0], [4,0], [3,0]], maxlen=3))
        self.assertEqual(self.list.element_list, deque([1,4,3], maxlen=3))

    
    def test_increment(self):

        self.list.tabu_list = deque([[2,1], [1,1], [4,0]], maxlen=3)
        self.list.element_list = deque([2,1,4], maxlen=3)
        self.list.increment_tabu_tenure()

        self.assertEqual(len(self.list.tabu_list), 3)
        self.assertEqual(len(self.list.element_list), 3)
        self.assertEqual(self.list.tabu_list, deque([[2,2], [1,2], [4,1]], maxlen=3))
        self.assertEqual(self.list.element_list, deque([2,1,4], maxlen=3))


    def test_remove(self):

        self.list.tabu_list = deque([[2,2], [1,1], [4,0]], maxlen=3)
        self.list.element_list = deque([2,1,4], maxlen=3)
        self.list.remove_expired_tabus()

        self.assertEqual(len(self.list.tabu_list), 2)
        self.assertEqual(len(self.list.element_list), 2)
        self.assertEqual(self.list.tabu_list, deque([[1,1], [4,0]], maxlen=3))
        self.assertEqual(self.list.element_list, deque([1,4], maxlen=3))
