# 仿真与系统集成

[返回总入口](../README.md) · [总知识网络](../总知识网络.md) · [重要知识索引](知识索引.md) · [具体学习指南](学习指南.md) · [练习与复盘](练习与复盘记录.md)

版本：2026-10-30 · 已展开 10 节讲义、40 道练习、独立答案、3 个 MJCF 模型、4 张图示与核对记录。基础仿真从 W07 使用，集成按 P1/P2 阶段推进，RL 环境和双臂扩展按选题深入。

提供可中断、可复跑的机器人实验环境，并把模型、规划、感知和执行接口接通。

<a id="chapter-intro"></a>

## 本章导读

**为什么学这一章。** 设备时间有限时，仿真让你持续推进实验；模块越来越多时，集成则决定它们能否一起工作。这章关心怎样建立可复位、可记录、能解释失败的实验系统。

**学完会有什么变化。** 学习前，可能主要依据模型有没有动来判断成功；学习后，你能说明模型、状态、执行器、时钟与接口怎样对应，并判断一项结果来自哪一层验证。

**接下来能做什么。** 可以复用已有运动学、控制和视觉成果，逐步接通P1/P2；再为IL/RL准备环境接口与固定评测。先让简单后端可靠，再按问题增加物理或真实设备。

## 学习内容与掌握层次

| 层次 | 内容 |
|---|---|
| 必须掌握 | MuJoCo 模型、状态/控制量、执行器、步长、复位与接触基础；MoveIt 规划组、场景、碰撞与执行；关节顺序、单位、零位、时钟一致性；日志与评测入口。 |
| 了解即可 | URDF/MJCF 差异、模型参数误差、域随机化、双臂规划与环境封装。 |
| 以后深入 | 模型辨识、复杂接触、并行仿真、仿真到真机迁移、系统性能和部署。 |

## 前置与衔接

- 前置：基础仿真只需 01；系统集成逐步引入 02、03、04、05 的必要内容。
- 去向：为 08 的数据生成、闭环评测和 RL 交互环境提供条件；后续按需要迁移真机。
- 层次表示毕业前与研一的深度边界；先通过小练习检查，已掌握的部分跳过。

<a id="route"></a>

## 学习路线

1. 第一阶段就加载一个简单 MuJoCo 模型，读取状态、发送动作、复位并记录结果。
2. 分别跑通 MoveIt 规划接口和仿真动态执行，核对各自模型与命令语义。
3. 按项目接通最小桥接接口，集成视觉操作；第三阶段封装重复评测或 RL 环境。

## 理论、代码与可验收成果

| 类型 | 当前要求 |
|---|---|
| 理论学习 | 理解可视化、接口模拟与物理仿真的验证边界，以及状态、动作和时间契约。 |
| 代码实践 | 实现仿真循环、复位/记录脚本、必要适配接口；选择标准环境后再考虑自建环境。 |
| 小项目/验收 | 固定初始条件下可复跑的目标到达或抓放任务，包含异常处理和结果记录。 |

无真机替代：本方向本身就是真机替代路径；普通电脑优先简单场景、小模型和较少并行环境。

成果尽量复用到总路线的项目版本中；运行成功、指标验证和硬件验证分别记录。

从[学习指南](学习指南.md)选择当周范围；[图示说明](图示/README.md)给出模型/控制/时间条件；[示例核对记录](示例核对记录.md)区分实际无界面 MuJoCo/Gymnasium 验证与尚未运行的框架/真机部分。

<a id="resources"></a>

## 参考资料

资料用于按问题查阅。先选一条主资源线，扩展材料在需要时打开；文档与安装版本对应。

| 编号 | 资料入口 | 用法 |
|---|---|---|
| <a id="r1"></a>R1 | [MuJoCo 3.17 Python](https://mujoco.readthedocs.io/en/3.17.0/python.html)、[XML](https://mujoco.readthedocs.io/en/3.17.0/XMLreference.html) | 模型/数据、状态/执行器、step/reset、查看器；匹配本次核对版本。 |
| <a id="r2"></a>R2 | [MoveIt 模型](https://moveit.picknik.ai/main/doc/examples/urdf_srdf/urdf_srdf_tutorial.html)、[场景](https://moveit.picknik.ai/main/doc/examples/planning_scene/planning_scene_tutorial.html)、[执行接口](https://moveit.picknik.ai/main/doc/examples/controller_configuration/controller_configuration_tutorial.html) | main 为 Rolling，实际使用选择与 Jazzy 匹配的模型/配置和示例。 |
| <a id="r3"></a>R3 | [Jazzy ros2_control 架构](https://control.ros.org/jazzy/doc/getting_started/getting_started.html)、[mock](https://control.ros.org/jazzy/doc/ros2_control/hardware_interface/doc/mock_components_userdoc.html) | 硬件抽象、read/update/write 与模拟反馈的边界，复用第二章。 |
| <a id="r4"></a>R4 | [Gymnasium Env API](https://gymnasium.farama.org/api/env/)、[时间限制](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/) | reset/step、空间、terminated/truncated；本次核对版本 1.4.0。 |
| <a id="r5"></a>R5 | [Gymnasium-Robotics](https://robotics.farama.org/)、[Dynamics Randomization 作者项目](https://xbpeng.github.io/projects/SimToReal/index.html) | 后续选择标准机器人任务或阅读迁移实验；本章未运行该机器人任务库/策略训练。 |

## 临时需要时怎么学

先到[知识索引](知识索引.md)找到问题 → 只补该行的最低前置 → 做最小验证 → 回到当前任务。涉及其他方向的知识编号可以直接点击。

