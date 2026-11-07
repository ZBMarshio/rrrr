# KIN-09：提示与参考答案

[返回题目](../讲义/KIN-09_旋量李群与指数积.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

```python
import numpy as np

def skew3(omega):
    x, y, z = np.asarray(omega, dtype=float)
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
```

skew3.T=-skew3，它将向量映射为叉乘结果，一般不满足旋转矩阵条件。SE(3) 的 T 底行为 [0,0,0,1]，se(3) 的生成矩阵底行为 [0,0,0,0]。

<a id="ex2"></a>

## 第 2 题

在已有 modern_robotics 环境中：

```python
import numpy as np
import modern_robotics as mr

M = np.eye(4)
M[0, 3] = 0.5
Slist = np.array([
    [0.0, 0.0],
    [0.0, 0.0],
    [1.0, 1.0],
    [0.0, 0.0],
    [0.0, -0.3],
    [0.0, 0.0],
])
q = np.array([0.4, -0.6])
T = mr.FKinSpace(M, Slist, q)
```

位置约 (0.472331614,0.077091637,0) m，yaw=-0.2 rad。按同一约定与 fk_pose 比较，零位和两组已知姿态也检查。

本次教材核对读取了作者 MIT 许可源码放临时目录，没有向系统安装该包。你的运行方式和版本应自行记录。

<a id="ex3"></a>

## 第 3 题

接上题的库、M、Slist 与 q，并假设已有自己的 jacobian_xy：

```python
Js = mr.JacobianSpace(Slist, q)
p = T[:3, 3]
J_point = np.column_stack([
    Js[3:, i] + np.cross(Js[:3, i], p)
    for i in range(Js.shape[1])
])
J_xy_from_space = J_point[:2, :]
```

它应与本章基座位置雅可比一致。第一轴的空间 v 列为零，但末端位置导数列不为零，直接截下三行漏掉了旋转的贡献。

本体雅可比的线速度分量又使用不同坐标表达；先读定义，不靠“都是 6×n”判断。

<a id="ex4"></a>

## 第 4 题

Delta@T 的位置为 (1.1,0,0)，T@Delta 为 (1,0.1,0)。前者增量在固定基座方向解释，后者在当前末端局部方向解释。

这里用纯平移方便比较。若 Delta 带旋转，它是整个刚体变换，左乘还可能改变原点位置，不能自动等同于“xyz 与 Euler 各自相加”。

记录策略动作时要有坐标、单位、绝对/增量、左右乘或具体组合方式，以及 TCP 定义。学会这些约定可复用到多种算法方向。

