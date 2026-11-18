import numpy as np

t = np.array([0.0, 0.1, 0.3])
dt = np.diff(t)

q = np.array([[0.0, 1.0],
              [0.1, 0.8],
              [0.5, 0.4]])
v_bad = np.diff(q, axis=0) / np.diff(t)
v = np.diff(q, axis=0) / dt[:, None]

print("dt:\n", dt)
print("dt[:, None]:\n", dt[:, None])
print("dt[None, :]:\n", dt[None, :])

print("v_bad:\n", v_bad)
print("v:\n", v)

# 手算：dt=([0.1, 0.2])   dq=([0.1, -0.2], [0.4, -0.4])
#       v=([1, -2], [2, -2])


def interval_velocity(t, q):
    t = np.asarray(t, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)

    dt = np.diff(t)
    return np.diff(q, axis=0) / dt[:, None]