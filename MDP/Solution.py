

class Solution:

    """
    This class defines the solution class, where val is 0 or 1 of an element in the superset, depending
    whether it's in the solution or not, and fitness is the score of the solution
    """

    def __init__(self, val, fitness=0):
        self.val = val
        self.fitness = fitness
