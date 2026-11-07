# ROS-06：提示与参考答案

[返回题目](../讲义/ROS-06_时间戳同步与时钟.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

```python
def stamp_to_ns(sec, nanosec):
    if not isinstance(sec, int) or not isinstance(nanosec, int):
        raise ValueError("stamp fields must be integers")
    if not 0 <= nanosec < 1_000_000_000:
        raise ValueError("nanosec out of range")
    return sec * 1_000_000_000 + nanosec
```

两条为 10.9e9 与 11.1e9 ns，间隔 200000000 ns，即 0.2 s。区间速度 [0.1,-0.2] rad/s。

倒序可能说明缓存顺序、时钟回拨或跨 episode；取绝对值会藏掉原因。此函数仅做字段算术，是否允许某时间范围/是否已初始化由上层约定检查。

<a id="ex2"></a>

## 第 2 题

A 收到 /clock 后使用约 12 s 的 ROS 时间，B 仍按其系统时间源。不能直接把二者时间戳相减解释网络延迟。

A 尚未初始化时应等待/拒绝依赖有效时间的处理。ROS 时间暂停，基于该时钟的 timer 也可能暂停；需要独立经过时间检查时可在节点中显式选择 steady clock。局部示意：

```python
from rclpy.clock import Clock, ClockType

self.steady_clock = Clock(clock_type=ClockType.STEADY_TIME)
self.watchdog_timer = self.create_timer(
    0.05, self.check_receive_timeout, clock=self.steady_clock,
)
```

这里 self 是已存在的节点，check_receive_timeout 由你实现。该检查仍需正确处理线程、数据与停止接口。

<a id="ex3"></a>

## 第 3 题

匹配状态索引依次为 0、2、3、None，差值约 0.02、0.03、0.03 s，最后一项最近也相差 0.17 s。

```python
def nearest_index(stamps_ns, query_ns, max_skew_ns):
    if max_skew_ns < 0:
        raise ValueError("max skew must be non-negative")
    if not stamps_ns:
        return None
    index = min(range(len(stamps_ns)), key=lambda i: abs(stamps_ns[i] - query_ns))
    if abs(stamps_ns[index] - query_ns) > max_skew_ns:
        return None
    return index
```

这是一小组数据的参考实现，输入是整数 ns 的普通列表。大数据用有序搜索或同步器优化；并明确时间相等、插值与重复使用样本的规则。

1.10 s 选择 1.13 s 体现离线可见未来；在线应等到该状态到达或采用只用过去样本的规则，再计入等待与偏差。

<a id="ex4"></a>

## 第 4 题

```python
def is_fresh(last_rx_ns, now_ns, max_age_ns):
    if max_age_ns <= 0:
        raise ValueError("max age must be positive")
    if last_rx_ns is None:
        return False
    elapsed = now_ns - last_rx_ns
    return 0 <= elapsed <= max_age_ns
```

还需检查采样时间及其时钟映射、消息序号/重复、字段有限性、帧/单位/关节契约、设备状态。持续收到重复旧帧可以满足接收活性，却仍不适合作为当前观测。

