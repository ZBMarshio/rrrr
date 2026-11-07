# KIN-05：提示与参考答案

[返回题目](../讲义/KIN-05_雅可比与局部运动.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

```python
import math
import numpy as np

def jacobian_xy(q, l1=0.3, l2=0.2):
    q = np.asarray(q, dtype=float)
    if q.shape != (2,) or not np.isfinite(q).all():
        raise ValueError("expected two finite joint angles")
    if not np.isfinite([l1, l2]).all() or l1 <= 0 or l2 <= 0:
        raise ValueError("link lengths must be finite and positive")
    q1, q2 = q
    s1, c1 = math.sin(q1), math.cos(q1)
    s12, c12 = math.sin(q1 + q2), math.cos(q1 + q2)
    return np.array([
        [-l1 * s1 - l2 * s12, -l2 * s12],
        [ l1 * c1 + l2 * c12,  l2 * c12],
    ])
```

q=(0,0) 时 J=[[0,0],[0.5,0.2]]；q=(0,π/2) 时 J=[[-0.2,-0.2],[0.3,0]]。

后者乘 (0.1,-0.2)，得到 xdot=(0.02,0.03) m/s。列向量是单位关节速度的瞬时贡献，不是两段连杆本身。

<a id="ex2"></a>

## 第 2 题

```python
import numpy as np

def finite_difference_jacobian(f, q, h=1e-6):
    q = np.asarray(q, dtype=float)
    if q.ndim != 1 or not np.isfinite(q).all():
        raise ValueError("q must be a finite vector")
    if not np.isfinite(h) or h <= 0:
        raise ValueError("h must be finite and positive")
    columns = []
    for i in range(q.size):
        step = np.zeros_like(q)
        step[i] = h
        columns.append((f(q + step) - f(q - step)) / (2 * h))
    return np.column_stack(columns)
```

同一模块中已有 fk_xy 时，比较 `finite_difference_jacobian(fk_xy,q)` 和 `jacobian_xy(q)`。本章普通构型、h=1e-6 可先用最大绝对误差 <1e-7 m/rad 检查。

差分也依赖 FK、步长、浮点和坐标约定，因此不把它当作所有模型的绝对真值。解析公式和独立库对照能补充证据。

<a id="ex3"></a>

## 第 3 题

在已有函数上计算：

```python
import numpy as np

q = np.array([0.4, -0.6])
dq = np.array([0.01, -0.02])
actual = fk_xy(q + dq) - fk_xy(q)
linear = jacobian_xy(q) @ dq
error = np.linalg.norm(actual - linear)
```

参考误差是遗漏的高阶项；足够小且未受舍入主导时，步长减半通常让主要二阶误差约为原来四分之一。应记录自己测得数值，而不是把“约四分之一”当成不带条件的断言。

<a id="ex4"></a>

## 第 4 题

两个速度相同，列交换后求和不变，可能漏掉错误。选 qdot=(0.1,0) 与 (0,0.1) 分别检查，再用有限差分确认每一列。

例如 q=(0,π/2)，只动 q1 会产生 (-0.02,0.03) m/s；只动 q2 产生 (-0.02,0) m/s。纵向分量能暴露交换问题。

