# CTRL-04：提示与参考答案

[返回题目](../讲义/CTRL-04_路径轨迹与时间参数.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

| t/s | q/rad | qd/(rad/s) | qdd/(rad/s²)，区间内公式 |
|---|---|---|---|
| 0 | [0,0] | [0,0] | [0.9,-0.6] |
| 1 | [0.3,-0.2] | [0.45,-0.3] | [0,0] |
| 2 | [0.6,-0.4] | [0,0] | [-0.9,0.6] |

运动外保持位置时，加速度为零；表中端点加速度是运动区间一侧的值。位置与速度连续，加速度不连续。

<a id="ex2"></a>

## 第 2 题

先只实现 cubic，再对照可选分支。函数以一维关节数组为约定，t 是标量：

```python
import numpy as np

def joint_reference(q0, qf, t, T, kind="cubic"):
    q0, qf = np.asarray(q0, dtype=float), np.asarray(qf, dtype=float)
    if q0.ndim != 1 or q0.size == 0 or qf.shape != q0.shape:
        raise ValueError("same nonempty joint-vector shapes required")
    if not np.isfinite(q0).all() or not np.isfinite(qf).all():
        raise ValueError("finite joints required")
    if not np.isfinite([t, T]).all() or T <= 0:
        raise ValueError("finite time and positive duration required")
    if kind not in ("cubic", "quintic"):
        raise ValueError("unknown time scaling")
    zeros = np.zeros_like(q0)
    if t < 0:
        return q0.copy(), zeros.copy(), zeros.copy()
    if t > T:
        return qf.copy(), zeros.copy(), zeros.copy()
    u = t/T
    if kind == "cubic":
        s = 3*u**2 - 2*u**3
        sd = (6*u - 6*u**2)/T
        sdd = (6 - 12*u)/T**2
    else:
        s = 10*u**3 - 15*u**4 + 6*u**5
        sd = (30*u**2 - 60*u**3 + 30*u**4)/T
        sdd = (60*u - 180*u**2 + 120*u**3)/T**2
    delta = qf-q0
    return q0+delta*s, delta*sd, delta*sdd
```

有限差分只在光滑区间做，选若干内部点与适当步长；无限缩小步长也会放大舍入误差。可与 Modern Robotics 作者库的 CubicTimeScaling/QuinticTimeScaling 核对 s，但不要用相同公式的另一份复制当唯一证据。

<a id="ex3"></a>

## 第 3 题

速度给出 T≥max(0.9,1.2)=1.2 s；加速度给出 T≥max(sqrt(1.8),sqrt(2.4))。所以共同要求：

`T_min=sqrt(2.4)≈1.549193338 s`。

局部计算片段：

```python
def cubic_min_duration(q0, qf, vmax, amax):
    arrays = [np.asarray(v, dtype=float) for v in (q0, qf, vmax, amax)]
    start, goal, vel, acc = arrays
    if start.ndim != 1 or start.size == 0 or any(a.shape != start.shape for a in arrays):
        raise ValueError("same nonempty joint-vector shapes required")
    if any(not np.isfinite(a).all() for a in arrays) or np.any(vel <= 0) or np.any(acc <= 0):
        raise ValueError("finite values and positive limits required")
    delta = np.abs(goal-start)
    return float(max(np.max(1.5*delta/vel), np.max(np.sqrt(6*delta/acc))))
```

零位移返回 0，表示不需要运动；它不能作为 joint_reference 的正时长输入。正式执行还要留出模型误差余量，并核对执行器、碰撞和实际反馈。

<a id="ex4"></a>

## 第 4 题

复用前面的函数与 CTRL-01 的 simulate_joint，可这样构造参考，不代写整套项目：

```python
def make_scalar_reference(T, qf=0.6):
    def reference(t):
        q, qd, _ = joint_reference([0.0], [qf], t, T)
        return float(q[0]), float(qd[0])
    return reference
```

分别传入 T=0.4 与 2.0，其他条件相同。解析参考峰值分别为：

| T/s | 最大速度/(rad/s) | 最大加速度/(rad/s²) |
|---|---|---|
| 0.4 | 2.25 | 22.5 |
| 2.0 | 0.45 | 0.9 |

短时长提高执行要求，限幅时 raw 不等于 applied。误差结果来自实际积分，不应写成“t=T，所以已到达”；[核对记录](../示例核对记录.md)给的是参考运行，不填你的练习状态。

