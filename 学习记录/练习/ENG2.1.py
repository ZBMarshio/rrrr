import numpy as np
q = np.array([[0., 1.], [0.1, 0.9], [0.2, 0.8], [0.3, 0.7]])
bias = np.array([0.1, -0.2])

print("q[:, 0].shape:", (q[:, 0]).shape)    # 这里大概懂了，但是说不清楚
print("q[:, :1].shape:", (q[:, :1]).shape)  # 

print("(q + bias).shape:", (q + bias).shape)
# (4,2) + (2,) ---> 2=2 , 4"="1  广播规则成立
#print("(q + bias[:, None]).shape:", (q + bias[:, None]).shape)
# (4,2) + (2,1)：最右维 2 与 1 可广播，但往左一维 4 与 2 既不相等也非 1 → ValueError

print("(q * q).shape:", (q * q).shape)      # 逐点相称，不会变化shape
print("(q @ q.T).shape:", (q @ q.T).shape)  # 作矩阵乘法

print("(np.mean(q, axis=0)):", np.mean(q, axis=0)) # 沿第0轴作平均值，也就是列
print("(np.mean(q, axis=1)):", np.mean(q, axis=1)) # 沿第1轴作平均值，也就是行
print("(np.mean(q, axis=0)).shape:", (np.mean(q, axis=0)).shape)
print("(np.mean(q, axis=1)).shape:", (np.mean(q, axis=1)).shape)
