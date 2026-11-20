import numpy as np

q_r = np.array([[0., 1.],
                [0.1, 0.9],
                [0.2, 0.8],
                [0.3, 0.7]])
q_o = np.array([[0.3, 1.2],
                [0.2, 0.9],
                [0.4, 0.9],
                [0.4, 0.7]])

def rmse_per_joint(q_ref, q_obs):
    ref = np.asarray(q_ref, dtype=np.float64)
    obs = np.asarray(q_obs, dtype=np.float64)

    if ref.ndim != 2 or ref.shape[1] != 2 or ref.shape[0] == 0:
        raise ValueError("input error")
    if obs.ndim != 2 or obs.shape[1] != 2 or obs.shape[0] == 0:
        raise ValueError("input error")

    if ref.shape != obs.shape:
        raise ValueError("ref must match obs")

    if not np.isfinite(ref).all() or not np.isfinite(obs).all():
        raise ValueError("ref and obs must be finite")

    if np.isnan(ref).all() or np.isnan(obs).all():
            raise ValueError("ref and obs can't be None")
    
    return np.sqrt(np.mean((q_ref - q_obs)**2, axis=0))

if __name__ == "__main__":
    print("rmse=", rmse_per_joint(q_r, q_o))

# 原本 rmse= [0.19364917 0.1118034 ]
# obs 两关节都+0.1 rmse= [0.28722813 0.19364917]
# 只第1关节+0.1 rmse= [0.28722813 0.1118034 ]
# 偏置只影响被加的那一列；第1列误差均值0.175，涨幅明显