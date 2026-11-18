import numpy as np

q = np.array([[0., 1.], [0.1, 0.9], [0.2, 0.8], [0.3, 0.7]])
bias = np.array([0.1, -0.2])

print("q:\n",q)
print("q[:, 0]:\n",q[:, 0])
print("q[:, 0:1]:\n",q[:, 0:1])

a = np.zeros((4, 2))
b = np.array([0.1, -0.2])   # (2,)
a + b                       # (4, 2)
b2 = b[:, None]   # 形状 (2, 1)
#a + b2            # ValueError

print("a:\n",a)
print("b:\n",b)
print("a+b:\n",a+b)
print(a.shape)
print("b2:\n",b2)
#print("a+b2:\n",a+b2)

alias = q
q = np.array([[0., 2.], [0.1, 0.9], [0.2, 0.8], [0.3, 0.7]])
print("alias_changed=", alias)   # 修改q不改变alias


X = np.array([[1, 3, 6, 10], [0, 5, 6, 8]])
print("axis=-1\n", np.diff(X))              # (1, 3)：默认最后一维
print("axis= 0\n", np.diff(X, axis=0))      # (1, 4)：按行（时间）差分