# KIN-06：提示与参考答案

[返回题目](../讲义/KIN-06_解析与数值IK.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

参考函数返回理想无障碍模型的候选，不自动保证限位与路径：

```python
import math
import numpy as np

def analytic_ik_2r(target, l1=0.3, l2=0.2, eps=1e-10):
    target = np.asarray(target, dtype=float)
    if target.shape != (2,) or not np.isfinite(target).all():
        raise ValueError("target must be finite xy")
    if not np.isfinite([l1, l2]).all() or l1 <= 0 or l2 <= 0:
        raise ValueError("link lengths must be finite and positive")
    x, y = target
    c2 = (x*x + y*y - l1*l1 - l2*l2) / (2*l1*l2)
    if abs(c2) > 1.0 + eps:
        return []
    c2 = float(np.clip(c2, -1.0, 1.0))
    s = math.sqrt(max(0.0, 1.0 - c2*c2))
    solutions = []
    for s2 in (s, -s):
        q2 = math.atan2(s2, c2)
        q1 = math.atan2(y, x) - math.atan2(l2*s2, l1+l2*c2)
        solutions.append(np.array([q1, q2]))
    return solutions
```

目标 (0.3,0.2) 得约 (0,1.570796327) 和 (1.176005207,-1.570796327) rad；代回位置相同。边界可能返回重复/周期等价候选，按关节约定再处理。

本例两段不等长。若扩展到等长且目标正好原点，第一关节可能出现连续多解，不能用这段普通分支代码代表完整解集。

<a id="ex2"></a>

## 第 2 题

以下是一种完整的教学函数，依赖同一模块中已验证的 fk_xy、jacobian_xy。建议自己尝试后对照，并保留自己的结构。

```python
import numpy as np

def solve_ik_position(
    target, q0, *, l1=0.3, l2=0.2, lower=None, upper=None,
    tol=1e-6, damping=1e-3, max_step=0.2, max_iter=150,
):
    target = np.asarray(target, dtype=float)
    q = np.asarray(q0, dtype=float).copy()
    lo = np.array([-np.pi, -np.pi]) if lower is None else np.asarray(lower, dtype=float)
    hi = np.array([np.pi, np.pi]) if upper is None else np.asarray(upper, dtype=float)
    if any(a.shape != (2,) or not np.isfinite(a).all() for a in (target, q, lo, hi)):
        raise ValueError("target, q0 and limits must be finite two-vectors")
    if np.any(lo > hi) or np.any(q < lo) or np.any(q > hi):
        raise ValueError("invalid limits or initial position")
    if not np.isfinite([tol, damping, max_step]).all() or min(tol, damping, max_step) <= 0:
        raise ValueError("positive finite solver parameters required")
    if not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("max_iter must be a positive integer")
    fk_xy(q, l1, l2)
    history = []

    def finish(reason, iterations):
        return q.copy(), {
            "success": reason == "converged",
            "reason": reason,
            "iterations": iterations,
            "residual_m": float(np.linalg.norm(target - fk_xy(q, l1, l2))),
            "history_m": history.copy(),
        }

    radius = np.linalg.norm(target)
    if radius > l1 + l2 + tol or radius < abs(l1-l2) - tol:
        history.append(float(np.linalg.norm(target - fk_xy(q, l1, l2))))
        return finish("geometrically_unreachable", 0)

    for iteration in range(max_iter + 1):
        error = target - fk_xy(q, l1, l2)
        residual = float(np.linalg.norm(error))
        history.append(residual)
        if residual <= tol:
            return finish("converged", iteration)
        if iteration == max_iter:
            return finish("max_iter", iteration)
        J = jacobian_xy(q, l1, l2)
        dq = J.T @ np.linalg.solve(J @ J.T + damping**2 * np.eye(2), error)
        size = np.linalg.norm(dq)
        if size < 1e-12:
            return finish("stalled", iteration)
        if size > max_step:
            dq *= max_step / size
        accepted = False
        for scale in (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125):
            candidate = np.clip(q + scale*dq, lo, hi)
            candidate_error = np.linalg.norm(target - fk_xy(candidate, l1, l2))
            if candidate_error < residual - 1e-12:
                q = candidate
                accepted = True
                break
        if not accepted:
            return finish("stalled", iteration)
```

限制单步和回溯用来帮助这个小例子稳定；关节限位用投影处理仍可能停滞，不是完整约束优化器。几何范围判断只排除明显超出位置容差的目标，不含碰撞/姿态判断。

输入异常、solver 未收敛、执行失败应分别处理。不要把一个返回 q 的函数自动当作成功。

<a id="ex3"></a>

## 第 3 题

普通目标应能从合适初值收敛，但记录实际迭代与残差。

target=(0.45,0)、q0=(0,0) 时，误差沿 x，而当前 J 的两列都沿 y；J.T@error=0，参考算法停滞。换成非零初值可以提供另一张局部地图，这不改变目标本来可达的事实。

(0.7,0) 超出半径 0.5 m，有几何不可达证据。q2 限在 [-1,1] 的 (0.3,0.2) 案例，解析解要求 ±π/2，有限位不可达；数值函数可能只报告 stalled，不把它的局部退出理由当作完整数学证明。

<a id="ex4"></a>

## 第 4 题

两个分支的 yaw 约为 π/2 和 -0.394791120 rad，都不是 0；位置收敛不满足新加的完整平面位姿任务。一般两关节不能任意独立指定 x、y、yaw 三项。

TCP 改变要更新几何/工具变换并用一致 FK 求解。真实可执行性还需规划、动力学、控制与设备验证，本函数只做数学位置任务。

