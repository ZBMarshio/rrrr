# ROS-08：提示与参考答案

[返回题目](../讲义/ROS-08_ros2_control与执行接口.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

launch 决定启动哪些组件、传哪些描述与配置；YAML 决定控制器类型、所需关节/接口和相关参数；ros2_control 描述声明硬件插件及状态/命令接口；插件实现实际读写。

更新频率可能有 manager、控制器与硬件组件多个层面，先读当前配置与实现。更新率参数不等于每个周期都按时完成。

当前 Jazzy 示例的部分名字通过 joint_prefix 参数生成，阅读展开后的配置更直接。RRBot read 中的简化逼近规则不是编码器测量；不要把日志中的 state 一律称为实测。

<a id="ex2"></a>

## 第 2 题

forward 裸数组按配置顺序解释：joint2 得 0.4 rad，joint1 得 -0.2 rad。数组本身没有关节名。

JointTrajectory 可以写 joint_names=[joint2,joint1]、positions=[0.4,-0.2]，或者相反顺序同时相应重排位置。名称映射需与具体控制器支持和关节集合约定一致，不能只换名字不换数值。

<a id="ex3"></a>

## 第 3 题

先在本机构造，不发送：

```python
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

trajectory = JointTrajectory()
trajectory.joint_names = ["joint1", "joint2"]
trajectory.points = [
    JointTrajectoryPoint(
        positions=[0.1, -0.1], time_from_start=Duration(sec=1),
    ),
    JointTrajectoryPoint(
        positions=[0.2, 0.0], time_from_start=Duration(sec=2),
    ),
]
```

一个简化验证函数：

```python
import math

def validate_trajectory(msg, required_names):
    names = list(msg.joint_names)
    if not names or len(set(names)) != len(names):
        raise ValueError("empty or duplicate trajectory joints")
    if set(names) != set(required_names) or len(names) != len(required_names):
        raise ValueError("trajectory joint set mismatch")
    if not msg.points:
        raise ValueError("empty trajectory")
    previous_ns = 0
    for point in msg.points:
        if len(point.positions) != len(names):
            raise ValueError("positions length mismatch")
        for field in ("positions", "velocities", "accelerations", "effort"):
            values = list(getattr(point, field))
            if values and len(values) != len(names):
                raise ValueError(f"{field} length mismatch")
            if not all(math.isfinite(float(v)) for v in values):
                raise ValueError(f"non-finite {field}")
        duration = point.time_from_start
        if not 0 <= duration.nanosec < 1_000_000_000:
            raise ValueError("invalid trajectory nanoseconds")
        current_ns = duration.sec * 1_000_000_000 + duration.nanosec
        if current_ns <= previous_ns:
            raise ValueError("point times must start positive and increase")
        previous_ns = current_ns
    return True
```

此函数未覆盖所有 JTC 组合约束、限位、速度/加速度可行性、header 起点和执行容差。输入检查通过后仍要根据实际接口验证，不直接当作可执行保证。

<a id="ex4"></a>

## 第 4 题

先检查包是否存在：

```bash
ros2 pkg prefix ros2_control_demo_example_1
```

包与依赖准备好、确认是官方模拟配置后，按教程启动 RRBot；可先查 --show-args。运行后检查：

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
ros2 topic info /joint_states --verbose
```

若 manager 在命名空间下，CLI 使用对应 controller_manager 路径，按本机 --help 指定。不要为了让命令有响应而连接实验室正在运行的 manager。

故障检查顺序：目标 manager/控制器是否正确 → 生命周期是否 active → 所需命令接口是否 available/claimed、是否被其他控制器占用 → 名称/类型/话题或动作 → 实际输入和反馈。

需要切换 forward 与轨迹控制时按当前版本教程处理接口占用，不能让两个控制器无意争用同一命令接口。运行报告写清：模型、插件、控制器、入口、目标、反馈、完成判据和未验证的物理性能。

