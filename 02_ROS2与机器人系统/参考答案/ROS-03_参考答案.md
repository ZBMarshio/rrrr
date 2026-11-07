# ROS-03：提示与参考答案

[返回题目](../讲义/ROS-03_QoS执行器与回调.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

假设其他相关策略兼容：

| Publisher | Subscriber | 兼容 |
|---|---|---|
| BEST_EFFORT | BEST_EFFORT | 是 |
| BEST_EFFORT | RELIABLE | 否 |
| RELIABLE | BEST_EFFORT | 是 |
| RELIABLE | RELIABLE | 是 |

| Publisher | Subscriber | 兼容与迟加入结果 |
|---|---|---|
| VOLATILE | VOLATILE | 是，接入后的新消息 |
| VOLATILE | TRANSIENT_LOCAL | 否 |
| TRANSIENT_LOCAL | VOLATILE | 是，不因此请求已有历史 |
| TRANSIENT_LOCAL | TRANSIENT_LOCAL | 是，可获得保留的历史与新消息 |

历史还受 depth、资源、生命周期等影响。TRANSIENT_LOCAL 不是永久数据库，普通话题也没有替你保存整个实验。

<a id="ex2"></a>

## 第 2 题

可先离线检查：

```python
from rclpy.qos import (
    QoSProfile, ReliabilityPolicy, DurabilityPolicy, LivelinessPolicy,
    QoSCompatibility, qos_check_compatible,
)

publisher_qos = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    liveliness=LivelinessPolicy.AUTOMATIC,
)
subscriber_qos = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    liveliness=LivelinessPolicy.AUTOMATIC,
)
compatibility, reason = qos_check_compatible(publisher_qos, subscriber_qos)
assert compatibility == QoSCompatibility.ERROR
```

创建端点时分别传入对应 QoSProfile。只将 subscriber 的 reliability 改为 BEST_EFFORT 后，此处配置检查应兼容；实际收到消息还要有正确域、话题、类型和执行器。

本例额外显式设置 liveliness，便于得到确定的配置检查结论。其他策略留为 SYSTEM_DEFAULT 时，检查器可能返回 WARNING，意思是仍有策略待确定；读 reason，不能直接把 WARNING 当作确定兼容。

CLI 默认配置可能按版本和端点适配，复现实验时显式指定，不凭 echo 碰巧收到就推断自己的 subscriber 配置也正确：

```bash
ros2 topic info /learn_ch2/joint_states --verbose
ros2 topic echo /learn_ch2/joint_states sensor_msgs/msg/JointState --qos-reliability best_effort --once
```

<a id="ex3"></a>

## 第 3 题

0.2 秒长回调占住执行线程，期间另一个回调无法执行；0.05 秒是就绪周期，无法凭空提供计算时间。具体执行次数与排队行为需观察，不能只按 1/0.2 给所有情形下结论。

一种结构：订阅回调仅验证并替换“最近一条状态”；独立工作线程/进程读取一致快照做计算；结果带来源时间和序号，使用前检查是否仍有效。对图像还可选择只处理最新帧。

先测处理耗时和消息年龄，再决定结构；加线程不能自动提升所有 Python 计算的吞吐。

<a id="ex4"></a>

## 第 4 题

同一个互斥组明确禁止两个回调并行；多线程执行器不会绕过这个约束。

可以用短锁保护“位置、时间戳、序号”一并替换和复制，计算在释放锁后进行。或用不可变消息快照与明确所有权交接，避免读到一半旧关节、一半新时间。

不要持锁等待服务/TF 或进行长计算。改成可重入后还要检查对象是否允许同时多次进入同一回调。

