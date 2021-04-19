# Created by longtaoliu at 17.04.21
import sys
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import gc
import json as js

from classes.Cell import *
from classes.Util import *

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


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
        self.myCanvas = None

        self.input_file = None

        self.rows = rows
        self.cols = cols
        self.cell_width = width / cols
        self.cell_height = height / rows

        self.grid = {}  # canvas grid image
        self.cells = {}  # cavas cells
        self.utilMap = {}
        self.p_cells = []
        self.t_cells = []

        self.b_next = Button(self.myFrame, text='next timestep', command=self.update_cells)
        self.b_next.pack(side=TOP, padx=2, pady=2)

        self.b_clear = Button(self.myFrame, text='clear', command=self.clear_grid)
        self.b_clear.pack(side=TOP, padx=2, pady=2)

        self.b_load = Button(self.myFrame, text='open', command=self.load_grid)
        self.b_load.pack(side=TOP, padx=2, pady=2)

    def draw_grid(self):
        # draw the base grid with empty cells
        self.myCanvas = Canvas(self.myFrame)
        self.myCanvas.configure(width=self.cell_height * self.rows + 2, height=self.cell_width * self.cols + 2)
        self.myCanvas.pack(side=RIGHT)

        for column in range(self.rows):
            for row in range(self.cols):
                x1 = column * self.cell_width + 4
                y1 = row * self.cell_height + 4
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height
                self.grid[row, column] = self.myCanvas.create_rectangle(x1, y1, x2, y2, fill="white")
                self.cells[row, column] = Cell(row, column)

    def clear_grid(self):
        # clear the grid, set all cells to empty
        for column in range(self.rows):
            for row in range(self.cols):
                self.myCanvas.itemconfig(self.grid[row, column], fill='white')
                self.cells[row, column].set_state(0)

    def load_grid(self):
        # Open json file and read the file id, setting the cells
        self.b_load.config(state=DISABLED)

        self.clear_grid()
        self.input_file = filedialog.askopenfilename(filetypes=[("Json", '*.json'), ("All files", "*.*")])

        if not self.input_file:
            return
        print('Loading file from', self.input_file)

        # json parser
        with open(self.input_file) as jf:
            data = js.load(jf)

            for ps in data['Pedestrian']:
                p = ps.split(',')
                p_row = int(p[0][1])
                p_col = int(p[1][0])
                self.cells[p_row, p_col].set_state(1)

            t = data['Target']
            t_row = int(t[1])
            t_col = int(t[3])
            self.cells[t_row, t_col].set_state(2)

            for os in data['Obstacle']:
                o = os.split(',')
                o_row = int(o[0][1])
                o_col = int(o[1][0])
                self.cells[o_row, o_col].set_state(3)

        # draw the cells
        self.draw_cells()

        self.b_load.config(state=NORMAL)

    def draw_cells(self):
        # draw the cells (Pedestrians, Obstacle, Target) on the grid

        # print(self.cells)
        for obj in gc.get_objects():
            if isinstance(obj, Cell):
                if obj.get_state() == 1:
                    self.myCanvas.itemconfig(self.grid[obj.current_row, obj.current_col], fill='yellow')
                elif obj.get_state() == 2:
                    self.myCanvas.itemconfig(self.grid[obj.current_row, obj.current_col], fill='red')
                elif obj.get_state() == 3:
                    self.myCanvas.itemconfig(self.grid[obj.current_row, obj.current_col], fill='purple')

        self.get_euclidean_util_map()

    def list_cells(self):
        # list all cells according to their type

        for column in range(self.rows):
            for row in range(self.cols):
                # print(self.cells[row, column].get_state())
                if self.cells[row, column].get_state() == 1:
                    self.p_cells.append(self.cells[row, column])
                if self.cells[row, column].get_state() == 2:
                    self.t_cells.append(self.cells[row, column])

    def update_cells(self):
        # update the Pedestrians position per time step
        self.b_next.config(state=DISABLED)

        # for column in range(self.rows):
        #     for row in range(self.cols):
        #         if(self.cells[row,column].get_state()==1):

        for obj in gc.get_objects():
            if isinstance(obj, Cell):
                if obj.get_state() == 1:
                    row = obj.current_row
                    column = obj.current_col

                    # find the nearest neighbor
                    best_n = GridWindow.find_best_neighbor(self.utilMap, row, column)
                    # the neighbor is empty
                    if self.cells[best_n[0], best_n[1]].get_state() == 0:
                        # move pedestrian to the neighbor
                        self.myCanvas.itemconfig(self.grid[best_n[0], best_n[1]], fill='yellow')
                        self.cells[best_n[0], best_n[1]].set_state(1)
                        # mark the path
                        self.myCanvas.itemconfig(self.grid[row, column], fill='blue')
                        self.cells[row, column].set_state(4)
                    # the neighbor is target
                    elif self.cells[best_n[0], best_n[1]].get_state() == 2:
                        # 不动了，停留原地？
                        self.cells[row, column].is_arrived()
                        messagebox.showinfo("STOP", "Reach Goal!!!")
                    # the neighbor is obstacle
                    elif self.cells[best_n[0], best_n[1]].get_state() == 3:
                        messagebox.showinfo("STOP", "Can Not Move!!!")
                    # the neighbor is another pedestrian
                    elif self.cells[best_n[0], best_n[1]].get_state() == 1:
                        # 不动了，停留原地？conflict
                        pass

        self.b_next.config(state=NORMAL)

    def get_euclidean_util_map(self):
        # compute the EuclideanDistance UtilMap
        self.list_cells()
        # print(self.t_cells[0].find_position())
        self.utilMap = np.round(EuclideanUtil().compute_util_map(self.rows, self.cols,
                                                                 self.t_cells[0].find_position()), 4)

        # print(self.utilMap)

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

    @staticmethod
    def find_best_neighbor(m, r, c):
        # return the position of neighbor with smallest util around cell@(r,c) based on UtilMap m
        neighbors = []
        best_n = (r, c)
        min_u = 1.1
        for i in range(-1, 2):
            new_r = r + i
            if 0 <= new_r <= len(m) - 1:
                for j in range(-1, 2):
                    new_c = c + j
                    if 0 <= new_c <= len(m[0]) - 1:
                        if new_c == c and new_r == r:
                            continue
                        print('(' + str(new_r) + ',' + str(new_c) + ')' + str(m[new_r, new_c]))
                        neighbors.append(m[new_r, new_c])
                        if m[new_r, new_c] <= min_u:
                            best_n = (new_r, new_c)
                            min_u = m[new_r, new_c]

        # print(neighbors)
        print(best_n)
        return best_n
