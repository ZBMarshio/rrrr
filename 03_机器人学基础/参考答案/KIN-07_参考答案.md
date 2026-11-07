# KIN-07：提示与参考答案

[返回题目](../讲义/KIN-07_奇异冗余与零空间.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

q=(0,0) 时 rank=1、det=0，奇异值为约 [0.538516481,0]。q=(0,π/2) 时 det=0.06，rank=2。

伸直时 xdot=0，ydot=0.5 q1dot+0.2 q2dot。它限制了一阶方向，不禁止关节运动或有限弯曲。

q2=1e-3 时理论满秩，但最小奇异值很小，条件数很大；用固定单位和 np.linalg.svd/cond 记录实际数值。

<a id="ex2"></a>

## 第 2 题

在已有 jacobian_xy 的模块中：

```python
import numpy as np

J = jacobian_xy([0.0, 1e-3])
desired_v = np.array([0.01, 0.0])
qdot_pinv = np.linalg.pinv(J) @ desired_v
damping = 0.01
qdot_damped = J.T @ np.linalg.solve(
    J @ J.T + damping**2 * np.eye(2), desired_v,
)
```

伪逆速度约为 [33.3333,-83.3333] rad/s，范数很大；阻尼解抑制放大，但不能准确给出原要求的 x 速度。用同一 J 计算残差体现取舍。

本例是数学速度需求，尚未检查执行器限速、加速度、轨迹或接触。

<a id="ex3"></a>

## 第 3 题

教学矩阵 rank=2、n=3，核包含 (-1,-1,1)，J 乘它为零；可沿这个方向进行局部连续调整。

2R 两肘部分支一般是分开的关节解，不说明每个普通构型都留有一个连续自由方向。伸直奇异点出现额外瞬时零空间，又是另一种秩变化。

<a id="ex4"></a>

## 第 4 题

```python
import numpy as np

J = np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 1.0]])
z = np.array([0.0, 0.0, 1.0])
N = np.eye(3) - np.linalg.pinv(J) @ J
direction = N @ z
damping = 0.1
J_damped = J.T @ np.linalg.solve(J @ J.T + damping**2*np.eye(2), np.eye(2))
direction_damped = (np.eye(3) - J_damped @ J) @ z
```

direction≈(-1/3,-1/3,1/3)，J@direction 在浮点容差内为零；J@direction_damped 一般非零。不要称阻尼后的矩阵为精确正交零空间投影。

加入关节居中等次目标时，要观察主任务偏差，并考虑限位与有限步长。此处不要求实现整套冗余控制器。

