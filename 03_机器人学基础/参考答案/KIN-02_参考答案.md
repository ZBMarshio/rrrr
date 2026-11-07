# KIN-02：提示与参考答案

[返回题目](../讲义/KIN-02_旋转位姿与四元数.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

```python
import math
import numpy as np

def rz(theta):
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
```

Rz(π/2) 将 +x 变到 +y；90 rad 不会得到这一姿态。按同一右手约定，Rz@Rx 作用于 +y 得 +z，而 Rx@Rz 得 -x。最右侧先作用。

<a id="ex2"></a>

## 第 2 题

q=(0,0,√0.5,√0.5)。在已有 SciPy 环境：

```python
import numpy as np
from scipy.spatial.transform import Rotation

q = np.array([0.0, 0.0, np.sqrt(0.5), np.sqrt(0.5)])
R1 = Rotation.from_quat(q).as_matrix()
R2 = Rotation.from_quat(-q).as_matrix()
assert np.allclose(R1, R2)
```

q-(-q)=2q，不是零，但姿态相同。默认 scalar-last 与这里一致，其他库要另查。零四元数应被拒绝；不把 SciPy 自动归一化理解成所有输入都有效。

<a id="ex3"></a>

## 第 3 题

```python
import numpy as np

def is_rigid_transform(T, atol=1e-8):
    T = np.asarray(T, dtype=float)
    if T.shape != (4, 4) or not np.isfinite(T).all():
        return False
    if not np.allclose(T[3], [0, 0, 0, 1], atol=atol, rtol=0):
        return False
    R = T[:3, :3]
    return (
        np.allclose(R.T @ R, np.eye(3), atol=atol, rtol=0)
        and abs(np.linalg.det(R) - 1.0) <= atol
    )
```

反射矩阵 R.T R=I，但 det=-1，应该拒绝。这里是小规模数值检查，不负责修复坏矩阵或证明实际标定正确；非数值对象转换失败也应由输入层说明。

<a id="ex4"></a>

## 第 4 题

直接角差为 -358°，最小姿态差为 2°。相对旋转的 trace 可给最小旋转角：

```python
import numpy as np

def rotation_error_angle(R_target, R_current):
    R_error = R_target @ R_current.T
    cosine = (np.trace(R_error) - 1.0) / 2.0
    return float(np.arccos(np.clip(cosine, -1.0, 1.0)))
```

输入前提是合法旋转矩阵，输出在 [0,π]、单位 rad。clip 防舍入越过 arccos 定义域，不能修复任意坏 R。非常小的角度用 trace/arccos 可能损失精度，按任务容差或成熟旋转实现处理。

