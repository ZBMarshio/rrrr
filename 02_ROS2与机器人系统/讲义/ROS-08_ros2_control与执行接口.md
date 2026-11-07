# ROS-08：把命令追到控制器、硬件接口与反馈

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#ros-08) · [提示与答案](../参考答案/ROS-08_参考答案.md) · [状态与停止](ROS-10_排错状态与停止条件.md)

<a id="intro"></a>

## 导读

**为什么学这一节。** 发布了一条轨迹，机器人为什么会动，状态又从哪里回来？把消息追到控制器和硬件接口，才能解释这个过程。

**学完会有什么变化。** 从把话题有数据当作执行成功，进到能画出命令、状态与资源关系，说明read/update/write各处理哪一层。

**接下来能做什么。** 可以阅读模拟硬件与控制器配置，结合[CTRL-03](../../04_机器人控制与运动规划/讲义/CTRL-03_控制接口与执行链.md#intro)核对位置、速度或力矩接口，再接规划器或学习策略。

## 本节放在 W11

先有状态、模型、轨迹与基础控制，再阅读/运行官方 RRBot 模拟硬件。这里形成接口理解，不从零写实际电机驱动。

| 官方资料 | 选读范围 |
|---|---|
| [ros2_control 架构](https://control.ros.org/jazzy/doc/getting_started/getting_started.html) | Controller Manager、Resource Manager、硬件组件与 read/update/write |
| [RRBot Example 1](https://control.ros.org/jazzy/doc/ros2_control_demos/example_1/doc/userdoc.html) | 启动、列接口/控制器、forward position、JTC；以本版参数为准 |
| [Jazzy RRBot 硬件源码](https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_1/hardware/rrbot.cpp) | 初始化、read、write，辨认演示状态如何更新 |
| [JTC 官方文档](https://control.ros.org/jazzy/doc/ros2_controllers/joint_trajectory_controller/doc/userdoc.html) | 支持的接口、轨迹话题/动作、反馈与完成 |
| [JointTrajectoryPoint](https://github.com/ros2/common_interfaces/blob/jazzy/trajectory_msgs/msg/JointTrajectoryPoint.msg) | positions 等字段的顺序、单位与 time_from_start |

RRBot 演示包本次未安装，不能把下面的运行目标标为已验证。到 W11 选择匹配 Jazzy 的包/源码与已知模拟配置；本章不自动安装或启动实验室驱动。

## 先画三条关系

```text
启动/配置：
launch → 机器人描述 + ros2_control 描述 + 控制器参数 → controller_manager/插件

命令：
应用 → 控制器话题/动作入口 → 控制器更新 → command interface → 硬件 write/驱动

反馈：
设备/模拟状态 → 硬件 read → state interface → joint_state_broadcaster → JointState
```

控制循环的概念顺序是 read → controller update → write。话题回调、实时缓冲和硬件周期如何衔接，需看实际控制器实现，不能把收到消息等同于电机已经执行。

## 几个角色的区别

| 角色 | 负责什么 |
|---|---|
| controller_manager | 管理控制器/接口并组织更新循环 |
| Resource Manager / 硬件组件 | 加载插件、管理硬件生命周期和接口，执行读写 |
| JointStateBroadcaster | 将状态接口内容发布为状态消息 |
| ForwardCommandController | 按已配置接口转发命令，关注顺序与类型 |
| JointTrajectoryController | 处理带时间的轨迹及相应反馈/动作协议，行为依接口与配置而定 |

位置、速度、力矩命令的单位和底层控制不同。位置 command interface 下，软件向硬件提供期望位置，实际闭环可能在驱动器中；不能因此认定上层 JTC 做了某套力矩控制。

## 模拟硬件能说明什么

有的 mock 将命令映射回状态；RRBot 示例源码还可用简化的状态逼近规则。它们用于理解接口和控制器，不是被测机构真实惯性、摩擦和接触模型。

状态 topic 出现、动作目标接受、控制器报告完成、真实末端完成任务，分别需要对应证据。time_from_start 给出参考到达时刻，物理可达性与实际跟踪仍受系统限制。

## 练习

<a id="ex1"></a>

### 第 1 题：从配置找到每个角色。约 25 分钟

阅读 RRBot 对应 launch、控制器 YAML、模型中的 ros2_control 和硬件插件，标出谁决定关节顺序、命令类型、控制周期和驱动实现。

初期可只做源文件阅读；运行时另外保存 controller 状态与接口输出，明确这两类证据。

<a id="ex2"></a>

### 第 2 题：两个数字发给哪两个关节？约 20 分钟

假设某 forward position 配置的 joints 顺序为 [joint2,joint1]，收到 data=[0.4,-0.2]。分别哪个关节收到哪个值？

同样目标改用 JointTrajectory 时，joint_names 和 positions 应怎样对应？说明为何一个裸数组与一个带名字的接口有不同的映射检查。

<a id="ex3"></a>

### 第 3 题：构造并检查一条小轨迹。约 30 分钟

创建 JointTrajectory，两个关节，两点位置分别在 1 秒、2 秒到达。自己写验证函数：名字与要求的关节集合一致、不重复；位置长度和顺序正确；数值有限；非空可选数组等长；首点时间大于零且后续严格递增。

这是本工具采用的简化输入约定，不代表 JTC 所有允许格式。只在本机消息对象上验证；发送需等你明确启动的 RRBot 模拟环境。

<a id="ex4"></a>

### 第 4 题：到 W11 再运行与排错。约 40—60 分钟

在独立练习 domain 中运行官方 RRBot，列控制器/硬件接口。沿教程选择一种命令入口，记录目标与反馈，说明当前是 forward 还是轨迹控制。

检查一次 inactive、未正确 claim 接口或关节名不匹配的模拟故障。只在演示配置中调整，保留原基线；没有演示包时先做配置/消息题，运行项待补。

## 直觉与回顾

可以把“我要到这里”与“实际如何让机构到这里”分成多张交接单。控制器把轨迹解释成合适的参考，硬件接口把参考交给设备，反馈再告诉上层实际状态。

追链路时每跨一层都问：这里传的量、单位、频率和完成含义是什么？复盘用一次自己的目标请求，画到状态回来，再说明哪一段目前只在模拟中验证。

