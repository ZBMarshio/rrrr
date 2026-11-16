import numpy as np

def transform_points_2d(p, r, t):

    return p @ r.T + t