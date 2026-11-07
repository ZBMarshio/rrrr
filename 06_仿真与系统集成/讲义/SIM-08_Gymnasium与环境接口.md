# SIM-08：先定义环境，再选择学习算法

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#sim-08) · [提示与答案](../参考答案/SIM-08_参考答案.md)

<a id="intro"></a>

## 导读

**为什么学这一节。** 学习算法只能通过环境交互接口认识任务。观测、动作、奖励和结束条件怎样定义，会直接决定它实际学的是什么。

**学完会有什么变化。** 从把step当推进一次画面，进到能解释环境一步、空间范围、复位与终止/截断，并将任务成功和奖励分开。

**接下来能做什么。** 可以手工核对一个标准环境，再为[RL-02](../../08_机器人学习与具身智能/导读.md#rl-02)、[RL-03](../../08_机器人学习与具身智能/导读.md#rl-03)或BC滚动提供可检查的交互与评测入口。

## 资料与范围

第三阶段 IL/RL 前使用。[Gymnasium Env API](https://gymnasium.farama.org/api/env/)、[自定义环境教程](https://gymnasium.farama.org/introduction/create_custom_env/)和[时间限制说明](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)是主资料。

先手工跑通接口和评测，不在本章训练 PPO/SAC。可用标准 [Pendulum-v1](https://gymnasium.farama.org/environments/classic_control/pendulum/)练 API，理解后再考虑包装自己的后端。

## 一次交互包含什么

reset(seed=...) 返回 observation、info；step(action) 返回 observation、reward、terminated、truncated、info。episode 结束后按 API 复位，不继续把新动作送进已结束的一局。

observation_space/action_space 约定形状、dtype 和范围。观测可以只包含部分状态；若任务需要速度、目标或时间信息，应说明是否可观测，不能仅靠 action 数组大小猜任务。

环境一步可能保持动作并推进多个物理步。例如 h=0.001 s、frame_skip=10，环境步长为 0.01 s。改变 frame_skip 会改变交互频率与任务条件。

## 奖励和成功分开

reward 是学习信号，任务成功需要独立判据。可以有距离奖励，但成功还要求位置/速度/保持时长，甚至物体最终状态。奖励变高不自动等于任务完成。

## 终止和截断为什么要区分

terminated 表示任务定义中的终端状态；truncated 表示任务外部限制等使轨迹被截断。本节将预定成功/失败定义为任务终端，将外部步数上限定义为截断。

rollout 遇到任一结束都停止；在相应价值学习假设和有效终止前观测下，bootstrap 掩码通常由 terminated 决定。不能把 done=terminated or truncated 直接当 bootstrap 掩码。

真正有限时域任务可能需要把剩余时间放进观测；自动重置/向量环境要按版本取得结束前观测，不能拿下一局的首帧替代。无效观测或通信故障也不应盲目当成可训练的正常截断转移。

## 练习

<a id="ex1"></a>

### 第 1 题：无渲染手工 rollout。约 25 分钟

建立 Pendulum-v1、g=9.81，设置一个短外部步数上限。固定 seed 与零力矩序列，检查 reset/step 的返回数量、space.contains 和最后的 flags，复位后复跑。

它的动作和三维观测各表示什么？不能把它当作本章单转子的同一模型。

<a id="ex2"></a>

### 第 2 题：归一化动作接什么物理量？约 20 分钟

把 [-1,0,1] 映到对应执行器范围 [-2,2]，明确输出单位。输入超出 [-1,1]、shape 或 dtype 不合时如何处理？

<a id="ex3"></a>

### 第 3 题：结束标志与价值目标。约 25 分钟

r=1、gamma=0.99、V_next=10，分别求普通转移、真正终止、外部时间截断的简单 bootstrap 目标。

再规定“到达和外部上限同一步发生”时自己的标志优先级，并解释框架中也可能同时出现两个 True。

<a id="ex4"></a>

### 第 4 题：设计环境卡片。约 30 分钟

为后续任务写观测、动作、时间尺度、初态、目标、reward、成功/失败、终止/截断、复位与 info。先用手工动作验证，再决定是否包装成 Env。

自建环境后可用官方 check_env 检查接口；接口通过仍不证明任务定义或奖励合理。

## 直觉与回顾

学习算法看到的是你定义的环境。观测漏了信息、动作单位错了、复位带着旧状态，算法再复杂也在解决另一个问题。

复盘画一条真实转移：动作从何时开始保持，推进了多少物理时间，下一观测与奖励来自哪个状态？

