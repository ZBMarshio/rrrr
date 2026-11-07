# ROS-05：TF 查询先写方向，再写代码

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#ros-05) · [提示与答案](../参考答案/ROS-05_参考答案.md) · [时间](ROS-06_时间戳同步与时钟.md)

<a id="intro"></a>

## 导读

**为什么学这一节。** 相机里识别到的位置，要先变到机器人使用的坐标系才能继续动作。TF2让这些带时间的坐标关系能被查询和复合。

**学完会有什么变化。** 从凭参数名字猜变换方向，进到能写清输入坐标、目标坐标和时刻，再用已知点核对查询结果。

**接下来能做什么。** 可以把传感器点变到基座，衔接[VIS-06](../../05_机器人感知与视觉/讲义/VIS-06_手眼标定与坐标闭合.md#intro)的手眼关系和视觉到达流程，也能定位差一个工具偏置的问题。

## 目标和资料

W04 先能核对 base_link 到 tool0；第二阶段把同样方法用于相机与目标。

| 官方资料 | 选读范围 |
|---|---|
| [TF2 Python listener](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Intermediate/Tf2/Writing-A-Tf2-Listener-Py.rst) | Buffer、TransformListener、target/source、Time() 与异常 |
| [Jazzy Buffer 实现与 API 注释](https://github.com/ros2/geometry2/blob/jazzy/tf2_ros_py/tf2_ros/buffer.py) | lookup_transform 参数方向、时间与等待；按对应函数定位 |
| [REP-103](https://github.com/ros-infrastructure/rep/blob/master/rep-0103.rst) | 米/弧度、右手系、相机 optical frame |
| [robot_state_publisher](https://github.com/ros/robot_state_publisher/blob/jazzy/README.md) | 哪些坐标边由模型与状态产生 |

## 把约定写在纸上

`T_A_B` 表示把 B 坐标下的量变换到 A 坐标下：

```text
p_base = T_base_camera × p_camera
T_base_target = T_base_camera × T_camera_target
```

查询 `lookup_transform("base_link", "camera_optical", stamp)`，返回用于把 camera_optical 中的量变到 base_link 的变换。第一个是目标坐标，第二个是输入坐标，不要按字符串读成“从 base 到 camera”。

TransformStamped 的 header.frame_id 是 parent/目标参考，child_frame_id 是子坐标；其中平移和旋转给出子坐标在父坐标中的关系。用一个已知点实际验证方向，比只背“正变换/逆变换”可靠。

## Buffer 与 Listener 的职责

Listener 接收 TF 消息；Buffer 保存带时间的关系并查询。查询可能需要沿多条边复合。

`Time()` 的零时间在 TF 查询中表示取最新可用关系；动态图中它不一定是当前系统时间，更不自动等于某张图像的采集时刻。

静态边与动态边分别对待。一个 child 应有明确 parent 和权威来源；模型节点、回放和手写 broadcaster 重复发布同一条边，会让来源难以解释。

## 容易踩的细节

- ROS 消息四元数通常按 x,y,z,w 字段，其他库可能用 w,x,y,z；查看接口，验证归一化。
- frame_id 不是节点名，也不会自动跟随 ROS namespace 改名。
- 相机 optical 轴通常 x 向右、y 向下、z 向前，区别于常见机器人机体坐标；明确发布相应变换。
- TF 树连通只证明有路径；数值、单位、方向和时间仍需核对。
- TF 未到、帧名错误、时钟不一致、请求时刻超出缓存，各有不同证据。不要全部改成 latest 掩盖。
- 回调中阻塞等待 TF，可能占住接收 TF 所需的执行线程。先用非阻塞查询或合理异步/缓存结构，按 ROS-03 理解。

## 练习

<a id="ex1"></a>

### 第 1 题：用一句话说明查询方向。约 15 分钟

解释这两条分别返回什么、可用于转换哪种输入：

```python
tf_buffer.lookup_transform("base_link", "camera_optical", stamp)
tf_buffer.lookup_transform("camera_optical", "base_link", stamp)
```

若你有相机坐标下的目标点，应该选哪条？并说明返回变换本身与把它应用到点是两个动作。

<a id="ex2"></a>

### 第 2 题：手算一组变换与逆。约 25 分钟

相机在基座坐标中的平移是 (1,0,0.5) m，相对基座绕 z 正转 90°。相机中的点为 (1,0,2) m。

写 T_base_camera，算点的基座坐标，再用逆变换算回相机坐标。给出对应四元数 x,y,z,w，并用数值程序核对。

<a id="ex3"></a>

### 第 3 题：最新变换能不能替代采集时刻变换？约 20 分钟

一张图采于 t=10.0 s，机械臂/相机还在移动，Buffer 最新关系在 t=10.2 s。查询采集时刻失败，改 latest 后“能跑了”。

列出至少三项该查的证据。什么条件下固定相机的静态关系可以跨时刻使用？什么条件下整条变换链仍有动态部分？

<a id="ex4"></a>

### 第 4 题：收到一个目标点，再查询对应时刻的变换。后续约 30 分钟

在学习节点中订阅 PointStamped，使用消息 frame_id 和 stamp 查询到 base_link 的变换。先用合成坐标，查询失败时明确记录并不输出旧结果。

验收：有方向图、一个已知点对照、一次错误帧名或缺失时刻的失败记录。可以先用离线 Buffer 插入已知关系验证，再做真实 Listener 收发。

## 直觉与回顾

TF 像保存了“谁相对谁、在什么时刻”的坐标关系表。知道两个人的地址关系，不代表拿错参照系后地址仍然对。

当你能写出 p_base = T_base_camera p_camera，API 的两个字符串就有了可检验的意义。复盘用一个点证明自己的方向，再说一句 latest 到底替你选择了什么。

