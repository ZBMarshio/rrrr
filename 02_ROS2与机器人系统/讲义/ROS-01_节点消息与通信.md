# ROS-01：从一条消息看懂节点与通信

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#ros-01) · [提示与答案](../参考答案/ROS-01_参考答案.md) · [下一节](ROS-02_包启动与参数.md)

<a id="intro"></a>

## 导读

**为什么学这一节。** 系统里的数值如何从一个程序送到另一个程序，是读懂机器人代码的起点。先从一条消息看谁产生、谁接收以及格式是什么。

**学完会有什么变化。** 从把包名、类名、节点名和话题名混在一起，进到能画出通信关系，区分持续数据、一次请求与有过程反馈的任务。

**接下来能做什么。** 可以写最小状态发布/订阅节点，随后用[ROS-07](ROS-07_记录回放与复现.md#intro)记录回放，用[ROS-08](ROS-08_ros2_control与执行接口.md#intro)继续追踪动作执行。

## 目标与资料

W02 先完成发布订阅，能说明消息由谁产生、格式是什么、谁接收。服务与动作先理解语义、调用现成示例。

| 资料 | 选读范围 |
|---|---|
| [Jazzy 官方教程目录](https://docs.ros.org/en/jazzy/Tutorials.html) | Beginner CLI：Nodes、Topics、Services、Actions 的关系与常用检查 |
| [Python 发布订阅教程源文件](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.rst) | 类初始化、create_publisher/subscription、timer、spin、main |
| [JointState 官方定义](https://github.com/ros2/common_interfaces/blob/jazzy/sensor_msgs/msg/JointState.msg) | 名称与数组对应、可选字段、单位、采样时间 |

资料网页受限时读官方源文件；下面是自写小例子，不用先下载一整套人形机器人代码。

## 先分清几种“名字”

```python
class StateSource(Node):
    def __init__(self):
        super().__init__("state_source")
        self.pub = self.create_publisher(JointState, "joint_states", 10)
```

这是局部片段，Node 和 JointState 需要导入。StateSource 是 Python 类名；state_source 是传给 ROS 的节点名；joint_states 是相对话题名；self.pub 是 Python 属性；JointState 是消息类型。

节点是 ROS 图中的参与者，不要求“一节点一进程”；一个进程可以承载多个节点。同名字符串也可能出现在控制器配置里，判断含义要看上下文。

## 一个完整的合成状态发布节点

可在自己的练习目录保存为 state_source.py：

```python
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from sensor_msgs.msg import JointState

class StateSource(Node):
    def __init__(self):
        super().__init__("state_source")
        self.pub = self.create_publisher(JointState, "joint_states", 10)
        self.timer = self.create_timer(0.1, self.publish_state)

    def publish_state(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ["joint_1", "joint_2"]
        msg.position = [0.1, -0.2]
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = StateSource()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == "__main__":
    main()
```

在已经按学习指南设置好环境的练习终端运行：

```bash
/usr/bin/python3 state_source.py --ros-args -r __ns:=/learn_ch2
```

main 初始化 ROS → 构造对象并注册 publisher/timer → spin 让执行器处理回调 → 定时调用 publish_state → 发消息。定义回调函数不等于回调已经执行。

0.1 s 是定时器的期望周期，实际调度会受系统和回调影响。这里的时间戳代表合成样本的当前生成时刻。

## 话题、服务与动作分别承诺什么

| 方式 | 适合的交互 | 要检查什么 |
|---|---|---|
| Topic | 连续状态、图像、流式参考 | 来源、类型、频率、QoS、时间 |
| Service | 一次请求与一次响应，如查询或设置 | 服务存在、请求内容、响应含义 |
| Action | 较长任务，有目标、反馈、结果及取消协议 | 目标是否接受、执行状态、最终结果、取消结果 |

“发出调用”“目标被接受”“任务完成”是不同事件。Action 提供取消交互，但具体执行端如何停止仍由其实现和平台决定。

## 常见细节

- JointState 的 name 与各非空数组对应；velocity/effort 可以为空。不要把缺失速度补零并声称是实测静止。
- 本章旋转关节位置用 rad；伸缩关节的 position 可以是 m，要读模型。
- 名称列表顺序可以变化，消费者按名字映射；不要默认第 0 项永远是左侧某关节。
- 话题名相同还要检查类型、QoS 与发现环境；topic list 出现不表示已有有效数据。
- 多个发布者可向同一话题发消息，消费者可能看到混合来源。状态来源不明时先查 publisher 数量。
- 消息里的 header 不替你校准时钟；JointState 是状态描述，不是通用控制命令。

## 练习

<a id="ex1"></a>

### 第 1 题：把名字和调用顺序画出来。约 15 分钟

对上面的完整例子，写出类名、节点完整名、话题完整名、消息类型、定时回调名。说明去掉 spin 后会怎样。

另开同环境终端，用 node list、node info、topic info 与 interface show 检查。先预测，再记录实际结果。

<a id="ex2"></a>

### 第 2 题：按关节名字取值。约 25 分钟

实现 `positions_in_order(msg, expected_names)`。检查 name 不重复、position 与 name 等长、非空可选数组长度一致、数值有限；期望名称全部存在，返回期望顺序的新列表。

输入名字为 `["joint_2","joint_1"]`、位置为 `[-0.2,0.1]`，期望 `["joint_1","joint_2"]`。再验证缺关节、重复名字、长度不一致、NaN 与空 velocity。

<a id="ex3"></a>

### 第 3 题：自己写订阅与记录节点。约 40—60 分钟

参考官方 subscriber 模板，写 state_recorder，订阅 joint_states，调用第 2 题验证并保存名字、位置、消息采样时间与接收时间。

先收上面的合成常量，再把发布者改为读取第一章 CSV 的 q_obs 两列。四行可能在发现完成前就发完，先用持续发布/明确启动顺序检查，再设计一次有限序列发送。

验收：原数据来源清楚；至少一次故意坏消息被拒绝；修改一列只影响对应关节；订阅回调能较快返回。记录器完整代码由你组织。

<a id="ex4"></a>

### 第 4 题：选交互方式，并读一个结果。约 20 分钟

为连续图像、查询设备信息、执行十秒轨迹分别选择通信方式并说明原因。在独立练习环境可调用已安装的 AddTwoInts 示例服务；动作先读 FollowJointTrajectory 的 Goal/Result/Feedback，W11 再接模拟控制器。

回答：节点打印“goal accepted”能否当作轨迹已经到达的证据？你还会收集什么？

## 直觉与回顾

节点可以看成各自负责一件事的协作者，消息是交接的数据单。话题告诉你“哪类单据在流动”，字段、名字、单位和时间告诉你“这张单据究竟是什么意思”。

你看懂一条消息之后，再看复杂系统，先找生产者与消费者就有入口。复盘时试着不用命令名，而用“谁给谁什么信息、接收后做什么”讲一次链路。

