from .tabuList import TabuList
from abc import abstractmethod
#abstractmethod are declared but don't contain any implementation - serve as placeholders for methods that must be implemented by non-abstract subclasses
from numpy import argmax
#argmax gives the index of the biggest value in the list
from copy import deepcopy
#copy creates a new object that is a copy of the top-level structure of the original object, but not the nested objects
#so changes on the nested objects within the copy will affect the original and vice versa
#deepcopy creates a new object that's not only the top-level structure but also all nested objects - entirely independent copies


class TabuSearch:

    def __init__(self, initial_solution, max_len, max_tenure, max_steps, max_score='*', max_wait='*', opt_tuple=()):
        self.curr_sol = initial_solution
        self.tabu_list = TabuList(max_len, max_tenure)
        self.max_steps = max_steps
        self.best = ''
        self.max_score = max_score
        self.opt_tuple = opt_tuple
        self.max_wait = max_wait
        self.wait = 0
        self.evaluate_curr_sol()

    @abstractmethod
    def _create_neighbourhood(self):
        """
            take self.curr_sol and produce a list of moves/paths
        """
        pass

    @abstractmethod
    def _score(self, val):
        pass

    @abstractmethod
    def _post_swap_change(self, move):
        pass


    def evaluate_curr_sol(self):
        self.curr_sol.fitness = self._score(self.curr_sol)

    def _best_score(self, neighbourhood):
        return neighbourhood[argmax([self._score(x.new_sol) for x in neighbourhood])]

    def run(self):

        for i in range(0, self.max_steps):

            neighbourhood = self._create_neighbourhood()
            neighbourhood_best = self._best_score(neighbourhood)

            self.tabu_list.remove_expired_tabus()

            while True:

                if self.tabu_list.is_move_tabu(neighbourhood_best):
                    #print(neighbourhood_best.path)
                    #print(self.tabu_list.tabu_list)
                    #print(self.tabu_list.element_list)
                    #print('TABU!')
                    if self._score(neighbourhood_best.new_sol) > self._score(self.best):
                        print('ASPIRATION!')
                        self.tabu_list.append_tabu_list(neighbourhood_best.path)
                        self.best = deepcopy(neighbourhood_best.new_sol)
                        self.curr_sol = deepcopy(neighbourhood_best.new_sol)

                        if self.max_wait !='*':
                            self.wait = 0

                        print(self.best.fitness)
                        break

                    else:
                        neighbourhood.remove(neighbourhood_best)
                        neighbourhood_best = self._best_score(neighbourhood)

                else:
                    #print('NOT TABU!')
                    self.tabu_list.append_tabu_list(neighbourhood_best.path)
                    self.curr_sol = deepcopy(neighbourhood_best.new_sol)
                    # print self.curr_sol.fitness
                    # print self.tabu_list.element_list
                    if self.best == '' or self._score(self.curr_sol) > self._score(self.best):
                        self.best = deepcopy(self.curr_sol)

                        if self.max_wait !='*':
                            self.wait = 0

                        print('NEW BEST')
                        print(self.best.fitness)

                    elif self.max_wait !='*':
                        self.wait += 1

                    break

            self.tabu_list.increment_tabu_tenure()

            # print self.curr_sol.fitness

            # call abstract post_swap_change method in case necessary for algo (like eq5 for memetic algo paper)
            self._post_swap_change(neighbourhood_best)
            if self.max_score != '*' and self._score(self.best) >= self.max_score:
                print('REACHED MAX SCORE AFTER ' + str(i) + ' ITERATIONS')
                return self.best, self._score(self.best)


            if self.max_wait !='*' and self.wait == self.max_wait:
                print(str(self.max_wait) + ' ITERATIONS WITHOUT IMPROVEMENT, STOPPING')
                return self.best, self._score(self.best)
            # print self._score(self.curr_sol)
            # print self._score(self.best)

        print('REACHED MAX STEPS')
        return self.best, self._score(self.best)