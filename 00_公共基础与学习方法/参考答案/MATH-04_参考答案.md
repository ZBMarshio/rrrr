# MATH-04：提示与参考答案

[返回题目](../讲义/MATH-04_最小二乘伪逆与数值误差.md) · [复盘](../练习与复盘记录.md)

<a id="ex1"></a>

## 第1题

A=[[0,1],[1,1],[2,1]]，theta=[2,1]。中间点变3.1后，a=2、b=1+0.1/3，按预测减观测的残差约 [0.033333,-0.066667,0.033333]。

```python
import numpy as np

def fit_affine(reference, reading):
    x, y = [np.asarray(v,dtype=np.float64) for v in (reference,reading)]
    if x.ndim != 1 or x.shape != y.shape or x.size < 2:
        raise ValueError("paired vectors with at least two samples required")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("finite observations required")
    design = np.column_stack([x,np.ones_like(x)])
    theta, _, rank, singular = np.linalg.lstsq(design,y,rcond=None)
    if rank != 2:
        raise ValueError("distinct reference positions required")
    return theta, design@theta-y, singular
```

校正用 `(reading-b)/a` 前还需检查 a 非零、与传感器模型/范围相符。这里不设一个适用于所有仪器的固定增益阈值。

<a id="ex2"></a>

## 第2题

b=[1,1e-6]，带噪 b=[1,2e-6]，解从 [1,1] 变成 [1,2]。cond₂=1e6；输出扰动范数1e-6，解扰动范数1。这个例子的绝对放大比为1e6，能精确拟合含噪 b，所以残差仍为0。条件数描述相对敏感性的界，不保证所有方向都达到同样放大。

<a id="ex3"></a>

## 第3题

```python
def damped_lstsq(matrix, target, damping):
    a = np.asarray(matrix,dtype=np.float64)
    b = np.asarray(target,dtype=np.float64)
    if a.ndim != 2 or min(a.shape) < 1 or b.shape != (a.shape[0],):
        raise ValueError("nonempty A[m,n] and b[m] required")
    if not np.isfinite(a).all() or not np.isfinite(b).all() or not np.isfinite(damping) or damping <= 0:
        raise ValueError("finite inputs and positive damping required")
    augmented = np.vstack([a,damping*np.eye(a.shape[1])])
    rhs = np.concatenate([b,np.zeros(a.shape[1])])
    return np.linalg.lstsq(augmented,rhs,rcond=None)[0]
```

用增广系统表达上述 lambda² 正则目标，避免在实现中显式求逆。例子解约 [0.999999,0.000002]；弱方向几乎被压到0，离真值1仍很远。lambda 与变量尺度有关，此数值仅用于指定无量纲例子。

<a id="ex4"></a>

## 第4题

三组残差均为0，前两组范数1，第三组为1/√2。lstsq/pinv 返回最小欧氏范数解 [0.5,0.5]。关节限位、碰撞、当前姿态、不同单位/权重和任务约束没有自动包含在这个最小范数偏好中。
