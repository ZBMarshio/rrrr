# ROS-10：提示与参考答案

[返回题目](../讲义/ROS-10_排错状态与停止条件.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

A 可先查实际 topic/type 与发布者 → 两端 QoS/domain/发现配置 → 记录器是否 spin、回调是否阻塞或已异常。topic list 只说明图中发现了话题。

B 可先查消息 name/position 的映射与单位 → 模型关节轴/零位/连接 → TF frame 与时间及来源。保留同一组输入下的数值对照。

C 可先查发到哪个实际控制器入口 → 控制器 active、接口 claim 与输入有效性 → 硬件 write/read 和状态来源。请求打印成功不能跳过中间证据。

这不是固定唯一顺序，已有错误日志时先用直接证据。记录你为什么选择这三项，比机械背表更有价值。

<a id="ex2"></a>

## 第 2 题

ArmController 是 Python 类；teleop_bridge 是初始化指定的节点名；arm_controller/joint_trajectory 是相对话题路径；YAML 的 arm_controller 是控制器实例配置名称。

还要确认 namespace/remap 后完整话题、消息类型、实际 subscriber、manager 加载的控制器类型/状态/配置，以及执行反馈。路径里出现 controller 字样不保证该接收者存在，也不证明 Python 类就是底层控制器插件。

<a id="ex3"></a>

## 第 3 题

一种检查函数如下，输入时间均为同源整数 ns：

```python
import math

def command_gate(q, lower, upper, active, last_rx_ns, now_ns, max_age_ns):
    if len(lower) != 2 or len(upper) != 2 or max_age_ns <= 0:
        raise ValueError("invalid gate configuration")
    if any(
        not math.isfinite(lo) or not math.isfinite(hi) or lo > hi
        for lo, hi in zip(lower, upper)
    ):
        raise ValueError("invalid joint bounds")
    if not active:
        return False, "controller inactive"
    if last_rx_ns is None:
        return False, "no state received"
    age = now_ns - last_rx_ns
    if age < 0 or age > max_age_ns:
        return False, "state reception stale or time mismatch"
    try:
        values = [float(v) for v in q]
    except (TypeError, ValueError):
        return False, "invalid joint values"
    if len(values) != 2:
        return False, "expected two joint positions"
    if not all(math.isfinite(v) for v in values):
        return False, "non-finite joint positions"
    if any(v < lo or v > hi for v, lo, hi in zip(values, lower, upper)):
        return False, "joint position out of bounds"
    return True, "ready"
```

正常例子：q=[0.1,-0.2]、上下界 [-1,-1]/[1,1]、active=True、now_ns=200000000、last_rx_ns=150000000、max_age_ns=100000000，通过。

这个简化函数没有采样时钟映射、序号/旧帧检测、速度/加速度/碰撞检查，也不执行停止。接收活性通过仍需 ROS-06 的采样有效性检查。

<a id="ex4"></a>

## 第 4 题

路径可画成：策略状态/队列 → 当前目标与取消请求 → 控制器状态和保持/停止策略 → command interface/write → 实际状态反馈。

模拟观察中，停止策略后先看是否仍有旧目标执行；使用该控制器支持的取消/停止交互时，分别记录请求发出、确认、最终状态与关节反馈。不能只在客户端打印“已取消”就认为执行端已经停止。

JTC 的取消/替换行为与参数随版本变化，应对照当前实现与模拟记录；实际驱动的停机/失联处理、硬件停止属于平台流程。本章不提供跨平台通用“发零即停”的命令。

