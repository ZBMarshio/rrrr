import numpy as np

q = np.array([[0., 1.],
                [0.1, 0.9],
                [0.2, 0.8],
                [0.3, 0.7]])

part = q[:2]            # 切片操作共享数据
saved = q[:2].copy()    # 使用.copy()在内存进行拷贝
part[0, 0] = 99.0
saved[0, 0] = -1.0
print(q[0, 0], part[0, 0], saved[0, 0]) # 结果中前两个一样

baseline = q.copy() # 保留基准数据还是应该用.copy