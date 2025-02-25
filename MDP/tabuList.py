
from collections import deque

class TabuList:

    """
    This class stores information about tabu list
    list_len is the length of tabu list
    element_list stores the indices of the elements
    """

    def __init__(self, list_len, max_tenure):

        self.tabu_list = deque(maxlen=list_len)
        self.element_list = deque(maxlen=list_len)

        self._max_tenure = max_tenure


    def is_move_tabu(self, move):

        if len(self.element_list) == 0:
            return False
        
        return True in [x in self.element_list for x in move.path]


    def append_tabu_list(self, path):

        if path in self.element_list:
            #If the elements to be added is already in the solution list, change the current tenure of the element back down to 0 instead of adding duplicates
            copy = list(self.tabu_list)

            for i in range(0, len(copy)):
                if copy[i][0] == path:
                    self.tabu_list[i][1] = 0
                    return

        copy = list(self.element_list)
        bool0 = True
        bool1 = True

        #Check if any elements are already in the solution list, if yes, change their current tenure to 0 and append the ones that are not in
        for i in range(0, len(copy)):
            if path[0] == copy[i]:
                self.tabu_list[i] = [path[0], 0]
                bool0 = False

            elif path[1] == copy[i]:
                self.tabu_list[i] = [path[1], 0]
                bool1 = False

        if bool0:
            self.tabu_list.append([path[0], 0])
            self.element_list.append(path[0])

        if bool1:
            self.tabu_list.append([path[1], 0])
            self.element_list.append(path[1])


    def increment_tabu_tenure(self):

        for i in range(0, len(self.tabu_list)):
            self.tabu_list[i][1] += 1


    def remove_expired_tabus(self):
        
        copy = list(self.tabu_list)
        for tabu in copy:
            if tabu[1] > self._max_tenure:
                self.tabu_list.remove(tabu)
                self.element_list.remove(tabu[0])
