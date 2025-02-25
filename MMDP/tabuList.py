
from collections import deque


class tabuList:

    """
    This class stores information about tabu list
    tabu_list stores the move and its current tenure
    list_len is the length of tabu list
    move_list stores the indices of elements involved in the move
    """

    def __init__(self, list_len, max_tenure):
        self.tabu_list = deque(maxlen=list_len)
        self.move_list = deque(maxlen=list_len)
        self._max_tenure = max_tenure

    def check_tabu(self, move):

        #(i,j) and (j,i) are considered the same move
        return move in self.move_list or move[::-1] in self.move_list

    def append_tabu_list(self, move):

        #Reset tenure to 0 if move already in tabu list
        #The aspiration move is first removed and then appended again to avoid being dropped due to reaching max deque length before reaching max tenure
        normalized_move = move if move[0] <= move[1] else move[::-1]
        if normalized_move in self.move_list:
            self.move_list.remove(normalized_move)
            copy = list(self.tabu_list)
            for tabu in copy:
                if tabu[0] == normalized_move:
                    self.tabu_list.remove(tabu)

        self.tabu_list.append([normalized_move, 0])
        self.move_list.append(normalized_move)

    def increment_tabu_tenure(self):
        #Increment tenure of all moves in the tabu list
        for i in range(0, len(self.tabu_list)):
            self.tabu_list[i][1] += 1

    def remove_expired_tabus(self):
        #Remove moves that have expired
        #Creating copy of the deque so not modifying while iterating over it
        copy = list(self.tabu_list)
        for tabu in copy:
            if tabu[1] > self._max_tenure:
                self.tabu_list.remove(tabu)
                self.move_list.remove(tabu[0])

    def adaptive_size(self, new_size):

        #Update lengths of tabu lists and tenure
        new_tabu_list = deque(list(self.tabu_list), maxlen=new_size)
        new_move_list = deque(list(self.move_list), maxlen=new_size)

        self.tabu_list = new_tabu_list
        self.move_list = new_move_list

        self._max_tenure = new_size
