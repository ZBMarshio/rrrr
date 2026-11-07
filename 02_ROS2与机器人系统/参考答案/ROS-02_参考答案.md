# ROS-02：提示与参考答案

[返回题目](../讲义/ROS-02_包启动与参数.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

生成的 setup.py 中保留原有安装信息，补对应入口：

```python
entry_points = {
    "console_scripts": [
        "state_source = trajectory_demo.state_source:main",
        "state_recorder = trajectory_demo.state_recorder:main",
    ],
}
```

这是传给 setup(...) 的 entry_points 配置片段，不是用这几行替换整个文件。setup.cfg 的脚本安装位置、resource 标记、package.xml 与包模块也需保留。

在自己的工作空间根目录：

```bash
colcon build --symlink-install --packages-select trajectory_demo
```

运行终端先 source ROS，再 source 该工作空间 install/setup.bash，然后：

```bash
ros2 pkg prefix trajectory_demo
ros2 pkg executables trajectory_demo
ros2 run trajectory_demo state_source --ros-args -r __ns:=/learn_ch2
```

src 保存源码；build 是中间构建内容；install 是可发现、可使用的安装结果；log 是构建日志。symlink-install 能减少部分源码改动后的复制，但新入口/资源与构建元信息变动仍应重建确认。

<a id="ex2"></a>

## 第 2 题

nodes.launch.py 的最小内容：

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package="trajectory_demo",
            executable="state_source",
            namespace="learn_ch2",
            output="screen",
        ),
        Node(
            package="trajectory_demo",
            executable="state_recorder",
            namespace="learn_ch2",
            output="screen",
        ),
    ])
```

源码位于包根的 launch/nodes.launch.py。setup.py 顶部导入 glob，并在原有 data_files 列表中增加：

```python
("share/" + package_name + "/launch", glob("launch/*.launch.py"))
```

这仍是列表项片段，需要原有 resource marker/package.xml 安装项。重建、重新 source 后运行：

```bash
ros2 launch trajectory_demo nodes.launch.py
```

节点名取决于源码和 launch 的 name/remap；namespace 相同且两端使用相对 joint_states 时，话题为 /learn_ch2/joint_states。若一端写了绝对 /joint_states，则不随该 namespace 变化。

<a id="ex3"></a>

## 第 3 题

构造函数中、创建 timer 前的片段：

```python
import math
from rcl_interfaces.msg import ParameterDescriptor

self.declare_parameter(
    "publish_hz", 10.0,
    ParameterDescriptor(read_only=True, description="startup publish rate [Hz]"),
)
hz = self.get_parameter("publish_hz").value
if not math.isfinite(hz) or hz <= 0.0:
    raise ValueError("publish_hz must be finite and positive")
self.timer = self.create_timer(1.0 / hz, self.publish_state)
```

它替换原例的固定 timer 创建，不能追加后保留两个 timer。双精度参数用 `5.0`，避免传入 int 类型 5 与声明不符。

```bash
ros2 run trajectory_demo state_source --ros-args -r __ns:=/learn_ch2 -p publish_hz:=5.0
ros2 param get /learn_ch2/state_source publish_hz
ros2 param describe /learn_ch2/state_source publish_hz
ros2 topic hz /learn_ch2/joint_states
```

前三条/第四条需要在合适的独立终端观察，topic hz 会持续运行，手动结束。测得频率受接收、调度和负载影响，不保证精确 5 Hz。

只读参数运行中应拒绝 set。去掉只读后若仅参数值变化，timer 仍是旧周期；需要另外实现更新逻辑才能承诺动态修改。

<a id="ex4"></a>

## 第 4 题

launch 设了 5.0、节点 get 仍 10.0：先查参数是否显式接到 Node(parameters=...)、启动的是哪份 launch、YAML 是否安装、节点完整名与键是否匹配、值类型是否正确。

get 已是 5.0、timer 仍旧：追到读取时刻、缓存变量、timer 创建/更新位置，也排查另一个同名发布者。

例如节点实际为 /learn_ch2/state_source，YAML 却写给 /other/state_source，覆盖不会按你的意图作用。正确节点范围示例：

```yaml
/learn_ch2/state_source:
  ros__parameters:
    publish_hz: 5.0
```

在 Python launch 中传入 launch argument，可显式使用 `ParameterValue(LaunchConfiguration("publish_hz"), value_type=float)`；需导入对应类并声明 argument。只创建 DeclareLaunchArgument 不会自动传参给节点。

