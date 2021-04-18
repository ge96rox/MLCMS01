# Created by longtaoliu at 17.04.21
import sys
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import gc
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import json as js


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

    """

    def __init__(self, row, col):
        self.current_row = row
        self.current_col = col

    def set_position(self, row, col):
        # update the position of cell
        self.current_row = row
        self.current_col = col

    def find_position(self):
        # return the position of cell
        return (self.current_row, self.current_col)


class Pedestrian(Cell):
    """class present each pedestrian in canvas"""

    def __init__(self, row, col):
        super().__init__(row, col)

        self.end_arrived = False

    def find_new_position(self):
        # TODO: implement algorithm
        pass

    def update_position(self):
        # TODO: update position
        pass


class Target(Cell):
    """class present each target in canvas"""

    def __init__(self, row, col):
        super().__init__(row, col)
        # self.color = "#008000"


class Obstacle(Cell):
    """class present each obstavle in canvas"""

    def __init__(self, row, col):
        super().__init__(row, col)
        # self.color = "#0000FF"


class EuclideanUtil:
    """
       EuclideanUtil(p, t)
       A class represent each cell in canvas

       Parameters
       ----------
       p : list
           The list of pedestrians coordinates


       t : list
           The list of target coordinate.


       Attributes
       ----------

    """

    def compute_util(self, p, t):
        # compute the euclidean distance
        return np.linalg.norm(p - t)

    def compute_util_map(self, r, c, t):
        # output the utils map
        utils = np.zeros((r, c))
        utils += np.inf
        # no obstacle considered here
        for i in range(r):
            for j in range(c):
                utils[i, j] = self.compute_util(np.array([i, j]), np.array(t))
                # print('('+str(i)+','+str(j)+')'+str(utils[i, j]))

        # normalize the utils to interval [0,1]
        return utils / (np.max(utils) + 1)


class GridWindow:
    """
       GridWindow(root,rows,cols,width,height)
       A class represent the interface window of grid canvas

       Parameters
       ----------
       rows : int
           The number of rows in the grid

       cols : int
           The number of columns in the grid

       width : int
           The width of tkinter canvas

       height : int
           The height of tkinter canvas



       Attributes
       ----------


    """

    def __init__(self, parent, rows, cols, width, height):
        self.myParent = parent
        self.myFrame = Frame(parent)
        self.myFrame.pack()

        self.rows = rows
        self.cols = cols
        self.cellwidth = width / cols
        self.cellheight = height / rows

        self.cells = {}
        self.utilMap = {}
        self.list_of_p = []
        self.list_of_t = []

        self.b_next = Button(self.myFrame, text='next timestep', command=self.update_cells)
        self.b_next.pack(side=TOP, padx=2, pady=2)

        self.b_clear = Button(self.myFrame, text='clear', command=self.clear_grid)
        self.b_clear.pack(side=TOP, padx=2, pady=2)

        self.b_load = Button(self.myFrame, text='open', command=self.load_grid)
        self.b_load.pack(side=TOP, padx=2, pady=2)

    def draw_grid(self):
        # draw the base grid with empty cells
        self.myCanvas = Canvas(self.myFrame)
        self.myCanvas.configure(width=self.cellheight * self.rows + 2, height=self.cellwidth * self.cols + 2)
        self.myCanvas.pack(side=RIGHT)

        for column in range(self.rows):
            for row in range(self.cols):
                x1 = column * self.cellwidth + 4
                y1 = row * self.cellheight + 4
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.cells[row, column] = self.myCanvas.create_rectangle(x1, y1, x2, y2, fill="white")

    def clear_grid(self):
        # clear the grid, set all cells to empty
        for column in range(self.rows):
            for row in range(self.cols):
                self.myCanvas.itemconfig(self.cells[row, column], fill='white')

    def load_grid(self):
        # Open json file and read the frid, setting the cells
        self.b_load.config(state=DISABLED)

        self.clear_grid()
        self.input_file = filedialog.askopenfilename(filetypes=[("Json", '*.json'), ("All files", "*.*")])

        if not self.input_file:
            return
        print('Loading file from', self.input_file)
        self.clear_grid()

        # load data into different cells
        with open(self.input_file) as jf:
            data = js.load(jf)

            i = 0
            self.pds = {}
            for ps in data['Pedestrian']:
                p = ps.split(',')
                prow = int(p[0][1])
                pcol = int(p[1][0])
                self.pds[i] = Pedestrian(prow, pcol)
                i += 1

            t = data['Target']
            trow = int(t[1])
            tcol = int(t[3])
            self.tgt = Target(trow, tcol)

            j = 0
            self.obs = {}
            for os in data['Obstacle']:
                o = os.split(',')
                orow = int(o[0][1])
                ocol = int(o[1][0])
                self.obs[j] = Obstacle(orow, ocol)
                j += 1

        # draw the cells
        self.draw_cells()

        self.b_load.config(state=NORMAL)

    def draw_cells(self):
        # draw the cells (Pedestrians, Obstacel, Target) on the grid

        self.clear_grid()
        for obj in gc.get_objects():
            if isinstance(obj, Pedestrian):
                # x1 = obj.current_col  * self.cellwidth+4
                # y1 = obj.current_row  * self.cellheight+4
                # x2 = x1 + self.cellwidth
                # y2 = y1 + self.cellheight
                # self.p = self.myCanvas.create_oval(x1,y1,x2,y2,fill = 'yellow')

                self.myCanvas.itemconfig(self.cells[obj.current_row, obj.current_col], fill='yellow')
            elif isinstance(obj, Target):

                self.myCanvas.itemconfig(self.cells[obj.current_row, obj.current_col], fill='red')
            elif isinstance(obj, Obstacle):

                self.myCanvas.itemconfig(self.cells[obj.current_row, obj.current_col], fill='purple')
        self.get_EUtilMap()

    def list_cells(self):
        # list all cells according to their type
        for obj in gc.get_objects():
            if isinstance(obj, Target):
                self.list_of_t.append(obj.find_position())
            if isinstance(obj, Pedestrian):
                self.list_of_p.append(obj.find_position())

    def update_cells(self):
        # update the Pedestrians position per time step
        self.b_next.config(state=DISABLED)

        # mark the past path as blue
        for column in range(self.rows):
            for row in range(self.cols):
                c = self.myCanvas.itemcget(self.cells[row, column], 'fill')
                if c == 'yellow':
                    self.myCanvas.itemconfig(self.cells[row, column], fill='blue')

        for obj in gc.get_objects():
            if isinstance(obj, Pedestrian):
                bestn = self.find_bestneighbor(self.utilMap, obj.current_row, obj.current_col)
                obj.set_position(bestn[0], bestn[1])
                self.myCanvas.itemconfig(self.cells[obj.current_row, obj.current_col], fill='yellow')
                # stop when reach the target
                if obj.find_position() == self.list_of_t[0]:
                    messagebox.showinfo("Finish", "Reach Goal!!!")

        self.b_next.config(state=NORMAL)

    def get_EUtilMap(self):
        # compute the EuclideanDistance UtilMap
        self.list_cells()
        self.utilMap = np.round(EuclideanUtil().compute_util_map(self.rows, self.cols, self.list_of_t), 4)
        print(self.utilMap)

        # plot the EUtilMap as density map
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        ax1 = ax.pcolormesh(self.utilMap, vmin=0, vmax=1, cmap='Greens')
        label_list = np.arange(0, self.rows - 1, 1)
        label_list = np.append(label_list, self.rows - 1)
        ax.set_xticks(label_list)
        ax.set_yticks(label_list)
        ax.title.set_text('util function')
        fig.colorbar(ax1, ax=ax)
        fig.show()

    def find_bestneighbor(self, m, r, c):
        # return the position of neighbor with smallest util around cell@(r,c) based on UtilMap m
        neighbors = []
        bestn = (r, c)
        minu = 1.1
        for i in range(-1, 2):
            newr = r + i
            if newr >= 0 and newr <= len(m) - 1:
                for j in range(-1, 2):
                    newc = c + j
                    if newc >= 0 and newc <= len(m[0]) - 1:
                        if newc == c and newr == r:
                            continue
                        print('(' + str(newr) + ',' + str(newc) + ')' + str(m[newr, newc]))
                        neighbors.append(m[newr, newc])
                        if m[newr, newc] <= minu:
                            bestn = (newr, newc)
                            minu = m[newr, newc]

        print(neighbors)
        return bestn

