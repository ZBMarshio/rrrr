# MATH-02：提示与参考答案

[返回题目](../讲义/MATH-02_导数梯度与链式法则.md) · [复盘](../练习与复盘记录.md)

<a id="ex1"></a>

## 第1题

内层为 0.5，g=0.25，梯度 [1,2]。一阶变化 -0.003；真实内层变成 0.497，真实差值 -0.002991，差为 9e-6，来自二阶项。

<a id="ex2"></a>

## 第2题

J=[[0.6,1],[cos(0.3),0]]，f=[-0.11,sin(0.3)]。损失 0.5||f||² 的梯度为 [0.6*(-0.11)+cos(0.3)*sin(0.3),-0.11]，约 [0.216321,-0.11]。

```python
import numpy as np

def central_jacobian(function, x, h=1e-6):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 1 or x.size == 0 or not np.isfinite(x).all() or not np.isfinite(h) or h <= 0:
        raise ValueError("finite nonempty vector and positive finite step required")
    base = np.atleast_1d(np.asarray(function(x), dtype=np.float64))
    if base.ndim != 1 or base.size == 0 or not np.isfinite(base).all():
        raise ValueError("finite scalar/vector output required")
    result = np.empty((base.size, x.size), dtype=np.float64)
    for col in range(x.size):
        step = np.zeros_like(x)
        step[col] = h
        plus = np.atleast_1d(np.asarray(function(x+step), dtype=np.float64))
        minus = np.atleast_1d(np.asarray(function(x-step), dtype=np.float64))
        if plus.shape != base.shape or minus.shape != base.shape or not np.isfinite(plus).all() or not np.isfinite(minus).all():
            raise ValueError("consistent finite output required")
        result[:,col] = (plus-minus)/(2*h)
    return result
```

本函数只做小数组、逐坐标绝对步长检查；不同量纲、边界、角度绕回和非光滑点需另行设计。

function应是固定输入可重复的映射。对会推进状态的仿真step，先恢复相同初态再比较扰动；否则差异可能来自状态演化，而非你要检查的导数。

<a id="ex3"></a>

## 第3题

先看误差数量级随 h 的趋势。中间某些 h 往往更合适，极小 h 相减会丢失有效位。不同版本/平台不承诺同一 h 总是最优；将解析值、dtype 和 h 一起保存。

<a id="ex4"></a>

## 第4题

中心差分为 0，但右导数为 1、左导数为 -1，该点不可导。数值检查是寻找错误的工具，不代替可微性条件；碰撞、clip、阈值等边界同样要单独考虑。
