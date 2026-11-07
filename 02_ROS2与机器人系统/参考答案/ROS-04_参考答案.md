# ROS-04：提示与参考答案

[返回题目](../讲义/ROS-04_URDFXacro与模型.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

零位时：link1 原点为 (0,0,0)，link2 原点为 (0.3,0,0)，tool0 为 (0.5,0,0)。只修改 visual origin 不改变关节坐标链，所以 tool0 的 FK 不变。

图像上箱体偏移不等于连杆坐标已经移动。问“这个 origin 属于哪个 XML 元素”比笼统说“改 origin”更明确。

<a id="ex2"></a>

## 第 2 题

名字不匹配时，模型无法按你的意图更新对应活动关节；具体日志/缺失 TF 表现随输入和版本观察。修复消息中的名字或有依据地映射到模型名，不是简单按下标猜测。

90 rad 约为 5156.6°，不是 90°；90° 应为 π/2 rad。URDF 声明限位不等于所有状态发布者/RViz 都会替你修正坏数据，先在输入边界验证。

<a id="ex3"></a>

## 第 3 题

下面是一份用于核对的完整最小 URDF。建议先自己写，再比较连接和偏置；它只包含显示与运动学需要的内容：

```xml
<?xml version="1.0"?>
<robot name="learning_two_r">
  <link name="base_link"/>
  <link name="link1">
    <visual>
      <origin xyz="0.15 0 0"/>
      <geometry><box size="0.3 0.03 0.03"/></geometry>
    </visual>
  </link>
  <link name="link2">
    <visual>
      <origin xyz="0.1 0 0"/>
      <geometry><box size="0.2 0.025 0.025"/></geometry>
    </visual>
  </link>
  <link name="tool0"/>
  <joint name="joint_1" type="revolute">
    <parent link="base_link"/><child link="link1"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.141592653589793" upper="3.141592653589793" effort="1" velocity="1"/>
  </joint>
  <joint name="joint_2" type="revolute">
    <parent link="link1"/><child link="link2"/>
    <origin xyz="0.3 0 0" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.141592653589793" upper="3.141592653589793" effort="1" velocity="1"/>
  </joint>
  <joint name="tool_joint" type="fixed">
    <parent link="link2"/><child link="tool0"/>
    <origin xyz="0.2 0 0" rpy="0 0 0"/>
  </joint>
</robot>
```

保存为你自己的 two_r.urdf 后可运行 `check_urdf two_r.urdf`。launch 中读取实际文件，并添加 robot_state_publisher 节点；示例局部：

```python
robot_xml = urdf_path.read_text(encoding="utf-8")
model_node = Node(
    package="robot_state_publisher",
    executable="robot_state_publisher",
    namespace="learn_ch2",
    parameters=[{"robot_description": robot_xml}],
    output="screen",
)
```

此处 Node 是 launch_ros.actions.Node，urdf_path 是你已解析的 Path；把 model_node 加入 LaunchDescription。安装 URDF 资源，并从包 share 找文件，避免依赖启动目录。

参考 FK：

```python
import math

def tool_xy(q1, q2, l1=0.3, l2=0.2):
    return (
        l1 * math.cos(q1) + l2 * math.cos(q1 + q2),
        l1 * math.sin(q1) + l2 * math.sin(q1 + q2),
    )
```

三组位置为 (0.5,0)、(0,0.5)、(0.3,0.2)，z=0。位置容差可先设 1e-6 m 用于这组理想数值对照；这不是实机精度承诺。

状态源与模型启动后，在相同练习环境查询：

```bash
ros2 run tf2_ros tf2_echo base_link tool0
```

若只显示固定边而缺少活动边，先查 joint_states、名字、时间与模型输入；不要先去改 TF 查询方向。

<a id="ex4"></a>

## 第 4 题

在实际 robot 根元素声明 `xmlns:xacro="http://www.ros.org/wiki/xacro"`，加入：

```xml
<xacro:property name="l1" value="0.3"/>
```

对应位置改为 Xacro 表达式：link1 box 长度 `${l1}`，其 visual origin x 为 `${l1/2}`，joint_2 origin x 为 `${l1}`。这些是嵌入完整模型的片段，不能单独作为 URDF 文件。

```bash
xacro two_r.urdf.xacro > two_r.expanded.urdf
check_urdf two_r.expanded.urdf
```

l1 改为 0.4 后，零位 tool0=(0.6,0,0)。展开文件中同时查看几何尺寸和 joint origin，确认参数真的进入了运动学链。

