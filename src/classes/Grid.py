# Created by longtaoliu at 17.04.21
import sys
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from functools import partial
import gc
import json as js
from collections import defaultdict
import random

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

    def __init__(self, parent):
        self.myParent = parent
        self.myFrame = Frame(parent)
        self.myFrame.grid()
        self.myCanvas = None

        self.input_file = None

        self.grid = {}  # canvas grid image
        self.cells = {}  # cavas cells
        self.peds = [] # pedestrians
        self.method = "Euclidean" #util func
        
        self.reach_goal = 0 # #of peds reached goal
        self.timestep = 0# #of time step
        
        self.eu_util_map = {}
        self.icost_map = {}
        self.util_map = {}
     

        self.b_load = Button(self.myFrame, text='open', command=self.load_grid)
        self.b_load.grid(row=1, column=1,  pady=100, padx=10)
        
  

    def draw_grid(self):
        
        # self.clear_grid()
        # draw the base grid with empty cells
    
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
                self.timestep = 0
    
    def draw_cells(self):
        # draw the cells (Pedestrians, Obstacle, Target) on the grid
        for column in range(self.rows):
            for row in range(self.cols):
                if(self.cells[row,column].get_state()==1):
                    self.myCanvas.itemconfig(self.grid[row, column], fill='yellow')
                elif (self.cells[row,column].get_state()==2):
                    self.myCanvas.itemconfig(self.grid[row, column], fill='red')
                elif (self.cells[row,column].get_state()==3):
                    self.myCanvas.itemconfig(self.grid[row, column], fill='purple')
                elif (self.cells[row,column].get_state()==4):
                    self.myCanvas.itemconfig(self.grid[row, column], fill='blue')

    def load_grid(self):
        # Open json file and read the file id, setting the cells
        self.b_load.config(state=DISABLED)

        
        self.input_file = filedialog.askopenfilename(filetypes=[("Json", '*.json'), ("All files", "*.*")])

        if not self.input_file:
            return
        print('Loading file from', self.input_file)

        # json parser
        with open(self.input_file) as jf:
            data = js.load(jf)
            
            self.cols = data['cols']
            self.rows = data['rows']
            self.width = data['width']
            self.height = data['height']
            self.cell_width = self.width / self.cols
            self.cell_height = self.height / self.rows
            self.method = data['method']
            
            #draw the grid
            self.myCanvas = Canvas(self.myFrame)
            self.myCanvas.configure(width=self.cell_height * self.rows + 2, height=self.cell_width * self.cols + 2)
            self.myCanvas.grid(row=1,column=0,pady=10)

            self.b_next = Button(self.myFrame, text='next timestep', command=self.update_cells)
            self.b_next.grid(row=1, column=4,  pady=5)

            self.b_clear = Button(self.myFrame, text='clear', command=self.clear_grid)
            self.b_clear.grid(row=1, column=2,  pady=5)

            self.b_load = Button(self.myFrame, text='load', command=self.load_grid)
            self.b_load.grid(row=1, column=1,  pady=5)

            self.e_time = Entry(self.myParent) 
            self.e_time.grid(row=0, column=0,  padx=80,pady=200, sticky="ne")

            self.b_run = Button(self.myFrame, text='run task', command=self.run_task)
            self.b_run.grid(row=1, column=3,  pady=5)

            self.draw_grid()
            
            for row, col in data['pedestrians']:    
                self.cells[row, col].set_state(1)
                self.peds.append(Pedestrian(row, col))
            
            for row, col in data['target']:    
                self.cells[row, col].set_state(2)
                
            
            for row, col in data['obstacles']:    
                self.cells[row, col].set_state(3)
    
            # draw the cells
            self.draw_cells()

        self.b_load.config(state=NORMAL)



    def list_cells(self):
        # list all cells according to their type
        
        #self.p_cells = [] # list of origin pedestrian positions [NON-CHANGE]
        self.t_cells = [] # list of origin target positions [NON-CHANGE]
        self.o_cells = [] # list of origin obstacle positions [NON-CHANGE]

        for column in range(self.rows):
            for row in range(self.cols):
                
                #if self.cells[row, column].get_state() == 1:
                    #self.p_cells.append(self.cells[row, column])
                if self.cells[row, column].get_state() == 2:
                    self.t_cells.append(self.cells[row, column])
                if self.cells[row, column].get_state() == 3:
                    self.o_cells.append(self.cells[row, column])
      

    def list_duplicates(self,seq):
        tally = defaultdict(list)
        for i,item in enumerate(seq):
            tally[item].append(i)
        return ((key,locs) for key,locs in tally.items() 
                                if len(locs)>1)
    
    def indices_matches(self, a, b):
        b_set = set(b)
        return [i for i, j in enumerate(a) if j in b_set]
    
    def handle_conflict(self):
        p_to_update = []
        p_to_stay = []
        curr_pos = []
        next_pos = []
        
        #not finished peds
        gen = (p for p in self.peds if p.arrived == 0)
        for p in gen:
            self.get_euclidean_util_map()
            self.get_interaction_cost_map(p)
            
            if(self.method == "Euclidean"):
                self.util_map = self.eu_util_map
            elif(self.method == "Euclidean+Cost"):
                self.util_map = self.icost_map + self.eu_util_map
                
            p.set_next_position(self.util_map)
            next_pos.append( p.get_next_position())
            curr_pos.append( p.find_position())
        
        #print(curr_pos)
        #print(next_pos)
        #find peds with same next_postion then randomly choose one to preceed, others stay put
        for dup in self.list_duplicates(next_pos):
            winner = random.choice(dup[1]) 
            losers = list(set(dup[1])- set([winner]))
            for loser in losers: 
                p_to_stay.append(curr_pos[loser])
        
        #find peds whose next_position is occupied by peds who stay put
        for i in self.indices_matches(next_pos,p_to_stay):
            p_to_stay.append(curr_pos[i])
            
        p_to_update = list(set(curr_pos)-set(p_to_stay))
        
        return p_to_update
    
    def update_cells(self):
        # update the Pedestrians position per time step
        self.b_next.config(state=DISABLED)
        
        p_to_update = self.handle_conflict()
        
        gen = (p for p in self.peds if p.find_position() in p_to_update)
        for p in gen:            
            p.update_peds(self.t_cells[0],self.cells)
            if p.arrived == 1: self.reach_goal +=1 
                
        self.draw_cells()
        self.timestep += 1
        
        if self.reach_goal == len(self.peds):
            messagebox.showinfo(title='STOP', message='ALL GOAL')
        
        
        self.b_next.config(state=NORMAL)
    
    def run_task(self):
        
        while self.timestep < int(self.e_time.get()):
            self.update_cells()
       
        
    def get_euclidean_util_map(self):
        # compute the EuclideanDistance UtilMap
        self.list_cells()
        # print(self.t_cells[0].find_position())
        self.eu_util_map = EuclideanUtil().compute_util_map(self.rows, self.cols,
                                                                 self.t_cells[0],
                                                                 self.o_cells)

        print(self.eu_util_map)

        # plot the EUtilMap as density map
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        ax1 = ax.pcolormesh(self.eu_util_map, vmin=0, vmax=1, cmap='Greens')
        label_list = np.arange(0, self.rows - 1, 1)
        label_list = np.append(label_list, self.rows - 1)
        ax.set_xticks(label_list)
        ax.set_yticks(label_list)
        ax.title.set_text('util function')
        fig.colorbar(ax1, ax=ax)
        #fig.show()
        
    def get_interaction_cost_map(self, pedestrian):

        other_peds = []
        gen = (p for p in self.peds if p.arrived == 0)
        for p in gen:
            if p != pedestrian: other_peds.append(p)
        self.icost_map = InteractionCost().compute_cost_map(self.rows, self.cols, pedestrian, other_peds)
        
        print(self.icost_map)
        
        

  