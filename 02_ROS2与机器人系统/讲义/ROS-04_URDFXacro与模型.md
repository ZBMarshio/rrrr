# ROS-04：机器人模型首先是一组坐标关系

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#ros-04) · [提示与答案](../参考答案/ROS-04_参考答案.md) · [TF2](ROS-05_TF2与坐标查询.md)

<a id="intro"></a>

## 导读

**为什么学这一节。** 机器人外观看起来正确，关节和工具坐标仍可能接错。URDF/Xacro表达的是机构关系，外观只是其中一部分。

**学完会有什么变化。** 从为了让模型显示而调整几何体，进到能区分link、joint、visual、collision与inertial，核对零位、轴和工具位置。

**接下来能做什么。** 可以搭出可验证的双关节描述，与[KIN-04](../../03_机器人学基础/讲义/KIN-04_正运动学FK.md#intro)的FK和[ROS-05](ROS-05_TF2与坐标查询.md#intro)的TF互相检查，再为规划和仿真提供模型。

## W04 的目标与资料

用 W03 的平面 2R 模型表达两段连杆，接收已有 JointState，核对 FK 与 TF。先用简单几何体。

| 官方资料 | 选读范围 |
|---|---|
| [URDF 与 robot_state_publisher 教程](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Intermediate/URDF/Using-URDF-with-Robot-State-Publisher-py.rst) | URDF 文件、状态输入、launch 与安装资源 |
| [robot_state_publisher README](https://github.com/ros/robot_state_publisher/blob/jazzy/README.md) | joint_states、robot_description、/tf 与 /tf_static 的职责 |
| [Jazzy 教程中的 URDF 专题](https://docs.ros.org/en/jazzy/Tutorials.html) | 按标题查 visual、joint、Xacro；动力学相关内容以后补 |

## link、joint、visual 分别表示什么

- link 定义一个刚体及其坐标系。
- joint 定义 parent/child 连接、零位关系、关节运动轴与约束。
- joint origin 指出零关节量时子坐标相对父坐标的关系；关节运动随后作用。
- visual origin 只放置外观几何体，不负责把下一个关节移到连杆末端。
- collision 与 inertial 服务碰撞和物理模型。只有 visual 的模型可以显示，不能因此认为物理参数已经完善。

本章取 L1=0.3 m、L2=0.2 m，转轴都沿 z：

```text
base_link -- joint_1(零位在基座) --> link1
link1 -- joint_2(零位沿 link1 的 x 平移 0.3 m) --> link2
link2 -- fixed tool_joint(沿 link2 的 x 平移 0.2 m) --> tool0
```

link2 的原点在第二关节处，tool0 才在第二段末端。把 link2 当作末端查询，是很常见的差一段长度的问题。

## 状态怎样让模型动起来

robot_state_publisher 读取 robot_description 中的模型，并订阅 joint_states；给定活动关节位置后，计算坐标变换。固定关节关系发布到 /tf_static，活动关节关系发布到 /tf。

命名空间为 learn_ch2 且使用相对 joint_states 时，状态输入为 /learn_ch2/joint_states。TF 的 frame_id 仍需按模型命名；不要以为加 namespace 就完成多机器人坐标隔离。

RViz 里固定坐标设 base_link；RobotModel 读取你的 robot_description 来源，检查 TF 与模型显示。具体显示配置按已安装版本操作。

## 要注意的细节

- 旋转位置用 rad，几何尺寸用 m；90 不代表 90°。
- joint axis 位于关节坐标中，不是随意写一个世界方向。
- 模型关节名必须与消息对应。多余或缺失名字不能靠数组长度“看起来是两个”判断。
- 关节零位、轴方向、几何中心分别检查。只移动 visual，通常不能修复 FK。
- 不同时给同一条状态输入接两个含义冲突的发布者；joint_state_publisher/GUI 与自己的 state_source 按目的选择。
- Xacro 用于复用和参数化，展开后的 URDF 才是理解结果的重要证据。
- 能通过 XML/URDF 检查，与能在 RViz 正确显示、能在动力学环境执行是不同验证。

## 练习

<a id="ex1"></a>

### 第 1 题：末端究竟是哪一个 frame？约 20 分钟

画出上述坐标链。q1=q2=0 时，link1、link2、tool0 相对 base_link 的位置分别是多少？

若 link1 的 visual origin 从 0.15 m 改为 0.2 m，joint_2 origin 仍是 0.3 m，tool0 的 FK 是否随之改变？说明原因。

<a id="ex2"></a>

### 第 2 题：关节名与单位错一次。约 20 分钟

模型关节名为 joint_1/joint_2，消息却是 joint1/joint2；另一组消息给 q1=90.0，原意是 90°。

分别预测模型与数值会怎样。先检查消息/模型约定，再在合成模型中修复；不把异常姿态发给真实执行接口。

<a id="ex3"></a>

### 第 3 题：自己建立最小 2R 模型并核对。约 45—60 分钟

创建 URDF 与启动入口，复用 W02 的合成 JointState。先做零位，再做 `(π/2,0)`、`(0,π/2)`，查询 base_link 到 tool0，与自己的 FK 比较。

验收：模型可解析；三组数值有对照；有 GUI 时再观察简单几何体，无 GUI 时保留数值证据。注意原发布者的常量需改成这些测试关节值。

<a id="ex4"></a>

### 第 4 题：把长度参数化，而不是只拉长外观。后续约 25 分钟

将 L1 提取为 Xacro property，从 0.3 改成 0.4 m。找出 visual 尺寸/中心与 joint_2 origin 中需要同步使用参数的位置。

展开到新 URDF 文件，检查零位 tool0 应变为多远。说明改变哪些字段只影响外观，哪些改变运动学。

## 直觉与回顾

先把模型看成一套带关节规则的坐标骨架，几何外观贴在骨架上。这样遇到“看起来很长，末端却没变”时，你会自然回头查连接关系。

你能从零位手画出骨架，再用一组非零角度核对，就已经在建立可解释的模型。复盘保留一个“外观正确但坐标错了”或相反的例子，写清证据。

