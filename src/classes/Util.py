# Created by longtaoliu at 19.04.21

import numpy as np

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
                utils[i, j] = self.compute_util(np.array([i, j]), np.array(target))
                #print('('+str(i)+','+str(j)+')'+str(utils[i, j]))
        
        utils = np.round(utils / (np.max(utils) + 1),4)
        
        for o in obstacle:
            utils[o.find_position()] = np.inf
        
        # normalize the utils to interval [0,1]
        return utils 

class InteractionCostUtil:
    """
       CostFUtil()
       A class represent Cost Function Util

       Parameters
       ----------

       Attributes
       ----------

    """ 

    def compute_util(self, r):
        self.r_max = 1
        return np.exp(1 / (np.power(r, 2) - np.power(self.r_max, 2))) if r < self.r_max else 0
    
    def compute_util_map(self,r,c,target,obstacle):
        # output the utils map
        utils = np.zeros((r, c))
        utils += np.inf
        

        utils = EuclideanUtil().compute_util_map(r,c,np.array([i, j]), np.array(target),obstacle)
             

        # normalize the utils to interval [0,1]
        return utils / (np.max(utils) + 1)
    






