
class Move:

    """
    This class takes in the old and new solution and the move made to change from one to another
    The new solution is the copy of the old solution that can be achieved by exchanging 2 elements
    described in path.change in the form of [i,j], where i is from the old solution and j from new solution
    """

    def __init__(self, old_sol, new_sol, path):
        self.old_sol = old_sol
        self.new_sol = new_sol
        self.path = path

    def __str__(self):
        return str(self.path)