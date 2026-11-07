# CTRL-09：提示与参考答案

[返回题目](../讲义/CTRL-09_约束超时与停止.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

延迟内走 0.04 rad，制动过程走 0.16 rad，共 0.20 rad；0.15 rad 在该理想条件下也不足。

```python
def ideal_stop_distance(velocity, delay, deceleration):
    if not np.isfinite([velocity, delay, deceleration]).all() or delay < 0 or deceleration <= 0:
        raise ValueError("finite values, nonnegative delay and positive deceleration required")
    return float(abs(velocity)*delay+velocity**2/(2*deceleration))
```

它是条件化的运动学估算。延迟内继续加速、负载或重力改变、净减速度不足、驱动状态不同等都可能增加实际距离；边界与测量余量也要另外考虑。

<a id="ex2"></a>

## 第 2 题

单步最大改变 [0.02,0.01] rad，所以输出 [0.02,-0.01] rad：

```python
def limit_position_reference(last_reference, desired, dt, vmax):
    last, desired, vmax = [np.asarray(v, dtype=float) for v in (last_reference, desired, vmax)]
    if last.ndim != 1 or last.size == 0 or desired.shape != last.shape or vmax.shape != last.shape:
        raise ValueError("same nonempty joint-vector shapes required")
    if not np.isfinite([dt]).all() or dt <= 0:
        raise ValueError("positive finite dt required")
    if any(not np.isfinite(a).all() for a in (last, desired, vmax)) or np.any(vmax <= 0):
        raise ValueError("finite references and positive velocity limits required")
    return last+np.clip(desired-last, -vmax*dt, vmax*dt)
```

这个结果只是参考，不是实际状态；步间参考速度可突变，所以没有自动满足加速度限制。还需控制器跟踪、实际状态检查和独立的新鲜度/边界门控。

<a id="ex3"></a>

## 第 3 题

复用 [ROS-06 答案](../../02_ROS2与机器人系统/参考答案/ROS-06_参考答案.md#ex4)与 [ROS-10 答案](../../02_ROS2与机器人系统/参考答案/ROS-10_参考答案.md#ex3)。

可以采用 ACTIVE→STALE→等待重新确认/重建参考→ACTIVE 的显式状态。超时时拒绝新运动目标，执行平台定义的停止/保持处理并记录其结果；恢复时检查实际位置、控制器状态和目标是否仍然有效。

这是一种可说明的策略，不是通用底层停机实现。平台文档/配置缺失时，把实际行为记为未确认，先在 mock 中验证状态转换。

<a id="ex4"></a>

## 第 4 题

“计时到终点”成立；控制器成功取决于其返回状态和容差，题中未给出；“任务到达”需要满足预先定义的位置/速度/任务容差，当前信息不足以通过。

记录可以包括：计划结束时间、实际时间戳、参考与实测、误差与容差、实际速度、action 结果/取消响应、命令门控原因、执行后端状态、是否在窗口内静止。数值/mock 与真机结论分别标明。

