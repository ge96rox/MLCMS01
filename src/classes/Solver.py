import numpy as np
import heapq
import copy


class NarrowNode(object):
    def __init__(self, time: int, pos: tuple):
        self.time = time
        self.position = pos

    def __repr__(self):
        return f'NarrowNode value: {self.time, self.position}'

    def __lt__(self, other):
        return self.time < other.time


class SolverTemplate:
    def __init__(self, u_map, f_i_map):
        self.u_map = u_map
        self.f_i_map = f_i_map

    def normalize_utils(self, utils):
        utils = np.where(utils == np.inf, -np.inf, utils)
        utils = np.where(utils != -np.inf, np.round(utils / (np.max(utils) + 1), 4), np.inf)
        return utils

    def solve(self):
        pass

    def find_neighbor(self, m, r, c):
        n = set()
        r_map, c_map = m.shape
        left_col = max(0, c - 1)
        right_col = min(c + 1, c_map - 1)

        up_row = max(0, r - 1)
        down_row = min(r + 1, r_map - 1)

        for new_c in range(left_col, right_col + 1):
            for new_r in range(up_row, down_row + 1):
                if abs(new_r - r) != abs(new_c - c):
                    n.add((new_r, new_c))
        return n

    def solve_process(self, t_row, t_col):
        rows, cols = self.u_map.shape
        unknown_set = set()
        narrow_set = set()
        frozen_set = set()
        narrow_mq = []
        for i in range(0, rows):
            for j in range(0, cols):
                if i != t_row or j != t_col:
                    unknown_set.add((i, j))
                    self.u_map[i, j] = np.inf
                if i == t_row and j == t_col:
                    self.u_map[i, j] = 0
                    narrow_set.add((i, j))
                    heapq.heappush(narrow_mq, NarrowNode(0, (i, j)))
        while len(narrow_set) != 0:
            node = heapq.heappop(narrow_mq)
            t_min = node.time
            row_min, col_min = node.position
            neighbor = self.find_neighbor(self.u_map, row_min, col_min)
            for rc_neighbor in neighbor:
                if not (rc_neighbor in frozen_set):
                    t_i = self.solve(rc_neighbor, row_min, col_min)
                    if rc_neighbor in unknown_set:
                        narrow_set.add(rc_neighbor)
                        heapq.heappush(narrow_mq, NarrowNode(t_i, rc_neighbor))
                        unknown_set.remove(rc_neighbor)
            set_to_op = set()
            set_to_op.add((row_min, col_min))
            narrow_set = narrow_set - set_to_op
            frozen_set.union(set_to_op)

        return self.normalize_utils(self.u_map)


class FmmSolver(SolverTemplate):
    def __init__(self, u_map, f_i_map):
        super().__init__(u_map, f_i_map)

    def solve_eikonal(self, row, col, t_i, f_i):
        a = 2
        min_queue = []
        for dim in range(0, 2):
            min_t = self.min_t_dim(self.u_map, row, col, dim)
            if min_t != np.inf and min_t < t_i:
                heapq.heappush(min_queue, min_t)
            else:
                a -= 1
        if a == 0:
            return np.inf
        t_hat_i = None
        for dim in range(0, a):
            t_hat_i = self.solve_n_dims(dim, min_queue, f_i)
            if dim == a - 1:
                break
            elif t_hat_i < min_queue[dim + 1]:
                break
        return t_hat_i

    def solve_n_dims(self, dim, min_queue, f_i):
        if f_i == 0:
            return np.inf
        copy_mq = copy.deepcopy(min_queue)
        if dim == 0:
            return heapq.heappop(copy_mq) + (1 / f_i)
        sum_t = sum(copy_mq[:dim + 1])
        sum_t2 = sum(list(map(lambda i: i ** 2, copy_mq))[:dim + 1])
        a = dim
        b = -2 * sum_t
        c = sum_t2 - (1 / f_i)
        q = b ** 2 - 4 * a * c
        if q < 0:
            return np.inf
        else:
            return (-b + np.sqrt(q)) / (2 * a)

    def min_t_dim(self, u_map, row, col, dim):
        if dim == 1:
            return min(u_map[row, max(0, col - 1)], u_map[row, min(len(u_map[1]) - 1, col + 1)])
        else:
            return min(u_map[max(0, row - 1), col], u_map[min(len(u_map[0]) - 1, row + 1), col])

    def solve(self, rc_neighbor, row_min, col_min):
        r, c = rc_neighbor
        t_i = self.u_map[r, c]
        t_hat_i = self.solve_eikonal(r, c, t_i, self.f_i_map[r][c])
        if t_hat_i < t_i:
            t_i = t_hat_i
            self.u_map[r, c] = t_i
        return t_i


class DijkstraSolver(SolverTemplate):
    def __init__(self, u_map, f_i_map):
        super().__init__(u_map, f_i_map)

    def solve_dijkstra(self, t_min, f_i):
        if f_i == np.inf:
            return np.inf
        else:
            return t_min + 1

    def solve(self, rc_neighbor, row_min, col_min):
        r, c = rc_neighbor
        t_min = self.u_map[row_min, col_min]
        t_i = self.u_map[r, c]
        t_hat_i = self.solve_dijkstra(t_min, self.f_i_map[r][c])

        if t_hat_i < t_i:
            t_i = t_hat_i
            self.u_map[r, c] = t_i
        return t_i
