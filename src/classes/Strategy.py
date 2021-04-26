import numpy as np


def find_best_neighbor_diag(m, r, c):
    """
    find the best neighbor using Moore Neighborhood definition, which contents the diagonal position

    Parameters
    ----------
    m : array shape(rows, cols)
        utility map
    r : int
        row of cell which need to find the best neighbor
    c : int
        col of cell which need to find the best neighbor

    Returns
    -------
    tuple:
        the position of neighbor with smallest util around cell@(r,c) based on UtilMap m
    """

    neighbors = []
    best_n = (r, c)
    min_u = np.inf
    for i in range(-1, 2):
        new_r = r + i
        if 0 <= new_r <= len(m) - 1:
            for j in range(-1, 2):
                new_c = c + j
                if 0 <= new_c <= len(m[0]) - 1:
                    if new_c == c and new_r == r:
                        continue
                    # print('(' + str(new_r) + ',' + str(new_c) + ')' + str(m[new_r, new_c]))
                    neighbors.append(m[new_r, new_c])
                    if m[new_r, new_c] <= min_u:
                        best_n = (new_r, new_c)
                        min_u = m[new_r, new_c]
    return best_n


def find_best_neighbor_v_h(m, r, c):
    """
    find the best neighbor using Von Neumann neighborhood definition, which contents only vertically
    and horizontally position

    Parameters
    ----------
    m : array shape(rows, cols)
        utility map
    r : int
        row of cell which need to find the best neighbor
    c : int
        col of cell which need to find the best neighbor

    Returns
    -------
    tuple:
        the position of neighbor with smallest util around cell@(r,c) based on UtilMap m
    """
    best_n = (r, c)
    min_u = np.inf

    r_map, c_map = m.shape
    left_col = max(0, c - 1)
    right_col = min(c + 1, c_map - 1)

    up_row = max(0, r - 1)
    down_row = min(r + 1, r_map - 1)

    for new_c in range(left_col, right_col + 1):
        for new_r in range(up_row, down_row + 1):
            if (abs(new_r - r) != abs(new_c - c)) or (new_r == r and new_c == c):
                if m[new_r, new_c] <= min_u:
                    best_n = (new_r, new_c)
                    min_u = m[new_r, new_c]

    return best_n


def find_best_neighbor_total(m, r, c):
    """
    find the best neighbor in a timestep for 2x speed pedestrian, which search in a wide neighbors

    Parameters
    ----------
    m : array shape(rows, cols)
        utility map
    r : int
        row of cell which need to find the best neighbor
    c : int
        col of cell which need to find the best neighbor

    Returns
    -------
    tuple:
        the position of neighbor with smallest util around cell@(r,c) based on UtilMap m
    """
    best_n = (r, c)
    min_u = np.inf

    r_map, c_map = m.shape
    left_col = max(0, c - 1)
    right_col = min(c + 1, c_map - 1)

    up_row = max(0, r - 1)
    down_row = min(r + 1, r_map - 1)

    for new_c in range(left_col, right_col + 1):
        for new_r in range(up_row, down_row + 1):
            if m[new_r, new_c] <= min_u:
                best_n = (new_r, new_c)
                min_u = m[new_r, new_c]

    for i in [-2, 2]:
        new_r = i + r
        if 0 <= i + r <= r_map and m[new_r, c] <= min_u:
            best_n = (new_r, c)
            min_u = m[new_r, c]

    for j in [-2, 2]:
        new_c = j + c
        if 0 <= new_c <= c_map and m[r, new_c] <= min_u:
            best_n = (r, new_c)
            min_u = m[r, new_c]
    return best_n


def find_best_neighbor_total_v3(m, r, c):
    """
    find the best neighbor in a timestep for 3x speed pedestrian, which search in a wide neighbors

    Parameters
    ----------
    m : array shape(rows, cols)
        utility map
    r : int
        row of cell which need to find the best neighbor
    c : int
        col of cell which need to find the best neighbor

    Returns
    -------
    tuple:
        the position of neighbor with smallest util around cell@(r,c) based on UtilMap m
    """
    best_n = (r, c)
    min_u = np.inf

    r_map, c_map = m.shape

    for new_c in range(c - 2, c + 2 + 1):
        if c - 2 < 0 or c + 2 > c_map:
            continue
        for new_r in range(r - 2, r + 2 + 1):
            if r - 2 < 0 or r + 2 > r_map:
                continue
            if (abs(new_r - r) == abs(new_c - c)) and (abs(new_r - r) == 2):
                continue
            if m[new_r, new_c] <= min_u:
                best_n = (new_r, new_c)
                min_u = m[new_r, new_c]

    for i in [-3, 3]:
        new_r = i + r
        if 0 <= i + r <= r_map and m[new_r, c] <= min_u:
            best_n = (new_r, c)
            min_u = m[new_r, c]

    for j in [-3, 3]:
        new_c = j + c
        if 0 <= new_c <= c_map and m[r, new_c] <= min_u:
            best_n = (r, new_c)
            min_u = m[r, new_c]

    return best_n