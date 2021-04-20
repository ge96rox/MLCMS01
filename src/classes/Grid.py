# Created by longtaoliu at 17.04.21

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

import json as js

import random

from classes.Cell import *
from classes.Util import *

import matplotlib
import matplotlib.pyplot as plt

from util.helper import list_duplicates, indices_matches

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

    def __init__(self, parent):
        self.myParent = parent
        self.myFrame = Frame(parent)
        self.myFrame.pack()
        self.myCanvas = None
        self.mark_path = True
        self.input_file = None

        self.rows = None
        self.cols = None
        self.cell_width = None
        self.cell_height = None
        self.cell_size = None
        self.pre_run = False
        self.step = 0
        self.round_finish = False
        self.animation = False
        self.first_round = True
        self.time = 400

        self.grid = {}  # canvas grid image
        self.cells = {}  # cavas cells

        self.peds = []  # pedestrians
        self.reach_goal = 0  # #of peds reached goal

        self.utilMap = {}
        self.o_cells = []
        self.t_cells = []

        self.b_next = Button(self.myFrame, text='next', command=self.update_cells)
        self.b_next.pack(side=TOP, padx=2, pady=2)
        self.b_next.config(state=DISABLED)

        self.b_clear = Button(self.myFrame, text='clear', command=self.clear_grid)
        self.b_clear.pack(side=TOP, padx=2, pady=2)

        self.b_load = Button(self.myFrame, text='open', command=self.init_setup)
        self.b_load.pack(side=TOP, padx=2, pady=2)

        self.b_run = Button(self.myFrame, text='run', command=self.animate)
        self.b_run.pack(side=TOP, padx=2, pady=2)
        self.b_run.config(state=DISABLED)

        self.label_text = StringVar()
        self.label_text.set(' step')
        self.label = Label(self.myFrame, textvariable=self.label_text)
        self.label.pack(side=TOP, padx=2, pady=2)

    def draw_grid(self):

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
                self.peds = []
                self.reach_goal = 0
        self.b_load.config(state=NORMAL)
        self.b_run.config(state=DISABLED)
        self.step = 0
        self.round_finish = False
        self.label_text.set(' step')

    def init_setup(self):

        # Open json file and read the file id, setting the cells
        self.b_load.config(state=DISABLED)

        # json parser
        data = self.open_read_data()

        if self.pre_run:
            self.clear_grid()
            self.pre_run = False
        else:
            self.myCanvas = Canvas(self.myFrame)
            self.myCanvas.configure(width=self.cell_height * self.rows + 4, height=self.cell_width * self.cols + 4)
            self.myCanvas.pack(side=RIGHT)

        # draw the base grid with empty cells
        if self.step == 0:
            self.first_round = True
            self.draw_grid()

        self.load_grid(data)

        # draw the cells
        self.draw_cells()
        self.b_next.config(state=NORMAL)

    def open_read_data(self):

        self.input_file = filedialog.askopenfilename(filetypes=[("Json", '*.json'), ("All files", "*.*")])
        if not self.input_file:
            return
        print('Loading file from', self.input_file)
        with open(self.input_file) as jf:
            data = js.load(jf)
        self.cell_size = data['cell_size']
        self.rows = data['rows']
        self.cols = data['cols']
        self.cell_height = self.cell_size
        self.cell_width = self.cell_size
        return data

    def load_grid(self, data):

        for ps in data['Pedestrian']:
            p = ps.split(',')
            p_row = int(p[0][1])
            p_col = int(p[1][0])
            self.cells[p_row, p_col].set_state(Cell.PEDESTRIAN)
            self.peds.append(Pedestrian(p_row, p_col))

        t = data['Target']
        t_row = int(t[1])
        t_col = int(t[3])
        self.cells[t_row, t_col].set_state(Cell.TARGET)

        for os in data['Obstacle']:
            o = os.split(',')
            o_row = int(o[0][1])
            o_col = int(o[1][0])
            self.cells[o_row, o_col].set_state(Cell.OBSTACLE)

    def draw_cells(self):

        # draw the cells (Pedestrians, Obstacle, Target) on the grid
        for column in range(self.rows):
            for row in range(self.cols):
                if self.cells[row, column].get_state() == Cell.PEDESTRIAN:
                    self.myCanvas.itemconfig(self.grid[row, column], fill='yellow')
                elif self.cells[row, column].get_state() == Cell.TARGET:
                    self.myCanvas.itemconfig(self.grid[row, column], fill='red')
                elif self.cells[row, column].get_state() == Cell.OBSTACLE:
                    self.myCanvas.itemconfig(self.grid[row, column], fill='purple')
                elif self.cells[row, column].get_state() == Cell.WALKOVER:
                    self.myCanvas.itemconfig(self.grid[row, column], fill='white')
        self.b_run.config(state=NORMAL)
        if self.first_round:
            self.first_round = False
        else:
            self.step += 1
        self.label_text.set('{} step'.format(self.step))

    def list_cells(self):
        # list all cells according to their type

        # self.p_cells = [] # list of origin pedestrian positions [NON-CHANGE]
        self.o_cells = []  # list of origin obstacle positions [NON-CHANGE]
        self.t_cells = []  # list of origin target positions [NON-CHANGE]

        for column in range(self.rows):
            for row in range(self.cols):

                # if self.cells[row, column].get_state() == 1:
                # self.p_cells.append(self.cells[row, column])
                if self.cells[row, column].get_state() == Cell.TARGET:
                    self.t_cells.append(self.cells[row, column])
                if self.cells[row, column].get_state() == Cell.OBSTACLE:
                    self.o_cells.append(self.cells[row, column])

    def handle_conflict(self):
        p_to_update = []
        p_to_stay = []
        curr_pos = []
        next_pos = []

        # not finished peds
        gen = (p for p in self.peds if p.arrived == 0)
        for p in gen:
            self.get_euclidean_util_map()
            p.set_next_position(self.utilMap)
            next_pos.append(p.get_next_position())
            curr_pos.append(p.find_position())

        # find peds with same next_postion then randomly choose one to preceed, others stay put
        for dup in list_duplicates(next_pos):
            winner = random.choice(dup[1])
            losers = list(set(dup[1]) - set([winner]))
            for loser in losers:
                p_to_stay.append(curr_pos[loser])

        # find peds whose next_position is occupied by peds who stay put
        for i in indices_matches(next_pos, p_to_stay):
            p_to_stay.append(curr_pos[i])

        p_to_update = list(set(curr_pos) - set(p_to_stay))

        return p_to_update

    def update_cells(self):
        # update the Pedestrians position per time step

        self.b_next.config(state=DISABLED)

        p_to_update = self.handle_conflict()
        print(p_to_update)

        gen = (p for p in self.peds if p.find_position() in p_to_update)
        for p in gen:
            p.update_peds(self.t_cells[0], self.cells)
            if p.arrived == 1:
                self.reach_goal += 1
        self.draw_cells()
        self.check_game_end()
        self.b_next.config(state=NORMAL)

    def check_game_end(self):
        if self.reach_goal == len(self.peds):
            messagebox.showinfo(title='STOP', message='ALL GOAL')
            self.pre_run = True
            self.animation = False
            self.round_finish = True
        if not self.round_finish and self.animation:
            self.myFrame.after(self.time, self.update_cells)

    def animate(self):
        self.animation = True
        self.update_cells()

    def get_euclidean_util_map(self):
        # compute the EuclideanDistance UtilMap
        self.list_cells()
        # print(self.t_cells[0].find_position())
        self.utilMap = EuclideanUtil().compute_util_map(self.rows, self.cols,
                                                        self.t_cells[0].find_position(),
                                                        self.o_cells)

        # plot the EUtilMap as density map
        # fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        # ax1 = ax.pcolormesh(self.utilMap, vmin=0, vmax=1, cmap='Greens')
        # label_list = np.arange(0, self.rows - 1, 1)
        # label_list = np.append(label_list, self.rows - 1)
        # ax.set_xticks(label_list)
        # ax.set_yticks(label_list)
        # ax.title.set_text('util function')
        # fig.colorbar(ax1, ax=ax)
        # fig.show()
