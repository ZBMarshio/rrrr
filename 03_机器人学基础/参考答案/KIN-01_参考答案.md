# KIN-01：提示与参考答案

[返回题目](../讲义/KIN-01_坐标与变换方向.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

提示：B 的 x 轴朝 A 的 +y，所以点的 (1,0,2) 先旋转为 (0,1,2)，再平移。

```python
import numpy as np

T_A_B = np.array([
    [0.0, -1.0, 0.0, 1.0],
    [1.0,  0.0, 0.0, 0.0],
    [0.0,  0.0, 1.0, 0.5],
    [0.0,  0.0, 0.0, 1.0],
])
p_B = np.array([1.0, 0.0, 2.0, 1.0])
p_A = T_A_B @ p_B
```

p_A=(1,1,2.5) m。逆变换后恢复 (1,0,2)。这是第二章坐标题的同一约定，可以复用旧数值作为证据。

<a id="ex2"></a>

## 第 2 题

T_B_C 是平移 (0.2,0,0)，所以 C 原点在 A 中是 (1,0.2,0.5) m。

若只是反序做数组乘法，会得到平移 (1.2,0,0.5)。它不是原坐标链的答案；这里用反序结果观察乘法不交换，不将它重新命名为原来的 T_A_C。

<a id="ex3"></a>

## 第 3 题

输入前提是合法刚体变换，检查矩阵本身放 KIN-02：

```python
import numpy as np

def rigid_inverse(T):
    T = np.asarray(T, dtype=float)
    if T.shape != (4, 4):
        raise ValueError("expected a 4x4 rigid transform")
    R, p = T[:3, :3], T[:3, 3]
    result = np.eye(4)
    result[:3, :3] = R.T
    result[:3, 3] = -R.T @ p
    return result
```

纯旋转且无平移时，整个齐次矩阵的转置碰巧等于逆；一加入平移，T.T 会把平移放到错误的最后一行。检查点来回变换和末行能暴露问题。

<a id="ex4"></a>

## 第 4 题

查询 base 为 target、camera 为 source，得到将 camera 数值变到 base 的关系，再应用到点。采集时刻的动态关系与 latest 区分，静态外参也需明确来源。

数学、离线 Buffer、Listener 收发与真实标定分别属于不同证据，不用其中一项替代全部。

