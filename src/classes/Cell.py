# Created by longtaoliu at 19.04.21
#from classes.Grid import GridWindow
import numpy as np

class Cell:
    """
       Cell(row, col)
       A class represent each cell in canvas

       Parameters
       ----------
       row : int
           The row position coordinate of the cell


       col : int
           The column position coordinate of the cell


       Attributes
       ----------
       current_row : int
           The row position coordinate of the cell

       current_col : int
           The column position coordinate of the cell

       current_state : int
                0: empty
                1: occupied
                2: target
                3: obstacle
                4: walked over

    """

    def __init__(self, row, col):
        self.current_row = row
        self.current_col = col
        self.current_state = 0
        self.arrived = 0

    def set_position(self, row, col):
        # update the position of cell
        self.current_row = row
        self.current_col = col

    def find_position(self):
        # return the position of cell
        return self.current_row, self.current_col

    def set_state(self, state):
        self.current_state = state

    def get_state(self):
        return self.current_state

class Pedestrian(Cell):       
    """
       Cell(row, col)
       A class represent each Pedestrian in canvas

       Parameters
       ----------
       row : int
           The row position coordinate of the cell


       col : int
           The column position coordinate of the cell


       Attributes
       ----------
       current_row : int
           The row position coordinate of the cell

       current_col : int
           The column position coordinate of the cell

       current_state : int
                0: empty
                1: occupied
                2: target
                3: obstacle
                4: walked over

        next_row : int
           The future row position coordinate of the cell

        next_col : int
           The future column position coordinate of the cell
           
        arrived : int
                0: no
                1: yes

        speed : int
            the number of cells moved in one time step


    """
    
    #class present each pedestrian in canvas
    def __init__(self, row, col): 
        super().__init__(row, col)
        self.current_state = 1
        self.arrived = 0 
        self.speed = 1
        self.next_row = row
        self.next_col = col
     

    def is_arrived(self):
        self.arrived = 1
        
    def set_next_position(self,util_map):
        
        row = self.current_row
        column = self.current_col
        best_n = self.find_best_neighbor(util_map, row, column) 
        self.next_row = best_n[0]
        self.next_col = best_n[1]

    def get_next_position(self):
        # return the position of cell
        return self.next_row, self.next_col
    
    def update_peds(self,target,cells):
        
        if (self.get_next_position()==target.find_position()):
            self.is_arrived()
            self.set_position(self.get_next_position()[0],self.get_next_position()[1])
            cells[self.find_position()].set_state(2)
            #messagebox.showinfo(title='STOP', message='GOAL')
        else:
            cells[self.find_position()].set_state(4)
            self.set_position(self.get_next_position()[0],self.get_next_position()[1])
            cells[self.find_position()].set_state(1)
          
    
    @staticmethod
    def find_best_neighbor(m, r, c):
        # return the position of neighbor with smallest util around cell@(r,c) based on UtilMap m
        neighbors = []
        best_n = (r, c)
        min_u = np.inf
        for i in range(-1, 2):
            new_r = r + i
            if 0 <= new_r <= len(m) - 1:
                for j in range(-1, 2):
                    new_c = c + j
                    if 0 <= new_c <= len(m[0]) - 1:
                        if new_c == c and new_r == r:
                            continue
                        #print('(' + str(new_r) + ',' + str(new_c) + ')' + str(m[new_r, new_c]))
                        neighbors.append(m[new_r, new_c])
                        if m[new_r, new_c] <= min_u:
                            best_n = (new_r, new_c)
                            min_u = m[new_r, new_c]

        # print(neighbors)
        # print(best_n)
        return best_n

"""

class Target(Cell):
    #class present each target in canvas
    def __init__(self, row, col):
        super().__init__(row, col)
        self.set_state(2)

class Obstacle(Cell):
    #class present each obstavle in canvas
    def __init__(self, row, col):
        super().__init__(row, col)
        self.set_state(3)
        
"""
