# KIN-04：提示与参考答案

[返回题目](../讲义/KIN-04_正运动学FK.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

| q，单位 rad | 第二关节 xy，m | tool0 xy，m | yaw，rad |
|---|---|---|---|
| (0,0) | (0.3,0) | (0.5,0) | 0 |
| (π/2,0) | (0,0.3) | (0,0.5) | π/2 |
| (0,π/2) | (0.3,0) | (0.3,0.2) | π/2 |

位置计算中的近零数允许浮点误差。yaw 的周期表示可不同，比较物理旋转时按 KIN-02 处理。

<a id="ex2"></a>

## 第 2 题

先自己实现，再对照一个直接公式版本：

```python
import math
import numpy as np

def fk_xy(q, l1=0.3, l2=0.2):
    q = np.asarray(q, dtype=float)
    if q.shape != (2,) or not np.isfinite(q).all():
        raise ValueError("expected two finite joint angles")
    if not np.isfinite([l1, l2]).all() or l1 <= 0 or l2 <= 0:
        raise ValueError("link lengths must be finite and positive")
    q1, q2 = q
    return np.array([
        l1 * math.cos(q1) + l2 * math.cos(q1 + q2),
        l1 * math.sin(q1) + l2 * math.sin(q1 + q2),
    ])
```

另一种计算使用平面 3×3 齐次矩阵，假设输入已经按上面约定验证：

```python
import math
import numpy as np

def fk_chain_xy(q, l1=0.3, l2=0.2):
    def rot(theta):
        c, s = math.cos(theta), math.sin(theta)
        return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
    def trans_x(length):
        T = np.eye(3)
        T[0, 2] = length
        return T
    q1, q2 = q
    T = rot(q1) @ trans_x(l1) @ rot(q2) @ trans_x(l2)
    return T[:2, 2].copy()
```

需要完整空间 4×4 位姿时，可在同一模块中复用 fk_xy：

```python
import math
import numpy as np

def fk_pose(q, l1=0.3, l2=0.2):
    xy = fk_xy(q, l1, l2)
    theta = float(np.sum(q))
    c, s = math.cos(theta), math.sin(theta)
    T = np.eye(4)
    T[:3, :3] = [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]
    T[:2, 3] = xy
    return T
```

纯数值三角与矩阵对照可先用 1e-10 m 容差；实际 TF/测量需按其误差来源另定。函数片段由你组织进自己的模块，图示不代替你的运行。

<a id="ex3"></a>

## 第 3 题

第二段误用绝对 q2 时，q1=0 的例子可能碰巧通过；用 (π/2,0) 即可区分正确 (0,0.5) 与错误 (0.2,0.3)。

把 L1 写成 300 m 会在零位得到 x=300.2 m。漏掉第二段末端偏置时，零位只得到 (0.3,0)，差了 L2。

记录你选的反例和实际结果，不只把公式改回去。

<a id="ex4"></a>

## 第 4 题

变化为：

```text
delta_p = 0.05 × [cos(q1+q2), sin(q1+q2)] m
```

它沿第二段当前方向，通常不是基座 +x。例 q=(0,π/2) 时增加 (0,0.05) m。

改变真实 TCP 定义也有类似问题：固定偏置先在其所属局部坐标中定义，再随变换链进入基座。

