# Created by longtaoliu at 19.04.21

import numpy as np
import classes.Fmm as fmm
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

        return fmm.fmm_u_map_init(utils, f_i_map, t_row, t_col)


class DijkstraUtil:
    def explore_node(self, r, c, queue, visited, o_list, utils):
        cost = np.full((r, c), np.inf)
        node = queue[0]

        for i in range(max(0, node[0] - 1), min(r - 1, node[0] + 1) + 1):
            for j in range(max(0, node[1] - 1), min(c - 1, node[1] + 1) + 1):
                if (i == node[0] and j == node[1]) or ((i, j) in visited):
                    continue
                queue.append((i, j))

                if (i, j) in o_list:
                    cost[i, j] = utils[node] + np.inf
                elif abs(i - node[0]) == abs(j - node[1]):
                    cost[i, j] = utils[node] + pow(2, 0.5)
                else:
                    cost[i, j] = utils[node] + 1
                if cost[i, j] < utils[i, j]:
                    utils[i, j] = cost[i, j]

        visited.append(node)
        queue.remove(node)

        return queue, visited, utils

    def process_queue(self, queue, utils):
        new_queue = []
        for q in queue:
            if q not in new_queue:
                new_queue.append(q)
        queue = new_queue

        min_cost = np.inf
        min_index = ()
        for q in queue:
            if utils[q] <= min_cost:
                min_cost = utils[q]
                min_index = q
        if queue[0] != min_index:
            queue.append(queue[0])
            queue.remove(min_index)
            queue[0] = min_index

        return queue

    def normalize_utils(self, utils):
        utils = np.where(utils == np.inf, -np.inf, utils)
        utils = np.where(utils != -np.inf, np.round(utils / (np.max(utils) + 1), 4), np.inf)
        return utils

    def compute_util_map(self, r, c, target, obstacle):
        utils = np.full((r, c), np.inf)
        utils[target] = 0

        visited = []
        queue = [target]
        o_list = []

        for o in obstacle:
            o_list.append(o.find_position())

        while queue:
            queue, visited, utils = self.explore_node(r, c, queue, visited, o_list, utils)
            if queue:
                queue = self.process_queue(queue, utils)

        utils = self.normalize_utils(utils)

        return utils


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
