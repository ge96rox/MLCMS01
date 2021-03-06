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

    UNMARKED = 0
    PEDESTRIAN = 1
    TARGET = 2
    OBSTACLE = 3
    WALKOVER = 4

    def __init__(self, row, col):
        self.current_row = row
        self.current_col = col
        self.current_state = 0
        self.arrived = 0

    def set_position(self, row, col):
        """
        set the cell position
        Parameters
        ----------
        row : int
        col : int

        Returns
        -------
        None
        """
        # update the position of cell
        self.current_row = row
        self.current_col = col

    def find_position(self):
        """
        find the current position
        Returns
        -------

        """
        # return the position of cell
        return self.current_row, self.current_col

    def set_state(self, state):
        """
        set the current state
        state :

        Returns
        -------
        None
        """
        self.current_state = state

    def get_state(self):
        """
        get the current state

        Returns
        -------
        int:
            current state
        """
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

    # class present each pedestrian in canvas
    def __init__(self, row, col, search_strategy):
        super().__init__(row, col)
        self.current_state = 1
        self.arrived = False
        self.speed = 1
        self.next_row = row
        self.next_col = col
        self.search_strategy = search_strategy

    def is_arrived(self):
        """
        set arrvied to true
        Returns
        -------
        None
        """
        self.arrived = True

    def set_next_position(self, util_map):
        """
        set the next position of cells
        Parameters
        ----------
        util_map : array, shape(rows, cols)

        Returns
        -------
        None
        """
        row = self.current_row
        column = self.current_col
        best_n = self.search_strategy(util_map, row, column)
        self.next_row = best_n[0]
        self.next_col = best_n[1]

    def get_next_position(self):
        """
        get the next position of cell

        Returns
        -------
        tuple:
         next position
        """

        return self.next_row, self.next_col

    def update_peds(self, target, cells):
        """
        update positon of pedestrians
        Parameters
        ----------
        target : Target
            target object
        cells : array, shape(rows, cols)
            array contents all cells objects

        Returns
        -------
        None
        """
        if (self.current_row, self.current_col) == target.find_position():
            # cells[self.find_position()].set_state(Cell.TARGET)
            pass
        elif self.get_next_position() == target.find_position():
            self.is_arrived()
            cells[self.find_position()].set_state(Cell.WALKOVER)
            self.set_position(self.get_next_position()[0], self.get_next_position()[1])
            # cells[self.find_position()].set_state(Cell.TARGET)
        else:
            cells[self.find_position()].set_state(Cell.WALKOVER)
            self.set_position(self.get_next_position()[0], self.get_next_position()[1])
            # cells[self.find_position()].set_state(Cell.PEDESTRIAN)

    def rewrite_peds_pos(self, target, cells):
        """
        if pedestrian not reach the target, set the cell state to PEDESTRIAN
        Parameters
        ----------
        target : Target
            target object
        cells : array, shape(rows, cols)
            array contents all cells objects

        Returns
        -------
        None
        """
        if (self.current_row, self.current_col) != target.find_position():
            cells[self.find_position()].set_state(Cell.PEDESTRIAN)

