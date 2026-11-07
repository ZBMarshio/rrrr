# ROS-07：提示与参考答案

[返回题目](../讲义/ROS-07_记录回放与复现.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

话题应是你实际记录的 /learn_ch2/joint_states，类型 sensor_msgs/msg/JointState。指定 sqlite3 时通常有 metadata.yaml 与对应数据库文件；使用其他插件时格式不同，以 info 为准。

消息数没有预填答案。记录器开始发现/订阅的时机、实际发布周期、QoS/负载、开始与停止边界都可能影响数量。

不存在的话题不会凭空产生数据；保留录制端日志与 info 的实际输出。若没有有效 bag 可读，也记录失败，不填写预期条数。

<a id="ex2"></a>

## 第 2 题

先用 topic info --verbose 确认原源已退出、当前发布者是回放。比较 header stamp、name、position，浮点按声明容差；记录本次接收时刻。

为避免混入原话题，还可在个人练习中重映射回放：

```bash
ros2 bag play bags/w02_states --remap /learn_ch2/joint_states:=/learn_ch2/replay/joint_states
```

同时让记录器订阅对应新话题，例如在原订阅完整名上做相同 remap。这样仍需先确认名称解析，不能只改 player 而忘掉消费者。

对消息一条条比对前，先核对实际数量与顺序。有丢失时先定位原因，再决定是否能进行同样的统计比较。

<a id="ex3"></a>

## 第 3 题

A：同一话题有多个来源，状态可能交错。关闭原源，或明确分话题比较。

B：同一条 TF 边可能由回放和模型重复提供。可选“回放 JointState + 当前固定版本模型重新算 TF”，或“回放已有 TF + 不启动重复 broadcaster”。检查静态边是否完整。

C：先统一数据、TF 与节点时钟。例如回放：

```bash
ros2 bag play bags/w02_states --clock 50
```

并让相关消费者/模型节点使用 use_sim_time=true，确认它们实际接到 /clock。这个例子 bag 只有状态时，需要匹配版本的模型重新算 TF；不是加 --clock 就自动产生缺失变换。

<a id="ex4"></a>

## 第 4 题

理想调度墙钟间隔约 0.05 秒，消息 header 间隔仍 0.1 秒。实际接收还受计算/传输影响。不能把收到消息的墙钟频率当成原始采样频率。

一份复现清单至少有：bag 身份/话题/插件/数量、代码版本与 dirty 状态、节点/launch 参数、模型与标定版本、frame/关节/单位、clock/use_sim_time、回放速率与 remap、启动/停止顺序、成功与失败规则。

如果实验依赖重置内部状态、随机种子或物理初始条件，也要记录。状态回放本身不重建设备内部执行过程。

