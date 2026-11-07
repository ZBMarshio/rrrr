# ROS-01：提示与参考答案

[返回题目](../讲义/ROS-01_节点消息与通信.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

类名 StateSource；按题目命名空间运行后，节点 /learn_ch2/state_source，话题 /learn_ch2/joint_states；类型 sensor_msgs/msg/JointState；回调 publish_state。

注册 timer 后需要执行器处理就绪事件；直接去掉 spin 并退出，不能期待定时发布。没有命名空间参数时，相对话题通常解析到 /joint_states。

```bash
ros2 node list --no-daemon
ros2 node info /learn_ch2/state_source
ros2 topic info /learn_ch2/joint_states --verbose
ros2 interface show sensor_msgs/msg/JointState
```

CLI 本身也可能创建临时节点。实际图中节点数量不要求恰好只有一个，先识别各来源。

<a id="ex2"></a>

## 第 2 题

提示：先验证一张消息，再按名称取值，不原地重排。

```python
import math

def positions_in_order(msg, expected_names):
    names = list(msg.name)
    if not names or len(names) != len(set(names)):
        raise ValueError("empty or duplicate joint names")
    if len(msg.position) != len(names):
        raise ValueError("position/name length mismatch")
    for field in ("position", "velocity", "effort"):
        values = list(getattr(msg, field))
        if values and len(values) != len(names):
            raise ValueError(f"{field} length mismatch")
        if not all(math.isfinite(float(v)) for v in values):
            raise ValueError(f"non-finite {field}")
    if len(expected_names) != len(set(expected_names)):
        raise ValueError("duplicate expected names")
    by_name = dict(zip(names, msg.position))
    missing = set(expected_names) - by_name.keys()
    if missing:
        raise ValueError(f"missing joints: {sorted(missing)}")
    return [float(by_name[name]) for name in expected_names]
```

题目正常结果为 `[0.1,-0.2]`。这里只要求 position 必须存在，velocity/effort 允许为空；这是本工具的输入约定。JointState 通用定义本身允许数组为空，其他消费者可以有不同约定。

<a id="ex3"></a>

## 第 3 题

订阅回调的局部结构可以是下面这样，需要你先创建 node、文件 writer、expected_names，并导入第 2 题函数：

```python
def on_state(self, msg):
    received_ns = self.get_clock().now().nanoseconds
    try:
        positions = positions_in_order(msg, self.expected_names)
    except ValueError as exc:
        self.get_logger().warning(f"rejected state: {exc}")
        return
    stamp_ns = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
    self.writer.writerow([stamp_ns, received_ns, *positions])
```

收到时间和消息时间只有在同一时钟域下才可解释差值。真实设备采样时间不应被订阅者直接替换为 now。

完整验收：发布者/记录器分别可启动；保存的数据按名字对齐；正常退出时文件被关闭；坏输入有原因；长时间 I/O 或绘图不阻塞高频回调。短练习可直接写小 CSV，重计算和批量绘图放到节点外。

消息流可能丢失，不能只凭发布者“发了四条”就认定录到了四条。先观察连接和实际条数，再讨论启动、QoS 与记录顺序。

<a id="ex4"></a>

## 第 4 题

连续图像用话题；查询用服务；有持续执行、反馈、结果的轨迹任务适合动作。具体系统也可能用话题流式下发命令，需按协议明确完成与停止含义。

仅在安装了 demo_nodes_cpp 的独立练习环境启动：

```bash
ros2 run demo_nodes_cpp add_two_ints_server
```

另一个相同练习环境的终端：

```bash
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 2, b: 3}"
ros2 interface show control_msgs/action/FollowJointTrajectory
```

算术服务预期 sum 为 5。若包未安装，先完成接口阅读，不去调用含义不明的实验室服务。

goal accepted 只说明服务端接受目标。还应观察反馈、最终状态/result、实际关节反馈和任务定义；软件返回成功的适用范围也取决于执行端与反馈来源。

