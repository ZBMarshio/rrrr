# CTRL-08：提示与参考答案

[返回题目](../讲义/CTRL-08_最优控制与MPC导读.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

连续 `A=[[0,1],[0,-b/I]]`，`B=[[0],[1/I]]`。前向 Euler 为 `A_d=E+hA`、`B_d=hB`，E 是单位矩阵，h 是离散步长。

以本章 I=0.05、b=0.1 为例，A 的右下角 -2，B 的下项 20。前向 Euler 位置用旧速度；CTRL-01 半隐式 Euler 先更新速度，再用新速度更新位置。二者都不是连续模型的精确离散化。

<a id="ex2"></a>

## 第 2 题

最优序列 (0.5,0)，预测状态 0.5、0.5，代价 (0.01+0.025)+0.01=0.045。只执行首项 0.5；下一次从实际测得的 0.4 重算。

```python
from itertools import product

def tiny_mpc_step(x, target=0.6, *, actions=(-0.5, 0.0, 0.5), horizon=2, effort_weight=0.1):
    actions = tuple(float(u) for u in actions)
    if not actions or not np.isfinite([x, target, effort_weight, *actions]).all() or effort_weight < 0:
        raise ValueError("finite state, target, actions and nonnegative weight required")
    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError("positive integer horizon required")
    best = None
    for sequence in product(actions, repeat=horizon):
        predicted, cost = float(x), 0.0
        for u in sequence:
            predicted += u
            cost += (predicted-target)**2+effort_weight*u**2
        if best is None or cost < best["cost"]:
            best = {"action": sequence[0], "sequence": sequence, "cost": float(cost)}
    return best
```

该归一化小模型没有机器人单位、完整状态约束、求解超时和连续动作优化；用途是看懂滚动执行。

<a id="ex3"></a>

## 第 3 题

结果约为 `[[0.5,0.33333333],[0.33333333,0.77777778]]` kg（本例是平面平移任务）。不同方向具有耦合，不能分别用关节惯性逐元素除以 J。

局部计算采用线性求解，先核对模型条件：

```python
def task_inertia(M, J):
    M, J = np.asarray(M, dtype=float), np.asarray(J, dtype=float)
    if M.ndim != 2 or M.shape[0] == 0 or M.shape[0] != M.shape[1]:
        raise ValueError("square inertia matrix required")
    if J.ndim != 2 or J.shape[0] == 0 or J.shape[1] != M.shape[0]:
        raise ValueError("compatible task Jacobian required")
    if not np.isfinite(M).all() or not np.isfinite(J).all() or not np.allclose(M, M.T, atol=1e-12, rtol=0):
        raise ValueError("finite symmetric inertia required")
    np.linalg.cholesky(M)
    if np.linalg.matrix_rank(J) != J.shape[0]:
        raise ValueError("full row rank required")
    inverse_task_inertia = J @ np.linalg.solve(M, J.T)
    return np.linalg.solve(inverse_task_inertia, np.eye(J.shape[0]))
```

秩不足时公式中的逆不存在；近奇异时数值也可能很差。应重新考虑任务、正则化或其他控制策略，不能通过随意加一个数就宣称物理问题消失。

<a id="ex4"></a>

## 第 4 题

答案取决于所选论文。合格卡片能追踪状态→算法→动作→底层执行→反馈，明确模型、假设、训练条件与评测范围。

例如“策略每次输出 0.1”不够；要确认哪个关节/坐标、绝对或增量、单位、频率、内环和限制。发现缺口后，只补当前阅读需要的基础，不因一个高级名词把整章重学。

