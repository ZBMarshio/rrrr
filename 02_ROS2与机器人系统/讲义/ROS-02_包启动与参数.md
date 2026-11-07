# ROS-02：从源码到启动命令，再到真正生效的参数

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#ros-02) · [提示与答案](../参考答案/ROS-02_参考答案.md)

<a id="intro"></a>

## 导读

**为什么学这一节。** 改了源码却没生效、参数写了却没被使用，都可能是启动链中的某一环没有接上。本节把源码与实际运行进程连起来。

**学完会有什么变化。** 从只记启动命令，进到能追踪模块、入口注册、安装位置、launch和节点初始化，判断参数在哪一层生效。

**接下来能做什么。** 可以建立自己的学习包，启动带配置的小系统，也能定位后续MoveIt或策略程序到底加载了哪份代码。

## 资料读到哪里

| 官方资料 | 选读范围 |
|---|---|
| [Creating a workspace](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.rst) | underlay/overlay、src/build/install/log、构建与 source |
| [Creating a package](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.rst) | ament_python 组成、package.xml、setup.py/setup.cfg |
| [Python 参数教程](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-Client-Libraries/Using-Parameters-In-A-Class-Python.rst) | declare/get、启动覆盖、descriptor；注意示例自己的更新行为 |
| [Creating launch files](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Intermediate/Launch/Creating-Launch-Files.rst) | 启动多个节点、namespace、参数与命令行参数 |

W02 先 Python 包与最小 launch；C++ 的 CMake/ament_cmake 组织随 W05 的官方模板补。

## 启动链要画到函数调用

`源码模块 → setup.py 的 console_scripts → install 中的可执行入口 → ros2 run → main → Node 初始化 → 回调`。

`ros2 launch` 读取 launch 描述，负责启动进程、传入参数与 remap；它不是自动替你实现节点内部逻辑。运行已安装包时，源目录新加的 launch/config 文件也要纳入安装规则。

包名、Python 模块名、可执行名、节点名可以相同，也可以不同。排“找不到 executable”先查入口注册，排“改源码没有变化”先查实际包前缀与模块来源。

## 自己创建一个学习包

先选没有混入实验室 overlay 的练习环境与独立工作空间。下面路径是你手动创建项目的示例：

```bash
mkdir -p ~/robot_learning_ws/src
cd ~/robot_learning_ws/src
ros2 pkg create trajectory_demo --build-type ament_python --license Apache-2.0 --dependencies rclpy sensor_msgs launch launch_ros
```

把 ROS-01 的源码放进包内的 trajectory_demo/state_source.py；订阅者同理。随后完善入口与安装，回到工作空间根目录构建。这里不会为你自动生成完整项目。

source 的顺序和位置要清楚：先 ROS underlay，再学习工作空间 overlay；建议构建终端只加载所需 underlay，运行时另开终端加载新 install，避免旧环境干扰。

## 参数有三个生效环节

1. launch/命令行实际传了什么；
2. 节点声明并接受了什么；
3. 程序在哪个时刻读取它、如何更新实际对象。

例如初始化时读取 publish_hz 并创建 timer，之后只修改参数服务器的值，不会凭空重建 timer。支持运行时修改，需要验证参数并更新相关对象；本期可明确采用“仅启动时配置”。

使用 YAML 参数时，节点完整名/命名空间匹配、ros__parameters 层级和数值类型都要检查。launch argument 也不会自动变成节点参数，必须显式连接。

## 练习

<a id="ex1"></a>

### 第 1 题：让 ros2 run 找到自己的节点。约 30 分钟

在新学习包中注册 state_source/state_recorder，构建并运行。解释 src、build、install、log 各存什么，找到实际包前缀。

保留一次 package.xml 依赖、setup.py 入口与 main 的对应说明。修改源文件后复跑，确认运行的是你这份代码。

<a id="ex2"></a>

### 第 2 题：用一个 launch 启动两个节点。约 30 分钟

创建 nodes.launch.py，启动同一包的发布者和记录器，namespace 都为 learn_ch2，输出到终端。让 ros2 launch 能找到安装后的 launch 文件。

验收：能说明两个完整节点名、状态话题名；关闭后新终端可复跑；无须依赖你手工 cd 到源码内部。

<a id="ex3"></a>

### 第 3 题：改变频率，先查它有没有真正生效。约 25 分钟

给发布者添加 double 类型 publish_hz 参数，启动时可设为 5.0 或 10.0，要求有限且大于零。

先实现仅启动时可配置并声明只读。用 param get/describe 与 topic hz 观察。再解释：如果去掉只读限制，却没有更新 timer 的逻辑，param set 成功后发布频率会自动改变吗？

运行时修改只作后续扩展，不把多线程参数更新挤进 W02。

<a id="ex4"></a>

### 第 4 题：配置传到哪里丢了？约 20 分钟

假设 launch argument 已设成 5.0，但节点仍打印 10.0；另一个场景是 get 参数显示 5.0、实际周期却仍约 0.1 秒。

分别写最短检查顺序。再给出一种 YAML 写错节点名导致参数未覆盖的例子，并说明怎样区分“传参没到”和“逻辑没用”。

## 直觉与回顾

包像一件可交付的软件，入口像它对外的门；launch 负责把合作者叫到一起，并告诉它们各自配置。被叫起来以后做什么，还要回到节点源码看。

参数也像一张配方：数值写在纸上，与已经拿它调好的定时器，是两个位置。理解这点后，遇到“我明明改了配置”就能顺着传递关系找到证据。

请画一次你自己的“启动命令 → 参数 → 读取位置 → 实际对象”图，并指出哪处决定是否支持运行时修改。

