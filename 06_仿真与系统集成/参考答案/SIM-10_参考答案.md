# SIM-10：提示与参考答案

[返回题目](../讲义/SIM-10_双臂接触与部署导读.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

复用 SIM-06 的名称映射。以下要求两组都已经转换为同一明确的执行器语义/单位：

```python
def merge_actuator_commands(left_names, left_values, right_names, right_values, actuator_order):
    left, right = list(left_names), list(right_names)
    lv, rv = np.asarray(left_values, dtype=float), np.asarray(right_values, dtype=float)
    if lv.shape != (len(left),) or rv.shape != (len(right),):
        raise ValueError("named actuator values required")
    return map_named_values(left+right, np.concatenate((lv, rv)), actuator_order)
```

重复名或集合不符会被拒绝。这个数组核对不处理臂间碰撞、规划协调、接触或同步；本章未运行完整双臂系统。

<a id="ex2"></a>

## 第 2 题

在同一 world 与时刻比较完整 SE(3)；只比物体原点不够。姿态差 10°不满足小容差下的刚性关系。可继续检查工具/抓取外参、配对时间、反馈、接触与物体观测，按实际证据定位。

<a id="ex3"></a>

## 第 3 题

RTF=2/0.1=20：

```python
def real_time_factor(simulated_seconds, wall_seconds):
    if not np.isfinite([simulated_seconds, wall_seconds]).all() or simulated_seconds < 0 or wall_seconds <= 0:
        raise ValueError("nonnegative simulation duration and positive wall duration required")
    return float(simulated_seconds/wall_seconds)
```

它只对应被计时的工作。在线系统还需测观测年龄、推理/规划时延、发送到实际应用/反馈的时间、周期抖动、丢帧/超时与负载条件。

<a id="ex4"></a>

## 第 4 题

已有第一章复跑说明、第二章链路、第三/四章模型控制、第五章标定/评测可以直接整合。交接应让别人从明确输入复现一个结果和一个失败，指出后端及未验证项。

研究扩展一次选一个，如新增双臂约束、触觉观测或并行评测；不要同时更换模型、接口与算法后失去原基线。

