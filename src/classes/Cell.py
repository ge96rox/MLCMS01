# Created by longtaoliu at 19.04.21

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
                0: unmarked
                1: pedestrian
                2: target
                3: obstacle
                4: walked over

        arrived : int
                0: no
                1: yes

        speed : int
            the number of cells moved in one time step


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

    def is_arrived(self):
        self.arrived = 1


"""
class Pedestrian(Cell):
    #class present each pedestrian in canvas
    def __init__(self, row, col):
        super().__init__(row, col)
        self.set_state(1)


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