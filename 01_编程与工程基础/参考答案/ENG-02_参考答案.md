# ENG-02：提示与参考答案

[返回题目](../讲义/ENG-02_NumPy形状广播与计算.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

提示：先写各输入形状，广播从右向左检查；矩阵乘法看中间维度。

| 表达式 | 结果形状或结论 |
|---|---|
| `q[:, 0]` | `(4,)`，第一关节的时间序列 |
| `q[:, 0:1]` | `(4, 1)`，同一序列，保留列维 |
| `q + bias` | `(4, 2)`，每行加同一组关节偏置 |
| `q + bias[:, None]` | 不兼容：`(4, 2)` 与 `(2, 1)` 的倒数第二维冲突 |
| `q * q` | `(4, 2)`，每个位置平方 |
| `q @ q.T` | `(4, 4)`，各行之间的内积表，单位 rad² |
| `mean(q, axis=0)` | `(2,)`，各关节的时间均值 |
| `mean(q, axis=1)` | `(4,)`，每时刻两个关节的均值 |

“能计算”与“是想要的指标”分别检查。跨不同关节取均值是否有任务意义，也需你解释。

<a id="ex2"></a>

## 第 2 题

提示：误差仍是两列；先平方再沿时间平均，最后开根号。

```python
import numpy as np

def rmse_per_joint(q_ref, q_obs):
    ref = np.asarray(q_ref, dtype=np.float64)
    obs = np.asarray(q_obs, dtype=np.float64)
    if ref.ndim != 2 or ref.shape[1] != 2 or ref.shape[0] == 0:
        raise ValueError("expected non-empty (N, 2) q_ref")
    if obs.shape != ref.shape:
        raise ValueError("q_obs shape must match q_ref")
    if not np.isfinite(ref).all() or not np.isfinite(obs).all():
        raise ValueError("joint positions must be finite")
    error = obs - ref
    return np.sqrt(np.mean(error ** 2, axis=0))
```

样例误差为 `[[0.1,-0.2],[-0.1,0.2],[0.2,-0.2],[-0.2,0.2]]`。两列平方均值为 `[0.025,0.04]`，因此 RMSE 约 `[0.158113883,0.2] rad`。

第一关节观测全部加 0.1 后，该列误差变为 `[0.2,0.0,0.3,-0.1]`，RMSE 为 `sqrt(0.035) ≈ 0.187082869 rad`；第二列仍为 0.2。RMSE 一般不能通过给旧 RMSE 加偏置得到。

`np.asarray` 可能共享输入数据，但这个实现只读输入，计算创建新结果。验证“不修改”应在调用前后比较输入；不要把“不修改”与“必定复制”混为一谈。

<a id="ex3"></a>

## 第 3 题

输出为 `99.0 99.0 -1.0`。part 与 q 共享相关数据，saved 是独立复制。`saved = q` 只是多一个名字。

自己再做一次：先保存完整 `baseline = q.copy()`，修改 q，确认 baseline 保持原值。不要在已经被写成 99 的数组上建立“原始”基准。

<a id="ex4"></a>

## 第 4 题

提示：时间差属于每一行，所以应把 `(N-1,)` 改成 `(N-1, 1)`。

正确区间速度为 `[[1,-2],[2,-2]] rad/s`；原写法得到约 `[[1,-1],[4,-2]]`，把两项时间差分别对齐到了两列。

```python
import numpy as np

def interval_velocity(t, q):
    t = np.asarray(t, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    if t.ndim != 1 or t.size < 2:
        raise ValueError("t must be one-dimensional, with at least 2 samples")
    if q.ndim != 2 or q.shape != (t.size, 2):
        raise ValueError("q must have shape (len(t), 2)")
    if not np.isfinite(t).all() or not np.isfinite(q).all():
        raise ValueError("t and q must be finite")
    dt = np.diff(t)
    if np.any(dt <= 0):
        raise ValueError("t must be strictly increasing")
    return np.diff(q, axis=0) / dt[:, None]
```

对非常小的时间差，虽然大于零，差分仍可能放大噪声；这是后续数值与传感问题。此题先验证定义和广播方向，不声称已经解决了速度估计的全部问题。

