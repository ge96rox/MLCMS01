# Created by longtaoliu at 19.04.21

import numpy as np
from classes.Solver import DijkstraSolver, FmmSolver
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


class EuclideanUtil:
    """
       EuclideanUtil()
       A class represent Euclidean Distance Util

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

    def compute_util_map(self, r, c, target, obstacle):
        # output the utils map
        utils = np.zeros((r, c))
        utils += np.inf

        for i in range(r):
            for j in range(c):
                utils[i, j] = self.compute_util(np.array([i, j]), np.array(target.find_position()))
                # print('('+str(i)+','+str(j)+')'+str(utils[i, j]))

        utils = np.round(utils / (np.max(utils) + 1), 4)

        for o in obstacle:
            utils[o.find_position()] = np.inf

        # normalize the utils to interval [0,1]
        return utils


class FmmUtil:

    def compute_util_map(self, r, c, target, obstacle):
        utils = np.full((r, c), np.inf)
        t_row, t_col = target

        f_i_map = np.full((r, c), 1)
        for o in obstacle:
            f_i_map[o.find_position()] = 0
        fmm_solver = FmmSolver(utils, f_i_map)
        return fmm_solver.solve_process(t_row, t_col)


class DijkstraUtil:

    def compute_util_map(self, r, c, target, obstacle):
        utils = np.full((r, c), np.inf)
        t_row, t_col = target

        f_i_map = np.full((r, c), 0).astype(float)
        for o in obstacle:
            f_i_map[o.find_position()] = np.inf

        dijkstra_solver = DijkstraSolver(utils, f_i_map)
        return dijkstra_solver.solve_process(t_row, t_col)


class InteractionCost:
    """
       CostFUtil()
       A class represent Cost Function that shows the interaction between pedestrians

       Parameters
       ----------

       Attributes
       ----------

    """

    def compute_cost(self, r):
        self.r_max = 1
        return np.exp(1 / (np.power(r, 2) - np.power(self.r_max, 2))) if r < self.r_max else 0

    def compute_cost_map(self, r, c, pedestrian, other_peds):
        # output the utils map
        costs = np.zeros((r, c))

        distances_to_peds = np.zeros((r, c))
        distances_to_peds += np.inf

        for i in range(r):
            for j in range(c):
                distances_to_peds[i, j] = EuclideanUtil().compute_util(np.array([i, j]),
                                                                       np.array(pedestrian.find_position()))

        for op in other_peds:
            index = op.find_position()
            costs[index] = self.compute_cost(distances_to_peds[index])

        return costs
