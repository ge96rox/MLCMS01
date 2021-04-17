# Created by longtaoliu at 17.04.21
from tkinter import *
from tkinter import messagebox
import gc
import numpy as np
from abc import ABC, abstractmethod
from itertools import product, starmap, islice


class Cell:
    """class present each cell in canvas"""

    def __init__(self, row, col):
        self.current_row = row
        self.current_col = col

    def set_position(self, row, col):
        self.current_row = row
        self.current_col = col

    def find_position(self):
        return (self.current_row, self.current_col)


class Pedestrian(Cell):
    def __init__(self, row, col):
        super().__init__(row, col)
        # self.color = "#FF0000"

        self.end_arrived = False

    def find_new_position(self):
        # TODO: implement algorithm
        pass

    def update_position(self):
        # TODO: update position
        pass
        # self.set_position(self.current_row, self.current_col+1)


class Target(Cell):
    def __init__(self, row, col):
        super().__init__(row, col)
        # self.color = "#008000"


class Obstacle(Cell):
    def __init__(self, row, col):
        super().__init__(row, col)
        # self.color = "#0000FF"


class EuclideanUtil:
    """
        A class to compute the utils with "Euclidean Distance".
    """

    def init_value(self):
        # the initial value of the euclidean distance should be inf
        return np.inf

    def compute_util(self, p, t):
        # compute the euclidean distance
        return np.linalg.norm(p - t)

    def compute_util_map(self, r, c, t):

        utils = np.zeros((r, c))
        utils += np.inf
        # no obstacle considered here
        for i in range(r):
            for j in range(c):
                utils[i, j] = self.compute_util(np.array([i, j]), np.array(t))

        # normalize the utils to interval [0,1]
        return utils / (np.max(utils) + 1)


class gridWindow:
    def __init__(self, parent, rows, cols, width, height):
        self.myParent = parent

        self.myContainer1 = Frame(parent)
        self.myContainer1.pack()

        self.rows = rows
        self.cols = cols
        self.cellwidth = width / cols
        self.cellheight = height / rows
        self.rect = {}
        self.utilMap = {}
        self.list_of_p = []
        self.list_of_t = []
        self.get_EUtilMap()

        b_next = Button(self.myContainer1, text='next timestep', command=self.update_cells)
        b_next.pack(side=LEFT, padx=5, pady=5)

        # b_clear = Button(frame, text='clear', command=self.clear_grid)
        # b_clear.pack(side=LEFT, padx=5, pady=5)

    def draw_grid(self):
        self.myCanvas = Canvas(self.myContainer1)
        self.myCanvas.configure(width=self.cellheight * self.rows + 2,
                                height=self.cellwidth * self.cols + 2)
        self.myCanvas.pack(side=RIGHT)

        for column in range(self.rows):
            for row in range(self.cols):
                x1 = column * self.cellwidth + 4
                y1 = row * self.cellheight + 4
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.rect[row, column] = self.myCanvas.create_rectangle(x1, y1, x2, y2, fill="white")

    # def clear_grid(self):

    # myCanvas.delete()

    def draw_cells(self):
        self.myCanvas.itemconfig(self.rect, fill='white')
        for obj in gc.get_objects():
            if isinstance(obj, Pedestrian):
                # x1 = obj.current_col  * self.cellwidth+4
                # y1 = obj.current_row  * self.cellheight+4
                # x2 = x1 + self.cellwidth
                # y2 = y1 + self.cellheight

                # self.p = self.myCanvas.create_oval(x1,y1,x2,y2,fill = 'yellow')
                self.myCanvas.itemconfig(self.rect[obj.current_col, obj.current_row], fill='yellow')

            elif isinstance(obj, Target):
                self.myCanvas.itemconfig(self.rect[obj.current_col, obj.current_row], fill='red')

            elif isinstance(obj, Obstacle):
                self.myCanvas.itemconfig(self.rect[obj.current_col, obj.current_row], fill='purple')

    def list_cells(self):

        for obj in gc.get_objects():
            if isinstance(obj, Target):
                self.list_of_t.append(obj.find_position())
            if isinstance(obj, Pedestrian):
                self.list_of_p.append(obj.find_position())

    def update_cells(self):

        for column in range(self.rows):
            for row in range(self.cols):
                c = self.myCanvas.itemcget(self.rect[row, column], 'fill')
                if c == 'yellow':
                    self.myCanvas.itemconfig(self.rect[row, column], fill='blue')

        for obj in gc.get_objects():
            if isinstance(obj, Pedestrian):
                if obj.find_position() == self.list_of_t[0]:
                    messagebox.showinfo("Finish", "Reach Goal")
                    obj.end_arrived = TRUE
                else:
                    n = self.find_neighbors(self.utilMap, obj.current_col, obj.current_row)
                    newr = np.where(self.utilMap == min(n))[0][0]
                    newc = np.where(self.utilMap == min(n))[1][0]
                    obj.set_position(newr, newc)
                    self.myCanvas.itemconfig(self.rect[obj.current_col, obj.current_row], fill='yellow')

    def get_EUtilMap(self):
        self.list_cells()
        self.utilMap = np.round(EuclideanUtil().compute_util_map(self.rows, self.cols, self.list_of_t), 3)

        print(self.utilMap)

    def find_neighbors(self, umap, x, y):
        xi = (0, -1, 1) if 0 < x < len(umap) - 1 else ((0, -1) if x > 0 else (0, 1))
        yi = (0, -1, 1) if 0 < y < len(umap[0]) - 1 else ((0, -1) if y > 0 else (0, 1))

        return list(islice(starmap((lambda a, b: umap[x + a][y + b]), product(xi, yi)), 1, None))
