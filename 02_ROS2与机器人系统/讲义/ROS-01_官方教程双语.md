# ROS-01 官方教程双语阅读（Jazzy）

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#ros-01) · [讲义正文](ROS-01_节点消息与通信.md) · [提示与答案](../参考答案/ROS-01_参考答案.md)

这份材料只做一件事：把 ROS-01 需要读的官方教程**原文完整摘出来，逐段给出忠实译文**。原文在前，译文在后，段落用 [1]、[2] 编号一一对应；每节最后才是我的补充（术语、长句、易错点、与练习的关系）。补充可以跳过，原文和译文请按顺序读。

**选读范围**（对应讲义“目标与资料”表）：

| 教程 | 回答的问题 | 建议用时 |
|---|---|---|
| Understanding nodes | 节点是什么，`ros2 run` / `node list` / `node info` 各看什么 | 15 min |
| Understanding topics | 话题怎么连接收发双方，消息类型、`echo` / `info` / `hz` / `pub` 怎么用 | 30 min |
| Understanding services | 请求/响应与发布/订阅的差别，`service list/type/info/call` | 20 min |
| Understanding actions | 目标、反馈、结果、取消与中止，`action list/info/send_goal` | 25 min |
| Writing a simple publisher and subscriber (Python) | 节点类、`create_publisher` / `create_subscription`、定时器、spin、入口点 | 60 min |
| JointState 定义 | 字段、单位，以及 name 与各数组的对应关系 | 15 min |

**原文出处**：英文取自 ROS 2 Jazzy 文档的源文件（`ros2_documentation` 仓库 `jazzy` 分支的 `.rst`），与网页版内容一致，只去掉了 Sphinx 标记；每节标题下给出源文件链接。ROS 文档以 CC BY 4.0 发布。文中的 `{REPOS_FILE_BRANCH}`、`{package(rclpy)}` 这类占位符，在网页上是构建时替换的，这里直接写成 `jazzy`、`rclpy`、`std_msgs`。

**怎么读**：第一遍不看译文，遇到卡住的段落记下编号；第二遍对照译文，检查自己是不是真的读懂了每个从句，而不是“大概知道在说啥”。命令和输出不用背，先记住“这条命令回答什么问题”。

---

<a id="context"></a>

## 0. 前因后果：这些教程在用什么，为什么按这个顺序

（编者按，不是原文）

**turtlesim 是什么。** 它是 ROS 2 自带的一个二维“海龟”模拟器，专门用来学通信，不碰真实硬件。启动 `turtlesim_node` 后会出现一个窗口和一只海龟；这个节点订阅 `/turtle1/cmd_vel`（类型 `geometry_msgs/msg/Twist`，装线速度和角速度），按收到的速度移动海龟，同时把位姿发布到 `/turtle1/pose`。另一个节点 `turtle_teleop_key` 把键盘方向键转成 `cmd_vel` 消息发出去。所以“按方向键 → 海龟动”这条链路里，已经包含了 ROS-01 要学的全部角色：发布者、订阅者、话题、消息类型。

**为什么先学命令行，而不是先写代码。** 机器人系统的第一类问题往往不是“代码写错了”，而是“我以为它在发，其实没发”“我订阅的名字和它发的不是同一个”“类型对不上”。`ros2 node/topic/service/action` 这一组命令，就是用来在**不改代码**的前提下回答这些问题的：图里有哪些节点、谁在发、发的是什么类型、频率多少、有几个人在收。等你会用这些命令观察了，再写发布/订阅节点，出错时才知道去哪儿看。

**五份材料的顺序是有依赖的：**

1. **节点**先回答“谁”。节点是图里的参与者，名字、命名空间、它连了哪些话题/服务/动作，`node info` 一次列全。
2. **话题**回答“持续流动的数据怎么走”。发布者与订阅者通过同名、同类型的话题连接；`echo` 看内容，`hz` 看频率，`info` 看有几个人在发、几个人在收。
3. **服务**回答“一次请求、一次响应”。它和话题的差别不只是“同步/异步”，而是**只有被调用时才产生数据**；`Empty`、`Spawn` 这些类型能让你直接看到请求和响应两段结构。
4. **动作**回答“要跑一段时间、还要能取消的任务”。它建立在话题和服务之上：goal、feedback、result 三段，客户端可以取消，服务端也可以中止（abort）。
5. **最后写发布/订阅节点**，把前面观察到的名字、类型、队列长度落到代码里：类继承 `Node`，构造函数里 `create_publisher` / `create_subscription`，`create_timer` 定时，`rclpy.spin` 让回调真正被调用。

**读之前的环境前提**：每个新终端都要 `source /opt/ros/jazzy/setup.bash`，否则 `ros2` 命令不存在，或者找不到 turtlesim。你的环境检查已经确认了 Jazzy 与 `/usr/bin/python3` 的 rclpy，这一条已经满足。如果按学习指南在练习终端里设了 `ROS_DOMAIN_ID` 和发现范围，**所有**参与实验的终端都要一致，否则互相看不见。

> 下面开始是原文。英文段落前的 [n] 是段落编号，译文用相同编号；代码、命令和输出保持原样。

---

<a id="nodes"></a>

## 1. Understanding nodes（理解节点）

原文：[Understanding-ROS2-Nodes.rst](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.rst)

**Goal:** Learn about the function of nodes in ROS 2, and the tools to interact with them.

**Tutorial level:** Beginner

**Time:** 10 minutes

### 原文

**Background**

[1] Over the next few tutorials, you will learn about a series of core ROS 2 concepts that make up what is referred to as the "ROS (2) graph".

[2] The ROS graph is a network of ROS 2 elements processing data together at the same time. It encompasses all executables and the connections between them if you were to map them all out and visualize them.

[3] Each node in ROS should be responsible for a single, modular purpose, e.g. controlling the wheel motors or publishing the sensor data from a laser range-finder.

[4] Each node can send and receive data from other nodes via topics, services, actions, or parameters.

[5] A full robotic system is comprised of many nodes working in concert.

[6] In ROS 2, a single executable (C++ program, Python program, etc.) can contain one or more nodes.

**Prerequisites**

[7] The previous tutorial shows you how to install the `turtlesim` package used here.

[8] As always, don't forget to source ROS 2 in every new terminal you open.

**Tasks**

*1 ros2 run*

[9] The command `ros2 run` launches an executable from a package.

```
$ ros2 run <package_name> <executable_name>
```

[10] To run turtlesim, open a new terminal, and enter the following command:

```
$ ros2 run turtlesim turtlesim_node
```

[11] The turtlesim window will open, as you saw in the previous tutorial.

[12] Here, the package name is `turtlesim` and the executable name is `turtlesim_node`.

[13] We still don't know the node name, however. You can find node names by using `ros2 node list`

*2 ros2 node list*

[14] `ros2 node list` will show you the names of all running nodes.

[15] This is especially useful when you want to interact with a node, or when you have a system running many nodes and need to keep track of them.

[16] Open a new terminal while turtlesim is still running in the other one, and enter the following command. The terminal will return the node name:

```
$ ros2 node list
/turtlesim
```

[17] Open another new terminal and start the teleop node with the command:

```
$ ros2 run turtlesim turtle_teleop_key
```

[18] Here, we are referring to the `turtlesim` package again, but this time we target the executable named `turtle_teleop_key`.

[19] Return to the terminal where you ran `ros2 node list` and run it again. You will now see the names of two active nodes:

```
$ ros2 node list
/turtlesim
/teleop_turtle
```

*2.1 Remapping*

[20] Remapping allows you to reassign default node properties, like node name, topic names, service names, etc., to custom values.

[21] In the last tutorial, you used remapping on `turtle_teleop_key` to change the cmd_vel topic and target **turtle2**.

[22] Now, let's reassign the name of our `/turtlesim` node. In a new terminal, run the following command:

```
$ ros2 run turtlesim turtlesim_node --ros-args --remap __node:=my_turtle
```

[23] Since you're calling `ros2 run` on turtlesim again, another turtlesim window will open.

[24] However, now if you return to the terminal where you ran `ros2 node list`, and run it again, you will see three node names:

```
/my_turtle
/turtlesim
/teleop_turtle
```

*3 ros2 node info*

[25] Now that you know the names of your nodes, you can access more information about them with:

```
$ ros2 node info <node_name>
```

[26] To examine your latest node, `my_turtle`, run the following command:

```
$ ros2 node info /my_turtle
/my_turtle
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim/msg/Color
    /turtle1/pose: turtlesim/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim/srv/Kill
    /my_turtle/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /my_turtle/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /my_turtle/get_parameters: rcl_interfaces/srv/GetParameters
    /my_turtle/list_parameters: rcl_interfaces/srv/ListParameters
    /my_turtle/set_parameters: rcl_interfaces/srv/SetParameters
    /my_turtle/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim/srv/Spawn
    /turtle1/set_pen: turtlesim/srv/SetPen
    /turtle1/teleport_absolute: turtlesim/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim/srv/TeleportRelative
  Service Clients:

  Action Servers:
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
  Action Clients:
```

[27] `ros2 node info` returns a list of subscribers, publishers, services, and actions. i.e. the ROS graph connections that interact with that node.

[28] Now try running the same command on the `/teleop_turtle` node, and see how its connections differ from `my_turtle`.

[29] You will learn more about the ROS graph connection concepts including the message types in the upcoming tutorials.

**Summary**

[30] A node is a fundamental ROS 2 element that serves a single, modular purpose in a robotics system.

[31] In this tutorial, you utilized nodes created in the `turtlesim` package by running the executables `turtlesim_node` and `turtle_teleop_key`.

[32] You learned how to use `ros2 node list` to discover active node names and `ros2 node info` to introspect a single node.

[33] These tools are vital to understanding the flow of data in a complex, real-world robot system.

**Next steps**

[34] Now that you understand nodes in ROS 2, you can move on to the topics tutorial. Topics are one of the communication types that connects nodes.

**Related content**

[35] The Concepts page adds some more detail to the concept of nodes.

### 译文

**背景**

[1] 在接下来的几节教程里，你会陆续认识一组核心的 ROS 2 概念，它们共同构成所谓的“ROS（2）图”。

[2] ROS 图是一张网络，其中的 ROS 2 元素在同一时间一起处理数据。如果你把所有可执行文件以及它们之间的连接都画出来、可视化，那么这张图涵盖的就是这些可执行文件和它们之间的连接。

[3] ROS 中的每个节点应当只负责一个单一的、模块化的目的，例如控制轮子电机，或者发布来自激光测距仪的传感器数据。

[4] 每个节点都可以通过话题、服务、动作或参数，向其他节点发送数据、从其他节点接收数据。

[5] 一个完整的机器人系统由许多协同工作的节点构成。

[6] 在 ROS 2 中，一个可执行文件（C++ 程序、Python 程序等）可以包含一个或多个节点。

**前置条件**

[7] 上一节教程展示了如何安装这里要用的 `turtlesim` 包。

[8] 和往常一样，别忘了在你打开的每一个新终端里 source 一下 ROS 2。

**任务**

*1 ros2 run*

[9] `ros2 run` 命令从某个包里启动一个可执行文件。

```
$ ros2 run <package_name> <executable_name>
```

[10] 要运行 turtlesim，打开一个新终端，输入下面的命令：

```
$ ros2 run turtlesim turtlesim_node
```

[11] turtlesim 的窗口会打开，和你在上一节教程里看到的一样。

[12] 这里，包名是 `turtlesim`，可执行文件名是 `turtlesim_node`。

[13] 不过，我们仍然不知道节点名。你可以用 `ros2 node list` 查出节点名。

*2 ros2 node list*

[14] `ros2 node list` 会显示所有正在运行的节点的名字。

[15] 当你想和某个节点交互，或者你的系统里跑着很多节点、需要随时掌握它们时，这条命令特别有用。

[16] 在 turtlesim 还在另一个终端里运行的时候，打开一个新终端，输入下面的命令。终端会返回节点名：

```
$ ros2 node list
/turtlesim
```

[17] 再打开一个新终端，用下面的命令启动 teleop 节点：

```
$ ros2 run turtlesim turtle_teleop_key
```

[18] 这里我们指的仍然是 `turtlesim` 这个包，但这一次瞄准的是名为 `turtle_teleop_key` 的可执行文件。

[19] 回到你运行 `ros2 node list` 的那个终端，再运行一次。现在你会看到两个活动节点的名字：

```
$ ros2 node list
/turtlesim
/teleop_turtle
```

*2.1 重映射*

[20] 重映射（remapping）让你可以把节点的默认属性——比如节点名、话题名、服务名等——重新指定为自定义的值。

[21] 上一节教程里，你对 `turtle_teleop_key` 用了重映射，把 cmd_vel 话题改掉，并让目标指向 **turtle2**。

[22] 现在，我们来给 `/turtlesim` 节点改个名字。在一个新终端里，运行下面的命令：

```
$ ros2 run turtlesim turtlesim_node --ros-args --remap __node:=my_turtle
```

[23] 因为你又对 turtlesim 调用了一次 `ros2 run`，所以会再打开一个 turtlesim 窗口。

[24] 不过，现在如果你回到运行 `ros2 node list` 的终端再运行一次，就会看到三个节点名：

```
/my_turtle
/turtlesim
/teleop_turtle
```

*3 ros2 node info*

[25] 既然知道了节点的名字，你就可以用下面的命令获取关于它们的更多信息：

```
$ ros2 node info <node_name>
```

[26] 要查看你最新启动的节点 `my_turtle`，运行下面的命令：

```
$ ros2 node info /my_turtle
/my_turtle
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim/msg/Color
    /turtle1/pose: turtlesim/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim/srv/Kill
    /my_turtle/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /my_turtle/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /my_turtle/get_parameters: rcl_interfaces/srv/GetParameters
    /my_turtle/list_parameters: rcl_interfaces/srv/ListParameters
    /my_turtle/set_parameters: rcl_interfaces/srv/SetParameters
    /my_turtle/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim/srv/Spawn
    /turtle1/set_pen: turtlesim/srv/SetPen
    /turtle1/teleport_absolute: turtlesim/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim/srv/TeleportRelative
  Service Clients:

  Action Servers:
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
  Action Clients:
```

[27] `ros2 node info` 返回订阅者、发布者、服务与动作的列表，也就是与该节点交互的那些 ROS 图连接。

[28] 现在试着对 `/teleop_turtle` 节点运行同一条命令，看看它的连接和 `my_turtle` 有什么不同。

[29] 在接下来的教程里，你会进一步了解 ROS 图连接的概念，包括消息类型。

**小结**

[30] 节点是 ROS 2 的基本元素，在机器人系统里承担一个单一的、模块化的目的。

[31] 本节教程里，你通过运行 `turtlesim_node` 和 `turtle_teleop_key` 这两个可执行文件，使用了 `turtlesim` 包里创建的节点。

[32] 你学会了用 `ros2 node list` 发现活动节点的名字，用 `ros2 node info` 内省单个节点。

[33] 在理解一个复杂的真实机器人系统里数据如何流动时，这些工具至关重要。

**下一步**

[34] 既然你已经理解了 ROS 2 中的节点，就可以继续看话题教程了。话题是连接节点的通信类型之一。

**相关内容**

[35] Concepts 页面补充了更多关于节点概念的细节。

### 读法补充

**术语**

| 英文 | 在 ROS 里的意思 | 不要误解成 |
|---|---|---|
| executable | 包里的一个可执行文件，`ros2 run` 的对象 | 不是节点；一个可执行文件可以起多个节点 |
| node | 图里的参与者，有名字、有连接 | 不等于进程 |
| introspect | 查看运行中对象的内部结构（这里有 `node info`、`topic info`） | 不是“反省” |
| remap | 把默认名字换成自定义名字 | 只改你指定的那一项，别的名字不变 |

**长句拆解**

- [2] `It encompasses all executables and the connections between them if you were to map them all out and visualize them.` 主句是 `It encompasses A and B`（它涵盖 A 和 B）；`if you were to ...` 是虚拟条件，“如果你把……都画出来并可视化的话”。`them` 指可执行文件。
- [27] `i.e. the ROS graph connections that interact with that node.` 这是对前半句的同位解释：`i.e.` = “也就是说”；`that interact with that node` 是定语从句，修饰 connections。

**读的时候注意**

- `node list` 输出的名字带前导 `/`，这是完全限定名；命名空间 + 节点名拼出来的。第 1 题要你写“节点完整名”，来源就是这里。
- 同一个 turtlesim 起了两次（`/turtlesim` 和 `/my_turtle`），说明**节点名可以重映射，话题名没有跟着变**：两个窗口都还在发 `/turtle1/...`。这正是“名字要看上下文”的具体例子。
- `ros2 node info` 的输出结构就是第 1 题要你画的那张关系图的文字版：Subscribers / Publishers / Service Servers / Service Clients / Action Servers / Action Clients 六类。先能照着它画，再谈“谁给谁什么信息”。

---

<a id="topics"></a>

## 2. Understanding topics（理解话题）

原文：[Understanding-ROS2-Topics.rst](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.rst)

**Goal:** Use rqt_graph and command line tools to introspect ROS 2 topics.

**Tutorial level:** Beginner

**Time:** 20 minutes

### 原文

**Background**

[1] ROS 2 breaks complex systems down into many modular nodes. Topics are a vital element of the ROS graph that act as a bus for nodes to exchange messages.

[2] A node may publish data to any number of topics and simultaneously have subscriptions to any number of topics.

[3] Topics are one of the main ways in which data is moved between nodes and therefore between different parts of the system.

**Prerequisites**

[4] The previous tutorial provides some useful background information on nodes that is built upon here.

[5] As always, don't forget to source ROS 2 in every new terminal you open.

**Tasks**

*1 Setup*

[6] By now you should be comfortable starting up turtlesim.

[7] Open a new terminal and run:

```
$ ros2 run turtlesim turtlesim_node
```

[8] Open another terminal and run:

```
$ ros2 run turtlesim turtle_teleop_key
```

[9] Recall from the previous tutorial that the names of these nodes are `/turtlesim` and `/teleop_turtle` by default.

*2 rqt_graph*

[10] Throughout this tutorial, we will use `rqt_graph` to visualize the changing nodes and topics, as well as the connections between them.

[11] The turtlesim tutorial tells you how to install rqt and all its plugins, including `rqt_graph`.

[12] To run rqt_graph, open a new terminal and enter the command:

```
$ ros2 run rqt_graph rqt_graph
```

[13] You can also open rqt_graph by opening `rqt` and selecting **Plugins** > **Introspection** > **Node Graph**.

[14] You should see the above nodes and topic, as well as two actions around the periphery of the graph (let's ignore those for now).

[15] If you hover your mouse over the topic in the center, you'll see the color highlighting like in the image above.

[16] The graph is depicting how the `/turtlesim` node and the `/teleop_turtle` node are communicating with each other over a topic.

[17] The `/teleop_turtle` node is publishing data (the keystrokes you enter to move the turtle around) to the `/turtle1/cmd_vel` topic, and the `/turtlesim` node is subscribed to that topic to receive the data.

[18] The highlighting feature of rqt_graph is very helpful when examining more complex systems with many nodes and topics connected in many different ways.

[19] rqt_graph is a graphical introspection tool. Now we'll look at some command line tools for introspecting topics.

*3 ros2 topic list*

[20] Running the `ros2 topic list` command in a new terminal will return a list of all the topics currently active in the system:

```
$ ros2 topic list
/parameter_events
/rosout
/turtle1/cmd_vel
/turtle1/color_sensor
/turtle1/pose
```

[21] `ros2 topic list -t` will return the same list of topics, this time with the topic type appended in brackets:

```
$ ros2 topic list -t
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim/msg/Color]
/turtle1/pose [turtlesim/msg/Pose]
```

[22] These attributes, particularly the type, are how nodes know they're talking about the same information as it moves over topics.

[23] If you're wondering where all these topics are in rqt_graph, you can uncheck all the boxes under **Hide:**

[24] For now, though, leave those options checked to avoid confusion.

*4 ros2 topic echo*

[25] To see the data being published on a topic, use:

```
$ ros2 topic echo <topic_name>
```

[26] Since we know that `/teleop_turtle` publishes data to `/turtlesim` over the `/turtle1/cmd_vel` topic, let's use `echo` to introspect that topic:

```
$ ros2 topic echo /turtle1/cmd_vel
```

[27] At first, this command won't return any data. That's because it's waiting for `/teleop_turtle` to publish something.

[28] Return to the terminal where `turtle_teleop_key` is running and use the arrows to move the turtle around. Watch the terminal where your `echo` is running at the same time, and you'll see position data being published for every movement you make:

```
linear:
  x: 2.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
  ---
```

[29] Now return to rqt_graph and uncheck the **Debug** box.

[30] `/_ros2cli_26646` is the node created by the `echo` command we just ran (the number might be different).

[31] Now you can see that the publisher is publishing data over the `cmd_vel` topic, and two subscribers are subscribed to it.

*5 ros2 topic info*

[32] Topics don't have to only be one-to-one communication; they can be one-to-many, many-to-one, or many-to-many.

[33] Another way to look at this is running:

```
$ ros2 topic info /turtle1/cmd_vel
Type: geometry_msgs/msg/Twist
Publisher count: 1
Subscription count: 2
```

*5.1 ros2 topic info --verbose*

[34] For more detailed information about a topic, you can use the `--verbose` (or `-v`) flag:

```
$ ros2 topic info /turtle1/cmd_vel --verbose
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: teleop_turtle
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 24.ba.3e.e7.c1.51.bb.46.21.41.de.36.1b.14.73.5e
QoS profile:
  Reliability: RELIABLE
  History (Depth): KEEP_LAST (7)
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 2

Node name: _ros2cli_300492
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: cc.4d.98.79.29.91.fe.25.8a.0a.c9.03.db.1a.ec.81
QoS profile:
  Reliability: RELIABLE
  History (Depth): KEEP_LAST (5)
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: 9c.33.59.38.b2.f2.42.47.69.1b.7f.0e.5e.1d.86.f5
QoS profile:
  Reliability: RELIABLE
  History (Depth): KEEP_LAST (7)
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```

[35] This will return additional details including:

- Node names and namespaces of publishers and subscribers
- Topic type
- QoS profiles

*6 ros2 interface show*

[36] Nodes send data over topics using messages. Publishers and subscribers must send and receive the same type of message to communicate.

[37] The topic types we saw earlier after running `ros2 topic list -t` let us know what message type is used on each topic.

[38] Recall that the `cmd_vel` topic has the type:

```
geometry_msgs/msg/Twist
```

[39] This means that in the package `geometry_msgs` there is a `msg` called `Twist`.

[40] Now we can run `ros2 interface show <msg_type>` on this type to learn its details. Specifically, what structure of data the message expects.

```
$ ros2 interface show geometry_msgs/msg/Twist
```

[41] Which will return:

```
# This expresses velocity in free space broken into its linear and angular parts.
Vector3  linear
        float64 x
        float64 y
        float64 z
Vector3  angular
        float64 x
        float64 y
        float64 z
```

[42] This tells you that the `/turtlesim` node is expecting a message with two vectors, `linear` and `angular`, of three elements each.

[43] If you recall the data we saw `/teleop_turtle` passing to `/turtlesim` with the `echo` command, it's in the same structure:

```
linear:
  x: 2.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
  ---
```

*7 ros2 topic pub*

[44] Now that you have the message structure, you can publish data to a topic directly from the command line using:

```
$ ros2 topic pub <topic_name> <msg_type> '<args>'
```

[45] The `'<args>'` argument is the actual data you'll pass to the topic, in the structure you just discovered in the previous section.

[46] There are four main ways to use the `pub` command as shown below. However, the autocomplete feature described in `c.` and `d.` is not supported in Windows.

*a. **Publishing dictionary strings**:*

[47] In order to publish data to a topic, you need to pass the data in the form of YAML strings.

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}"
```

[48] However, you do not need to specify the entire message, if you are just changing the linear or angular velocity, you can just specify the values you want to change.

[49] For example, if you want to change the linear velocity to 2.0 and keep the angular velocity at 1.8, you can do the following:

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 1.8}}"
```

*b. **Publishing an empty message**:*

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist
```

[50] This will publish the default values for the message type at 1 Hz. In this case, this equivalent to the following command:

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --rate 1
```

*c. **Using autocomplete**:*

[51] You can trigger the autocomplete feature of your terminal by the following:

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist <TAB>
--keep-alive
--max-wait-time-secs
--node-name
--once
--print
--qos-depth
--qos-durability
--qos-history
--qos-liveliness
--qos-liveliness-lease-duration-seconds
--qos-profile
--qos-reliability
--rate
--spin-time
--stdin
--times
--use-sim-time
--wait-matching-subscriptions
--yaml-file
-1
-n
-p
-r
-s
-t
-w
\'linear:\^J\ \ x:\ 0.0\^J\ \ y:\ 0.0\^J\ \ z:\ 0.0\^Jangular:\^J\ \ x:\ 0.0\^J\ \ y:\ 0.0\^J\ \ z:\ 0.0\^J\'
```

[52] All the options will be autocompleted by pressing the **tab** key after the entering the first few characters of the option.

[53] However, the topic message prototype will only be autocompleted after `\'<TAB>` is entered.

[54] This is because the terminal does not recognize the single quote as part of the autocomplete string. Hence it needs to be escaped by using `\'` to be recognized as part of the string.

[55] The final autocompleted string will look like this:

```
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist 'linear:
  x: 0.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
'
```

[56] This string is editable and you can change the values of the message type as required.

*d. **Using the raw autocompleted string**:*

[57] As mentioned above, the autocompleted string for `geometry_msgs/msg/Twist` looks like this:

```
\'linear:\^J\ \ x:\ 0.0\^J\ \ y:\ 0.0\^J\ \ z:\ 0.0\^Jangular:\^J\ \ x:\ 0.0\^J\ \ y:\ 0.0\^J\ \ z:\ 0.0\^J\'
```

[58] This can be directly used in place of the yaml string in the command line.

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist \'linear:\^J\ \ x:\ 0.0\^J\ \ y:\ 0.0\^J\ \ z:\ 0.0\^Jangular:\^J\ \ x:\ 0.0\^J\ \ y:\ 0.0\^J\ \ z:\ 0.0\^J\'
```

[59] The turtle (and commonly the real robots which it is meant to emulate) require a steady stream of commands to operate continuously. So, to get the turtle moving, and keep it moving, you can use the following dictionary string:

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}"
```

[60] At times you may want to publish data to your topic only once (rather than continuously). To publish your command just once add the `--once` option.

```
$ ros2 topic pub --once -w 2 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}"
```

[61] `--once` is an optional argument meaning "publish one message then exit".

[62] `-w 2` is an optional argument meaning "wait for two matching subscriptions". This is needed because we have both turtlesim and the topic echo subscribed.

[63] You will see the following output in the terminal:

```
Waiting for at least 2 matching subscription(s)...
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=1.8))
```

[64] And you will see your turtle move like so:

[65] You can refresh rqt_graph to see what's happening graphically. You will see that the `ros2 topic pub ...` node (`/_ros2cli_30358`) is publishing over the `/turtle1/cmd_vel` topic, which is being received by both the `ros2 topic echo ...` node (`/_ros2cli_26646`) and the `/turtlesim` node now.

[66] Finally, you can run `echo` on the `pose` topic and recheck rqt_graph:

```
$ ros2 topic echo /turtle1/pose
```

[67] You can see that the `/turtlesim` node is also publishing to the `pose` topic, which the new `echo` node has subscribed to.

[68] When publishing messages with timestamps, `pub` has two methods to automatically fill them out with the current time. For messages with a `std_msgs/msg/Header`, the header field can be set to `auto` to fill out the `stamp` field.

```
$ ros2 topic pub /pose geometry_msgs/msg/PoseStamped '{header: "auto", pose: {position: {x: 1.0, y: 2.0, z: 3.0}}}'
```

[69] If the message does not use a full header, but just has a field with type `builtin_interfaces/msg/Time`, that can be set to the value `now`.

```
$ ros2 topic pub /reference sensor_msgs/msg/TimeReference '{header: "auto", time_ref: "now", source: "dumy"}'
```

*8 ros2 topic hz*

[70] You can also view the rate at which data is published using:

```
$ ros2 topic hz /turtle1/pose
average rate: 59.354
  min: 0.005s max: 0.027s std dev: 0.00284s window: 58
```

[71] It will return data on the rate at which the `/turtlesim` node is publishing data to the `pose` topic.

[72] Recall that you set the rate of `turtle1/cmd_vel` to publish at a steady 1 Hz using `ros2 topic pub --rate 1`. If you run the above command with `turtle1/cmd_vel` instead of `turtle1/pose`, you will see an average reflecting that rate.

> **Note:** The rate reflects the receiving rate on the subscription created by the `ros2 topic hz` command, which might be affected by platform resources and QoS configuration, and may not exactly match the publisher rate.

*9 ros2 topic bw*

[73] The bandwidth used by a topic can be viewed using:

```
$ ros2 topic bw /turtle1/pose
Subscribed to [/turtle1/pose]
1.51 KB/s from 62 messages
    Message size mean: 0.02 KB min: 0.02 KB max: 0.02 KB
```

[74] It returns the bandwidth utilization and number of messages being published to the `/turtle1/pose` topic.

> **Note:** The bandwidth reflects the receiving rate on the subscription created by the `ros2 topic bw` command, which might be affected by platform resources and QoS configuration, and may not exactly match the publisher's bandwidth.

*10 ros2 topic find*

[75] To list a list of available topics of a given type use:

```
$ ros2 topic find <topic_type>
```

[76] Recall that the `cmd_vel` topic has the type:

```
geometry_msgs/msg/Twist
```

[77] Using the `find` command outputs topics available when given the message type:

```
$ ros2 topic find geometry_msgs/msg/Twist
/turtle1/cmd_vel
```

*11 Clean up*

[78] At this point you'll have a lot of nodes running. Don't forget to stop them by entering `Ctrl+C` in each terminal.

**Summary**

[79] Nodes publish information over topics, which allows any number of other nodes to subscribe to and access that information.

[80] In this tutorial you examined the connections between several nodes over topics using rqt_graph and command line tools. You should now have a good idea of how data moves around a ROS 2 system.

**Next steps**

[81] Next you'll learn about another communication type in the ROS graph with the tutorial Understanding services.

### 译文

**背景**

[1] ROS 2 把复杂系统拆成许多模块化的节点。话题是 ROS 图中至关重要的元素，它像一条总线，供节点交换消息。

[2] 一个节点可以向任意数量的话题发布数据，同时也可以订阅任意数量的话题。

[3] 话题是节点之间、也就是系统不同部分之间移动数据的主要方式之一。

**前置条件**

[4] 上一节教程提供了一些关于节点的有用背景，本节在此基础上展开。

[5] 和往常一样，别忘了在你打开的每一个新终端里 source 一下 ROS 2。

**任务**

*1 准备*

[6] 到现在，你应该已经能熟练启动 turtlesim 了。

[7] 打开一个新终端并运行：

```
$ ros2 run turtlesim turtlesim_node
```

[8] 打开另一个终端并运行：

```
$ ros2 run turtlesim turtle_teleop_key
```

[9] 回想上一节教程：这两个节点的名字默认是 `/turtlesim` 和 `/teleop_turtle`。

*2 rqt_graph*

[10] 在本教程中，我们会用 rqt_graph 来可视化不断变化的节点和话题，以及它们之间的连接。

[11] turtlesim 教程告诉你如何安装 rqt 及其所有插件，包括 `rqt_graph`。

[12] 要运行 rqt_graph，打开一个新终端，输入命令：

```
$ ros2 run rqt_graph rqt_graph
```

[13] 你也可以先打开 `rqt`，再选择 **Plugins > Introspection > Node Graph** 来打开 rqt_graph。

[14] 你应该能看到上面这些节点和话题，以及图外围的两个动作（先不管它们）。

[15] 如果你把鼠标悬停在中间的话题上，就会看到像上图那样的颜色高亮。

[16] 这张图描绘的是 `/turtlesim` 节点和 `/teleop_turtle` 节点如何通过一个话题互相通信。

[17] `/teleop_turtle` 节点把数据（你输入的、让海龟移动的按键）发布到 `/turtle1/cmd_vel` 话题，`/turtlesim` 节点订阅该话题来接收数据。

[18] 在检查由许多节点和话题以多种方式连接起来的更复杂的系统时，rqt_graph 的高亮功能非常有用。

[19] rqt_graph 是一个图形化的内省工具。接下来我们看一些用于内省话题的命令行工具。

*3 ros2 topic list*

[20] 在新终端里运行 `ros2 topic list`，会返回系统中当前所有活动话题的列表：

```
$ ros2 topic list
/parameter_events
/rosout
/turtle1/cmd_vel
/turtle1/color_sensor
/turtle1/pose
```

[21] `ros2 topic list -t` 会返回同样的话题列表，只是这次把话题类型用方括号附在后面：

```
$ ros2 topic list -t
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim/msg/Color]
/turtle1/pose [turtlesim/msg/Pose]
```

[22] 这些属性，尤其是类型，正是节点在话题上传输信息时判断“我们说的是同一份信息”的依据。

[23] 如果你想知道这些话题在 rqt_graph 里都去哪儿了，可以把 **Hide:** 下面的复选框全部取消勾选：

[24] 不过眼下，先让这些选项保持勾选，以免混淆。

*4 ros2 topic echo*

[25] 要查看某个话题上正在发布的数据，用：

```
$ ros2 topic echo <topic_name>
```

[26] 既然我们知道 `/teleop_turtle` 通过 `/turtle1/cmd_vel` 话题向 `/turtlesim` 发布数据，那就用 `echo` 来内省这个话题：

```
$ ros2 topic echo /turtle1/cmd_vel
```

[27] 一开始，这条命令不会返回任何数据。这是因为它正在等待 `/teleop_turtle` 发布内容。

[28] 回到正在运行 `turtle_teleop_key` 的终端，用方向键让海龟动起来。同时盯着运行 `echo` 的终端，你会看到你每动一次，就有一份位置数据被发布出来：

```
linear:
  x: 2.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
  ---
```

[29] 现在回到 rqt_graph，取消勾选 **Debug** 框。

[30] `/_ros2cli_26646` 就是我们刚运行的 `echo` 命令创建的节点（数字可能不同）。

[31] 现在你能看到，发布者正通过 `cmd_vel` 话题发布数据，而有两个订阅者订阅了它。

*5 ros2 topic info*

[32] 话题不必只是一对一通信；它可以是一对多、多对一或多对多。

[33] 换一种方式看这件事，可以运行：

```
$ ros2 topic info /turtle1/cmd_vel
Type: geometry_msgs/msg/Twist
Publisher count: 1
Subscription count: 2
```

*5.1 带 --verbose*

[34] 要获取某个话题更详细的信息，可以用 `--verbose`（或 `-v`）选项：

```
$ ros2 topic info /turtle1/cmd_vel --verbose
```

[35] 这会返回额外的细节，包括：

- 发布者和订阅者的节点名与命名空间
- 话题类型
- QoS 配置

（完整输出见原文，字段含义见下面“读法补充”。）

*6 ros2 interface show*

[36] 节点通过消息在话题上发送数据。发布者和订阅者必须发送、接收同一类型的消息，才能通信。

[37] 我们前面运行 `ros2 topic list -t` 时看到的话题类型，就是告诉我们每个话题上用的是哪种消息类型。

[38] 回想一下，`cmd_vel` 话题的类型是：

```
geometry_msgs/msg/Twist
```

[39] 这意味着在 `geometry_msgs` 包里有一个名为 `Twist` 的 `msg`。

[40] 现在我们可以对这个类型运行 `ros2 interface show <msg_type>`，了解它的细节。具体说，就是这条消息期望什么样的数据结构。

```
$ ros2 interface show geometry_msgs/msg/Twist
```

[41] 它会返回：

```
# This expresses velocity in free space broken into its linear and angular parts.
Vector3  linear
        float64 x
        float64 y
        float64 z
Vector3  angular
        float64 x
        float64 y
        float64 z
```

[42] 这告诉你，`/turtlesim` 节点期待的消息包含两个向量 `linear` 和 `angular`，每个向量各有三个元素。

[43] 如果你还记得我们用 `echo` 命令看到的 `/teleop_turtle` 传给 `/turtlesim` 的数据，它的结构是一样的：

```
linear:
  x: 2.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
  ---
```

*7 ros2 topic pub*

[44] 既然拿到了消息结构，你就可以直接用命令行向话题发布数据：

```
$ ros2 topic pub <topic_name> <msg_type> '<args>'
```

[45] `'<args>'` 这个参数就是你要传给话题的实际数据，结构就是你上一节刚发现的那个。

[46] 如下所示，`pub` 命令有四种主要用法。不过，c 和 d 里描述的自补全功能在 Windows 上不受支持。

*a. **发布字典字符串**：*

[47] 要向话题发布数据，你需要以 YAML 字符串的形式传入数据。

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}"
```

[48] 不过，你不必指定整条消息；如果你只是想改线速度或角速度，只需要写出你想改的值。

[49] 例如，如果你想把线速度改成 2.0、把角速度保持为 1.8，可以这样做：

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 1.8}}"
```

*b. **发布空消息**：*

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist
```

[50] 这会以 1 Hz 的频率发布该消息类型的默认值。在这个例子里，它等价于下面这条命令：

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --rate 1
```

*c. **使用自动补全**：*

[51] 你可以在终端里这样触发自动补全功能：

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist <TAB>
```

[52] 输入选项的前几个字符后按 **Tab** 键，所有选项都会被自动补全。

[53] 不过，话题消息的模板只有在输入 `\'<TAB>` 之后才会补全。

[54] 这是因为终端不把单引号当作自动补全字符串的一部分。因此需要用 `\'` 转义，它才会被识别为字符串的一部分。

[55] 最终补全出来的字符串看起来像这样：

```
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist 'linear:
  x: 0.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
'
```

[56] 这个字符串是可编辑的，你可以按需要修改消息类型各字段的值。

*d. **使用原始的自动补全字符串**：*

[57] 如上所述，`geometry_msgs/msg/Twist` 自动补全出来的字符串是这样的：

```
\'linear:\^J\ \ x:\ 0.0\^J\ \ y:\ 0.0\^J\ \ z:\ 0.0\^Jangular:\^J\ \ x:\ 0.0\^J\ \ y:\ 0.0\^J\ \ z:\ 0.0\^J\'
```

[58] 它可以直接用在命令行里，替代 YAML 字符串。

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist \'linear:\^J\ \ x:\ 0.0\^J\ \ y:\ 0.0\^J\ \ z:\ 0.0\^Jangular:\^J\ \ x:\ 0.0\^J\ \ y:\ 0.0\^J\ \ z:\ 0.0\^J\'
```

[59] 海龟（以及它通常要模拟的真实机器人）需要持续不断的命令流才能持续运动。所以，要让海龟动起来并保持运动，你可以用下面这个字典字符串：

```
$ ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}"
```

[60] 有时你可能只想向话题发布一次数据（而不是持续发布）。要只发布一次命令，加上 `--once` 选项。

```
$ ros2 topic pub --once -w 2 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}"
```

[61] `--once` 是一个可选参数，意思是“发布一条消息然后退出”。

[62] `-w 2` 是一个可选参数，意思是“等待两个匹配的订阅”。这里需要它，是因为 turtlesim 和 topic echo 都订阅了。

[63] 你会在终端里看到下面的输出：

```
Waiting for at least 2 matching subscription(s)...
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=1.8))
```

[64] 然后你会看到海龟这样移动：

[65] 你可以刷新 rqt_graph，看看图形上发生了什么。你会看到 `ros2 topic pub ...` 节点（`/_ros2cli_30358`）正在通过 `/turtle1/cmd_vel` 话题发布，而 `ros2 topic echo ...` 节点（`/_ros2cli_26646`）和 `/turtlesim` 节点现在都在接收它。

[66] 最后，你可以对 `pose` 话题运行 `echo`，再检查一次 rqt_graph：

```
$ ros2 topic echo /turtle1/pose
```

[67] 你能看到 `/turtlesim` 节点也在向 `pose` 话题发布，而新的 `echo` 节点订阅了它。

[68] 发布带时间戳的消息时，`pub` 有两种方法用当前时间自动填写时间戳。对于带 `std_msgs/msg/Header` 的消息，可以把 header 字段设为 `auto`，来自动填写 `stamp` 字段。

```
$ ros2 topic pub /pose geometry_msgs/msg/PoseStamped '{header: "auto", pose: {position: {x: 1.0, y: 2.0, z: 3.0}}}'
```

[69] 如果消息不使用完整的 header，而只是有一个 `builtin_interfaces/msg/Time` 类型的字段，可以把它设为 `now`。

```
$ ros2 topic pub /reference sensor_msgs/msg/TimeReference '{header: "auto", time_ref: "now", source: "dumy"}'
```

*8 ros2 topic hz*

[70] 你也可以用下面的命令查看数据发布的频率：

```
$ ros2 topic hz /turtle1/pose
average rate: 59.354
  min: 0.005s max: 0.027s std dev: 0.00284s window: 58
```

[71] 它会返回 `/turtlesim` 节点向 `pose` 话题发布数据的频率信息。

[72] 回想一下，你用 `ros2 topic pub --rate 1` 把 `turtle1/cmd_vel` 的发布频率设成了稳定的 1 Hz。如果你把上面命令里的 `turtle1/pose` 换成 `turtle1/cmd_vel`，就会看到反映该频率的平均值。

> **注意：** 这个频率反映的是 `ros2 topic hz` 命令所创建的订阅端的接收频率；它可能受平台资源和 QoS 配置影响，未必与发布频率完全一致。

*9 ros2 topic bw*

[73] 可以用下面的命令查看某个话题占用的带宽：

```
$ ros2 topic bw /turtle1/pose
Subscribed to [/turtle1/pose]
1.51 KB/s from 62 messages
    Message size mean: 0.02 KB min: 0.02 KB max: 0.02 KB
```

[74] 它返回 `/turtle1/pose` 话题的带宽占用和正在发布的消息数量。

> **注意：** 带宽反映的是 `ros2 topic bw` 命令所创建的订阅端的接收速率；它可能受平台资源和 QoS 配置影响，未必与发布端的带宽完全一致。

*10 ros2 topic find*

[75] 要列出某个给定类型的可用话题，用：

```
$ ros2 topic find <topic_type>
```

[76] 回想一下，`cmd_vel` 话题的类型是：

```
geometry_msgs/msg/Twist
```

[77] 给 `find` 命令提供消息类型，它就会输出可用的话题：

```
$ ros2 topic find geometry_msgs/msg/Twist
/turtle1/cmd_vel
```

*11 清理*

[78] 到这一步，你会有很多节点在运行。别忘了在每个终端里按 `Ctrl+C` 把它们停掉。

**小结**

[79] 节点通过话题发布信息，这允许任意数量的其他节点订阅并获取这些信息。

[80] 在本教程中，你用 rqt_graph 和命令行工具检查了若干节点之间通过话题建立的连接。现在你应该对数据如何在 ROS 2 系统中流动有了较好的认识。

**下一步**

[81] 接下来，你会通过“理解服务”教程了解 ROS 图中的另一种通信类型。

### 读法补充

**这一节真正的骨架**：发布者 + 话题名 + 消息类型 + 订阅者。四个要素里任意一个对不上，就收不到数据。`topic list -t` 看的是“话题名 + 类型”，`topic info --verbose` 看的是“谁在发、谁在收、QoS 是否匹配”，`echo` 看的是“内容长什么样”，`hz`/`bw` 看的是“发得多快、多占带宽”。

**术语**

| 英文 | 意思 | 备注 |
|---|---|---|
| introspection | 内省：查看运行中系统的内部状态 | `rqt_graph` 是图形化内省，`topic info` 是命令行内省 |
| QoS profile | 服务质量配置：可靠性、历史深度、持久性等 | 发布者与订阅者的 QoS 不兼容时，即使名字和类型都对，也可能收不到 |
| Publisher count / Subscription count | 发布者数量 / 订阅者数量 | 不是消息条数 |
| rate | 频率，单位 Hz | `hz` 的 `window: 58` 是统计窗口内的消息数 |

**长句拆解**

- [22] `These attributes, particularly the type, are how nodes know they're talking about the same information as it moves over topics.` 主干是 `These attributes are how nodes know ...`；`particularly the type` 是插入语；`as it moves over topics` 是时间状语，“当信息在话题上流动时”。
- [62] `This is needed because we have both turtlesim and the topic echo subscribed.` `have both A and B subscribed` 是“让 A 和 B 都处于订阅状态”；`because` 从句解释为什么需要 `-w 2`。
- [68] `For messages with a std_msgs/msg/Header, the header field can be set to auto to fill out the stamp field.` `For messages with ...` 是“对于带……的消息”；`be set to auto to fill out ...` 两个 to 不同：第一个是“被设为”，第二个表目的。

**读的时候注意**

- `ros2 topic pub` 默认是**持续发布**（默认 1 Hz），按 `Ctrl+C` 才停；只想发一次必须加 `--once`。这是第 3 题里“四行数据可能在发现完成前就发完”的根源。
- `-w 2` 的“wait for two matching subscriptions”是在等**匹配的订阅者出现**，不是在等它们处理完。它只解决“发的时候有没有人听”，不解决“听完有没有处理”。
- `topic info --verbose` 里发布者的 `History (Depth): KEEP_LAST (7)`、订阅者的 `KEEP_LAST (5)`，就是 `create_publisher(..., 10)` 那个队列深度在运行时的样子；后面 ROS-03 会展开 QoS 匹配。
- `echo` 命令本身会创建临时节点（输出里的 `_ros2cli_26646`），所以 `topic info` 的订阅者数量会比你“以为的”多一个。这不是 bug。

---

<a id="services"></a>

## 3. Understanding services（理解服务）

原文：[Understanding-ROS2-Services.rst](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Services/Understanding-ROS2-Services.rst)

**Goal:** Learn about services in ROS 2 using command line tools.

**Tutorial level:** Beginner

**Time:** 10 minutes

### 原文

**Background**

[1] Services are another method of communication for nodes in the ROS graph. Services are based on a call-and-response model versus the publisher-subscriber model of topics.

[2] While topics allow nodes to subscribe to data streams and get continual updates, services only provide data when they are specifically called by a client.

**Prerequisites**

[3] Some concepts mentioned in this tutorial, like Nodes and Topics, were covered in previous tutorials in the series.

[4] You will need the turtlesim package.

[5] As always, don't forget to source ROS 2 in every new terminal you open.

**Tasks**

*1 Setup*

[6] Start up the two turtlesim nodes, `/turtlesim` and `/teleop_turtle`.

[7] Open a new terminal and run:

```
$ ros2 run turtlesim turtlesim_node
```

[8] Open another terminal and run:

```
$ ros2 run turtlesim turtle_teleop_key
```

*2 ros2 service list*

[9] Running the `ros2 service list` command in a new terminal will return a list of all the services currently active in the system:

```
$ ros2 service list
/clear
/kill
/reset
/spawn
/teleop_turtle/describe_parameters
/teleop_turtle/get_parameter_types
/teleop_turtle/get_parameters
/teleop_turtle/list_parameters
/teleop_turtle/set_parameters
/teleop_turtle/set_parameters_atomically
/turtle1/set_pen
/turtle1/teleport_absolute
/turtle1/teleport_relative
/turtlesim/describe_parameters
/turtlesim/get_parameter_types
/turtlesim/get_parameters
/turtlesim/list_parameters
/turtlesim/set_parameters
/turtlesim/set_parameters_atomically
```

[10] You will see that both nodes have the same six services with `parameters` in their names.

[11] Nearly every node in ROS 2 has these infrastructure services that parameters are built off of. There will be more about parameters in the next tutorial.

[12] In this tutorial, the parameter services will be omitted from the discussion.

[13] For now, let's focus on the turtlesim-specific services, `/clear`, `/kill`, `/reset`, `/spawn`, `/turtle1/set_pen`, `/turtle1/teleport_absolute`, and `/turtle1/teleport_relative`.

[14] You may recall interacting with some of these services using rqt in the "Use turtlesim, ros2, and rqt" tutorial.

*3 ros2 service type*

[15] Services have types that describe how the request and response data of a service is structured. Service types are defined similarly to topic types, except service types have two parts: one message for the request and another for the response.

[16] To find out the type of a service, use the command:

```
$ ros2 service type <service_name>
```

[17] Let's take a look at turtlesim's `/clear` service. In a new terminal, enter the command:

```
$ ros2 service type /clear
std_srvs/srv/Empty
```

[18] The `Empty` type means the service call sends no data when making a request and receives no data when receiving a response.

*3.1 ros2 service list -t*

[19] To see the types of all the active services at the same time, you can append the `--show-types` option, abbreviated as `-t`, to the `list` command:

```
$ ros2 service list -t
/clear [std_srvs/srv/Empty]
/kill [turtlesim/srv/Kill]
/reset [std_srvs/srv/Empty]
/spawn [turtlesim/srv/Spawn]
...
/turtle1/set_pen [turtlesim/srv/SetPen]
/turtle1/teleport_absolute [turtlesim/srv/TeleportAbsolute]
/turtle1/teleport_relative [turtlesim/srv/TeleportRelative]
...
```

*4 ros2 service info*

[20] To see information of a particular service, use the command:

```
$ ros2 service info <service_name>
```

[21] This returns the service type and the count of service clients and servers.

[22] For example, you can find the count of clients and servers for the `/clear` service:

```
$ ros2 service info /clear
Type: std_srvs/srv/Empty
Clients count: 0
Services count: 1
```

*5 ros2 service find*

[23] If you want to find all the services of a specific type, you can use the command:

```
$ ros2 service find <type_name>
```

[24] For example, you can find all the `Empty` typed services like this:

```
$ ros2 service find std_srvs/srv/Empty
/clear
/reset
```

*6 ros2 interface show*

[25] You can call services from the command line, but first you need to know the structure of the input arguments.

```
$ ros2 interface show <type_name>
```

[26] Try this on the `/clear` service's type, `Empty`:

```
$ ros2 interface show std_srvs/srv/Empty
---
```

[27] The `---` separates the request structure (above) from the response structure (below).

[28] But, as you learned earlier, the `Empty` type doesn't send or receive any data. So, naturally, its structure is blank.

[29] Let's introspect a service with a type that sends and receives data, like `/spawn`. From the results of `ros2 service list -t`, we know `/spawn`'s type is `turtlesim/srv/Spawn`.

[30] To see the request and response arguments of the `/spawn` service, run the command:

```
$ ros2 interface show turtlesim/srv/Spawn
float32 x
float32 y
float32 theta
string name # Optional.  A unique name will be created and returned if this is empty
---
string name
```

[31] The information above the `---` line tells us the arguments needed to call `/spawn`. `x`, `y` and `theta` determine the 2D pose of the spawned turtle, and `name` is clearly optional.

[32] The information below the line isn't something you need to know in this case, but it can help you understand the data type of the response you get from the call.

*7 ros2 service call*

[33] Now that you know what a service type is, how to find a service's type, and how to find the structure of that type's arguments, you can call a service using:

```
$ ros2 service call <service_name> <service_type> <arguments>
```

[34] The `<arguments>` part is optional. For example, you know that `Empty` typed services don't have any arguments:

```
$ ros2 service call /clear std_srvs/srv/Empty
```

[35] This command will clear the turtlesim window of any lines your turtle has drawn.

[36] Now let's spawn a new turtle by calling `/spawn` and setting arguments. Input `<arguments>` in a service call from the command-line need to be in YAML syntax.

[37] Enter the command:

```
$ ros2 service call /spawn turtlesim/srv/Spawn "{x: 2, y: 2, theta: 0.2, name: ''}"
requester: making request: turtlesim.srv.Spawn_Request(x=2.0, y=2.0, theta=0.2, name='')

response:
turtlesim.srv.Spawn_Response(name='turtle2')
```

[38] You will get this method-style view of what's happening, and then the service response.

[39] Your turtlesim window will update with the newly spawned turtle right away:

*8 ros2 service echo*

[40] To see the data communication between a service client and a service server you can `echo` the service using:

```
$ ros2 service echo <service_name | service_type> <arguments>
```

[41] `ros2 service echo` depends on service introspection of a service client and server, that is disabled by default.

[42] To enable it, users must call `configure_introspection` after creating a service client or server.

[43] Start up the `introspection_client` and `introspection_service` service introspection demo.

```
$ ros2 launch demo_nodes_cpp introspect_services_launch.py
```

[44] Open another terminal and run the following to enable service introspection for `introspection_client` and `introspection_service`.

```
$ ros2 param set /introspection_service service_configure_introspection contents
$ ros2 param set /introspection_client client_configure_introspection contents
```

[45] Now we are able to see the service communication between `introspection_client` and `introspection_service` via `ros2 service echo`.

```
$ ros2 service echo --flow-style /add_two_ints
 info:
   event_type: REQUEST_SENT
   stamp:
     sec: 1709408301
     nanosec: 423227292
   client_gid: [1, 15, 0, 18, 250, 205, 12, 100, 0, 0, 0, 0, 0, 0, 21, 3]
   sequence_number: 618
 request: [{a: 2, b: 3}]
 response: []
 ---
 info:
   event_type: REQUEST_RECEIVED
   stamp:
     sec: 1709408301
     nanosec: 423601471
   client_gid: [1, 15, 0, 18, 250, 205, 12, 100, 0, 0, 0, 0, 0, 0, 20, 4]
   sequence_number: 618
 request: [{a: 2, b: 3}]
 response: []
 ---
 info:
   event_type: RESPONSE_SENT
   stamp:
     sec: 1709408301
     nanosec: 423900744
   client_gid: [1, 15, 0, 18, 250, 205, 12, 100, 0, 0, 0, 0, 0, 0, 20, 4]
   sequence_number: 618
 request: []
 response: [{sum: 5}]
 ---
 info:
   event_type: RESPONSE_RECEIVED
   stamp:
     sec: 1709408301
     nanosec: 424153133
   client_gid: [1, 15, 0, 18, 250, 205, 12, 100, 0, 0, 0, 0, 0, 0, 21, 3]
   sequence_number: 618
 request: []
 response: [{sum: 5}]
 ---
```

**Summary**

[46] Nodes can communicate using services in ROS 2. Unlike a topic - a one way communication pattern where a node publishes information that can be consumed by one or more subscribers - a service is a request/response pattern where a client makes a request to a node providing the service and the service processes the request and generates a response.

[47] You generally don't want to use a service for continuous calls; topics or even actions would be better suited.

[48] In this tutorial you used command line tools to identify, introspect, and call services.

**Next steps**

[49] In the next tutorial, you will learn about configuring node settings.

**Related content**

[50] Check out this tutorial; it's an excellent realistic application of ROS services using a Robotis robot arm.

### 译文

**背景**

[1] 服务是 ROS 图中节点之间另一种通信方式。服务基于调用—响应模型，而话题基于发布—订阅模型。

[2] 话题允许节点订阅数据流并持续获得更新，而服务只在被客户端明确调用时才提供数据。

**前置条件**

[3] 本教程提到的某些概念，比如节点和话题，已在此前教程中讲过。

[4] 你会需要 turtlesim 包。

[5] 和往常一样，别忘了在你打开的每一个新终端里 source 一下 ROS 2。

**任务**

*1 准备*

[6] 启动两个 turtlesim 节点，`/turtlesim` 和 `/teleop_turtle`。

[7] 打开一个新终端并运行：

```
$ ros2 run turtlesim turtlesim_node
```

[8] 打开另一个终端并运行：

```
$ ros2 run turtlesim turtle_teleop_key
```

*2 ros2 service list*

[9] 在一个新终端里运行 `ros2 service list`，会返回系统中当前所有活动的服务：

```
$ ros2 service list
/clear
/kill
/reset
/spawn
/teleop_turtle/describe_parameters
/teleop_turtle/get_parameter_types
/teleop_turtle/get_parameters
/teleop_turtle/list_parameters
/teleop_turtle/set_parameters
/teleop_turtle/set_parameters_atomically
/turtle1/set_pen
/turtle1/teleport_absolute
/turtle1/teleport_relative
/turtlesim/describe_parameters
/turtlesim/get_parameter_types
/turtlesim/get_parameters
/turtlesim/list_parameters
/turtlesim/set_parameters
/turtlesim/set_parameters_atomically
```

[10] 你会看到两个节点都有同样六个名字里带 `parameters` 的服务。

[11] ROS 2 中几乎每个节点都有这些基础设施服务，参数功能就建立在它们之上。下一节教程会更多地讲参数。

[12] 在本教程中，参数相关的服务不讨论。

[13] 现在，我们专注于 turtlesim 特有的服务：`/clear`、`/kill`、`/reset`、`/spawn`、`/turtle1/set_pen`、`/turtle1/teleport_absolute` 和 `/turtle1/teleport_relative`。

[14] 你可能记得，在“使用 turtlesim、ros2 和 rqt”教程里用 rqt 接触过其中一些服务。

*3 ros2 service type*

[15] 服务有类型，类型描述了一个服务的请求数据和响应数据如何组织。服务类型的定义方式与话题类型类似，区别在于服务类型有两部分：一个用于请求的消息，另一个用于响应的消息。

[16] 要查某个服务的类型，用：

```
$ ros2 service type <service_name>
```

[17] 我们来看看 turtlesim 的 `/clear` 服务。在一个新终端里输入：

```
$ ros2 service type /clear
std_srvs/srv/Empty
```

[18] `Empty` 类型意味着这个服务调用在发出请求时不发送任何数据，接收响应时也不接收任何数据。

*3.1 ros2 service list -t*

[19] 要同时看到所有活动服务的类型，可以在 `list` 命令后加上 `--show-types` 选项，简写为 `-t`：

```
$ ros2 service list -t
/clear [std_srvs/srv/Empty]
/kill [turtlesim/srv/Kill]
/reset [std_srvs/srv/Empty]
/spawn [turtlesim/srv/Spawn]
...
/turtle1/set_pen [turtlesim/srv/SetPen]
/turtle1/teleport_absolute [turtlesim/srv/TeleportAbsolute]
/turtle1/teleport_relative [turtlesim/srv/TeleportRelative]
...
```

*4 ros2 service info*

[20] 要查看某个特定服务的信息，用：

```
$ ros2 service info <service_name>
```

[21] 它返回服务类型，以及服务客户端和服务端的数量。

[22] 例如，你可以查看 `/clear` 服务的客户端和服务端数量：

```
$ ros2 service info /clear
Type: std_srvs/srv/Empty
Clients count: 0
Services count: 1
```

*5 ros2 service find*

[23] 如果你想找出所有属于某个特定类型的服务，可以用：

```
$ ros2 service find <type_name>
```

[24] 例如，你可以这样找出所有 `Empty` 类型的服务：

```
$ ros2 service find std_srvs/srv/Empty
/clear
/reset
```

*6 ros2 interface show*

[25] 你可以从命令行调用服务，但首先需要知道输入参数的结构。

```
$ ros2 interface show <type_name>
```

[26] 在 `/clear` 服务的类型 `Empty` 上试试：

```
$ ros2 interface show std_srvs/srv/Empty
---
```

[27] `---` 把请求结构（上面）和响应结构（下面）分开。

[28] 但正如你前面学到的，`Empty` 类型不发送也不接收任何数据。所以它的结构自然是空的。

[29] 我们来内省一个会收发数据的服务，比如 `/spawn`。从 `ros2 service list -t` 的结果可知，`/spawn` 的类型是 `turtlesim/srv/Spawn`。

[30] 要查看 `/spawn` 服务的请求和响应参数，运行：

```
$ ros2 interface show turtlesim/srv/Spawn
float32 x
float32 y
float32 theta
string name # Optional.  A unique name will be created and returned if this is empty
---
string name
```

[31] `---` 之上的信息告诉我们调用 `/spawn` 所需的参数。`x`、`y` 和 `theta` 决定新生成海龟的二维位姿，`name` 显然是可选的。

[32] 在这个例子里，线下的信息不是你必须要知道的，但它能帮你理解调用返回的响应是什么数据类型。

*7 ros2 service call*

[33] 现在你知道了什么是服务类型、如何查找服务的类型、如何查找该类型参数的结构，就可以用下面的方式调用服务：

```
$ ros2 service call <service_name> <service_type> <arguments>
```

[34] `<arguments>` 部分是可选的。例如，你知道 `Empty` 类型的服务没有任何参数：

```
$ ros2 service call /clear std_srvs/srv/Empty
```

[35] 这条命令会清除 turtlesim 窗口里海龟画出的所有线条。

[36] 现在我们来调用 `/spawn` 并设置参数，生成一只新海龟。命令行里服务调用的 `<arguments>` 需要使用 YAML 语法。

[37] 输入命令：

```
$ ros2 service call /spawn turtlesim/srv/Spawn "{x: 2, y: 2, theta: 0.2, name: ''}"
requester: making request: turtlesim.srv.Spawn_Request(x=2.0, y=2.0, theta=0.2, name='')

response:
turtlesim.srv.Spawn_Response(name='turtle2')
```

[38] 你会看到这种“方法调用式”的过程视图，然后是服务响应。

[39] 你的 turtlesim 窗口会立刻更新，出现新生成的海龟。

*8 ros2 service echo*

[40] 要查看服务客户端和服务端之间的数据通信，可以用下面的命令 echo 服务：

```
$ ros2 service echo <service_name | service_type> <arguments>
```

[41] `ros2 service echo` 依赖于服务客户端和服务端的服务内省（service introspection），而该功能默认关闭。

[42] 要启用它，用户必须在创建服务客户端或服务端之后调用 `configure_introspection`。

[43] 启动 `introspection_client` 和 `introspection_service` 这两个服务内省示例。

```
$ ros2 launch demo_nodes_cpp introspect_services_launch.py
```

[44] 打开另一个终端，运行下面命令，为 `introspection_client` 和 `introspection_service` 启用服务内省。

```
$ ros2 param set /introspection_service service_configure_introspection contents
$ ros2 param set /introspection_client client_configure_introspection contents
```

[45] 现在我们就能通过 `ros2 service echo` 看到 `introspection_client` 和 `introspection_service` 之间的服务通信了。

（输出见原文；四次事件依次是 REQUEST_SENT、REQUEST_RECEIVED、RESPONSE_SENT、RESPONSE_RECEIVED，请求 `{a: 2, b: 3}`，响应 `{sum: 5}`。）

**小结**

[46] 节点可以在 ROS 2 中使用服务通信。话题是一种单向通信模式：一个节点发布信息，一个或多个订阅者消费这些信息；与它不同，服务是一种请求/响应模式：客户端向提供服务的节点发出请求，服务处理请求并生成响应。

[47] 你通常不会用服务做持续调用；话题甚至动作会更合适。

[48] 本教程中，你用命令行工具识别、内省并调用了服务。

**下一步**

[49] 下一节教程中，你会学到如何配置节点设置。

**相关内容**

[50] 看看这个教程；它用 Robotis 机械臂展示了 ROS 服务的一个很好的实际应用。

### 读法补充

**服务与话题的差别，一句话版**：话题是“我一直发，谁爱听谁听”；服务是“你问我，我才答，而且只答这一次”。所以服务不适合当状态流用——想知道当前关节角，不该每秒调用一次服务，而应该订阅状态话题。

**术语**

| 英文 | 意思 | 注意 |
|---|---|---|
| call-and-response | 调用—响应 | 强调“有请求才有响应” |
| request / response | 请求 / 响应 | 服务类型被 `---` 分成这两段 |
| service client / service server | 服务客户端 / 服务端 | 客户端发请求，服务端处理并回应 |
| spawn | 生成（这里指生成一只新海龟） | 不是“孵化” |
| teleport | 瞬移 | `teleport_absolute` 用绝对坐标，`teleport_relative` 用相对位移 |

**长句拆解**

- [1] `Services are based on a call-and-response model versus the publisher-subscriber model of topics.` `versus` 在这里是“与……相对/相比”，不是“对抗”；整句在对比两种模型。
- [46] 这句很长，骨架是 `Unlike a topic ..., a service is a request/response pattern where ...`。两个破折号之间是对 topic 的解释（单向、一个发布者、一个或多个订阅者）；`where` 从句解释 request/response pattern 具体怎么运作。

**读的时候注意**

- `service info /clear` 输出 `Services count: 1`，指的是**服务端**数量。同一个服务名可以有多个客户端，但通常只有一个服务端；服务端退出后，客户端调用会失败。
- `Empty` 的 `interface show` 只输出一行 `---`，这不是“没输出”，而是请求和响应都为空。看懂这一点，再看 `Spawn` 的 `x/y/theta/name` 就顺了。
- `ros2 service call` 的响应里 `name='turtle2'` 是**服务端生成并返回**的，不是你传进去的 `''`。这正好说明“请求”和“响应”是两份不同的数据。
- 第 4 题会用到 `AddTwoInts`：它的请求是 `int64 a`、`int64 b`，响应是 `int64 sum`。你可以先用 `ros2 interface show example_interfaces/srv/AddTwoInts` 看结构，再 `ros2 service call` 调一次，体会“请求字段”和“响应字段”的对应。

---

<a id="actions"></a>

## 4. Understanding actions（理解动作）

原文：[Understanding-ROS2-Actions.rst](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Actions/Understanding-ROS2-Actions.rst)

**Goal:** Introspect actions in ROS 2.

**Tutorial level:** Beginner

**Time:** 15 minutes

### 原文

**Background**

[1] Actions are one of the communication types in ROS 2 and are intended for long running tasks. They consist of three parts: a goal, feedback, and a result.

[2] Actions are built on topics and services. Their functionality is similar to services, except actions can be canceled. They also provide steady feedback, as opposed to services which return a single response.

[3] Actions use a client-server model, similar to the publisher-subscriber model (described in the topics tutorial). An "action client" node sends a goal to an "action server" node that acknowledges the goal and returns a stream of feedback and a result.

**Prerequisites**

[4] This tutorial builds off concepts, like nodes and topics, covered in previous tutorials.

[5] This tutorial uses the turtlesim package.

[6] As always, don't forget to source ROS 2 in every new terminal you open.

**Tasks**

*1 Setup*

[7] Start up the two turtlesim nodes, `/turtlesim` and `/teleop_turtle`.

[8] Open a new terminal and run:

```
$ ros2 run turtlesim turtlesim_node
```

[9] Open another terminal and run:

```
$ ros2 run turtlesim turtle_teleop_key
```

*2 Use actions*

[10] When you launch the `/teleop_turtle` node, you will see the following message in your terminal:

```
Use arrow keys to move the turtle.
Use G|B|V|C|D|E|R|T keys to rotate to absolute orientations. 'F' to cancel a rotation.
```

[11] Let's focus on the second line, which corresponds to an action. (The first instruction corresponds to the "cmd_vel" topic, discussed previously in the topics tutorial.)

[12] Notice that the letter keys `G|B|V|C|D|E|R|T` form a "box" around the `F` key on a US QWERTY keyboard (if you are not using a QWERTY keyboard, see this link to follow along).

[13] Each key's position around `F` corresponds to that orientation in turtlesim. For example, the `E` will rotate the turtle's orientation to the upper left corner.

[14] Pay attention to the terminal where the `/turtlesim` node is running. Each time you press one of these keys, you are sending a goal to an action server that is part of the `/turtlesim` node.

[15] The goal is to rotate the turtle to face a particular direction. A message relaying the result of the goal should display once the turtle completes its rotation:

```
[INFO] [turtlesim]: Rotation goal completed successfully
```

[16] The `F` key will cancel a goal mid-execution.

[17] Try pressing the `C` key, and then pressing the `F` key before the turtle can complete its rotation. In the terminal where the `/turtlesim` node is running, you will see the message:

```
[INFO] [turtlesim]: Rotation goal canceled
```

[18] Not only can the client-side (your input in the teleop) stop a goal, but the server-side (the `/turtlesim` node) can as well. When the server-side chooses to stop processing a goal, it is said to "abort" the goal.

[19] Try hitting the `D` key, then the `G` key before the first rotation can complete. In the terminal where the `/turtlesim` node is running, you will see the message:

```
[WARN] [turtlesim]: Rotation goal received before a previous goal finished. Aborting previous goal
```

[20] This action server chose to abort the first goal because it got a new one. It could have chosen something else, like reject the new goal or execute the second goal after the first one finished.

[21] Don't assume every action server will choose to abort the current goal when it gets a new one.

*3 ros2 node info*

[22] To see the list of actions a node provides, `/turtlesim` in this case, open a new terminal and run the command:

```
$ ros2 node info /turtlesim
/turtlesim
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim/msg/Color
    /turtle1/pose: turtlesim/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim/srv/Kill
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim/srv/Spawn
    /turtle1/set_pen: turtlesim/srv/SetPen
    /turtle1/teleport_absolute: turtlesim/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim/srv/TeleportRelative
    /turtlesim/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /turtlesim/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /turtlesim/get_parameters: rcl_interfaces/srv/GetParameters
    /turtlesim/list_parameters: rcl_interfaces/srv/ListParameters
    /turtlesim/set_parameters: rcl_interfaces/srv/SetParameters
    /turtlesim/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
  Action Clients:
```

[23] The command returns a list of `/turtlesim`'s subscribers, publishers, services, action servers and action clients.

[24] Notice that the `/turtle1/rotate_absolute` action for `/turtlesim` is under `Action Servers`. This means `/turtlesim` responds to and provides feedback for the `/turtle1/rotate_absolute` action.

[25] The `/teleop_turtle` node has the name `/turtle1/rotate_absolute` under `Action Clients` meaning that it sends goals for that action name. To see that, run:

```
$ ros2 node info /teleop_turtle
/teleop_turtle
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Service Servers:
    /teleop_turtle/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /teleop_turtle/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /teleop_turtle/get_parameters: rcl_interfaces/srv/GetParameters
    /teleop_turtle/list_parameters: rcl_interfaces/srv/ListParameters
    /teleop_turtle/set_parameters: rcl_interfaces/srv/SetParameters
    /teleop_turtle/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:

  Action Clients:
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
```

*4 ros2 action list*

[26] To identify all the actions in the ROS graph, run the command:

```
$ ros2 action list
/turtle1/rotate_absolute
```

[27] This is the only action in the ROS graph right now. It controls the turtle's rotation, as you saw earlier. You also already know that there is one action client (part of `/teleop_turtle`) and one action server (part of `/turtlesim`) for this action from using the `ros2 node info <node_name>` command.

*4.1 ros2 action list -t*

[28] Actions have types, similar to topics and services. To find `/turtle1/rotate_absolute`'s type, run the command:

```
$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]
```

[29] In brackets to the right of each action name (in this case only `/turtle1/rotate_absolute`) is the action type, `turtlesim/action/RotateAbsolute`. You will need this when you want to execute an action from the command line or from code.

*5 ros2 action type*

[30] If you want to check the action type for the action, run the command:

```
$ ros2 action type /turtle1/rotate_absolute
turtlesim/action/RotateAbsolute
```

*6 ros2 action info*

[31] You can further introspect the `/turtle1/rotate_absolute` action with the command:

```
$ ros2 action info /turtle1/rotate_absolute
Action: /turtle1/rotate_absolute
Action clients: 1
    /teleop_turtle
Action servers: 1
    /turtlesim
```

[32] This tells us what we learned earlier from running `ros2 node info` on each node: The `/teleop_turtle` node has an action client and the `/turtlesim` node has an action server for the `/turtle1/rotate_absolute` action.

*7 ros2 interface show*

[33] One more piece of information you will need before sending or executing an action goal yourself is the structure of the action type.

[34] Recall that you identified `/turtle1/rotate_absolute`'s type when running the command `ros2 action list -t`. Enter the following command with the action type in your terminal:

```
$ ros2 interface show turtlesim/action/RotateAbsolute
```

[35] Which will return:

```
# The desired heading in radians
float32 theta
---
# The angular displacement in radians to the starting position
float32 delta
---
# The remaining rotation in radians
float32 remaining
```

[36] The section of this message above the first `---` is the structure (data type and name) of the goal request. The next section is the structure of the result. The last section is the structure of the feedback.

*8 ros2 action send_goal*

[37] Now let's send an action goal from the command line with the following syntax:

```
$ ros2 action send_goal <action_name> <action_type> <values>
```

[38] `<values>` need to be in YAML format.

[39] Keep an eye on the turtlesim window, and enter the following command into your terminal:

```
$ ros2 action send_goal /turtle1/rotate_absolute turtlesim/action/RotateAbsolute "{theta: 1.57}"
Waiting for an action server to become available...
Sending goal:
   theta: 1.57

Goal accepted with ID: f8db8f44410849eaa93d3feb747dd444

Result:
  delta: -1.568000316619873

Goal finished with status: SUCCEEDED
```

[40] You should see the turtle rotating.

[41] All goals have a unique ID, shown in the return message. You can also see the result, a field with the name `delta`, which is the displacement to the starting position.

[42] To see the feedback of this goal, add `--feedback` to the `ros2 action send_goal` command:

```
$ ros2 action send_goal /turtle1/rotate_absolute turtlesim/action/RotateAbsolute "{theta: -1.57}" --feedback
Sending goal:
   theta: -1.57

Goal accepted with ID: e6092c831f994afda92f0086f220da27

Feedback:
  remaining: -3.1268222332000732

Feedback:
  remaining: -3.1108222007751465

…

Result:
  delta: 3.1200008392333984

Goal finished with status: SUCCEEDED
```

[43] You will continue to receive feedback, the remaining radians, until the goal is complete.

**Summary**

[44] Actions are like services that allow you to execute long running tasks, provide regular feedback, and are cancelable.

[45] A robot system would likely use actions for navigation. An action goal could tell a robot to travel to a position. While the robot navigates to the position, it can send updates along the way (i.e. feedback), and then a final result message once it's reached its destination.

[46] Turtlesim has an action server that action clients can send goals to for rotating turtles. In this tutorial, you introspected that action, `/turtle1/rotate_absolute`, to get a better idea of what actions are and how they work.

**Next steps**

[47] Now you've covered all of the core ROS 2 concepts. The last few tutorials in this set will introduce you to some tools and techniques that will make using ROS 2 easier, starting with Using Rqt Console.

**Related content**

[48] You can read more about the design decisions behind actions in ROS 2 here.

### 译文

**背景**

[1] 动作是 ROS 2 中的通信类型之一，面向长时间运行的任务。它由三部分组成：目标（goal）、反馈（feedback）和结果（result）。

[2] 动作建立在话题和服务之上。它的功能与服务类似，区别在于动作可以被取消。它还提供稳定的反馈，而服务只返回一次响应。

[3] 动作使用客户端—服务器模型，类似于发布—订阅模型（话题教程里描述过）。一个“动作客户端”节点向一个“动作服务器”节点发送目标，后者确认该目标，并返回一串反馈和一个结果。

**前置条件**

[4] 本教程建立在前面教程讲过的节点和话题等概念之上。

[5] 本教程使用 turtlesim 包。

[6] 和往常一样，别忘了在你打开的每一个新终端里 source 一下 ROS 2。

**任务**

*1 准备*

[7] 启动两个 turtlesim 节点，`/turtlesim` 和 `/teleop_turtle`。

[8] 打开一个新终端并运行：

```
$ ros2 run turtlesim turtlesim_node
```

[9] 打开另一个终端并运行：

```
$ ros2 run turtlesim turtle_teleop_key
```

*2 使用动作*

[10] 启动 `/teleop_turtle` 节点时，你会在终端看到下面的消息：

```
Use arrow keys to move the turtle.
Use G|B|V|C|D|E|R|T keys to rotate to absolute orientations. 'F' to cancel a rotation.
```

[11] 我们重点关注第二行，它对应一个动作。（第一条指令对应 `cmd_vel` 话题，前面话题教程里讨论过。）

[12] 注意，字母键 `G|B|V|C|D|E|R|T` 在美式 QWERTY 键盘上围绕 `F` 键组成一个“方框”（如果你用的不是 QWERTY 键盘，可以看这个链接对照）。

[13] 每个键相对于 `F` 的位置，对应 turtlesim 中的那个朝向。例如，`E` 会把海龟的朝向转到左上角。

[14] 注意运行 `/turtlesim` 节点的那个终端。每次你按这些键之一，你都是在向 `/turtlesim` 节点内部的一个动作服务器发送目标。

[15] 这个目标是让海龟转到某个特定方向。海龟完成旋转后，应该会显示一条转达目标结果的消息：

```
[INFO] [turtlesim]: Rotation goal completed successfully
```

[16] `F` 键会在目标执行中途取消它。

[17] 试着按 `C` 键，然后在海龟完成旋转之前按 `F` 键。在运行 `/turtlesim` 节点的终端里，你会看到：

```
[INFO] [turtlesim]: Rotation goal canceled
```

[18] 不仅客户端一侧（你在 teleop 里的输入）可以停止目标，服务器一侧（`/turtlesim` 节点）也可以。当服务器一侧选择停止处理某个目标时，我们说它“中止”（abort）了该目标。

[19] 试着按 `D` 键，然后在第一次旋转完成之前按 `G` 键。在运行 `/turtlesim` 节点的终端里，你会看到：

```
[WARN] [turtlesim]: Rotation goal received before a previous goal finished. Aborting previous goal
```

[20] 这个动作服务器选择中止第一个目标，因为它收到了一个新目标。它也可以选择别的做法，比如拒绝新目标，或者在第一个目标完成后再执行第二个目标。

[21] 不要假设每个动作服务器在收到新目标时都会中止当前目标。

*3 ros2 node info*

[22] 要查看一个节点提供了哪些动作（这里是 `/turtlesim`），打开新终端运行：

```
$ ros2 node info /turtlesim
/turtlesim
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim/msg/Color
    /turtle1/pose: turtlesim/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim/srv/Kill
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim/srv/Spawn
    /turtle1/set_pen: turtlesim/srv/SetPen
    /turtle1/teleport_absolute: turtlesim/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim/srv/TeleportRelative
    /turtlesim/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /turtlesim/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /turtlesim/get_parameters: rcl_interfaces/srv/GetParameters
    /turtlesim/list_parameters: rcl_interfaces/srv/ListParameters
    /turtlesim/set_parameters: rcl_interfaces/srv/SetParameters
    /turtlesim/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
  Action Clients:
```

[23] 该命令返回 `/turtlesim` 的订阅者、发布者、服务、动作服务器和动作客户端列表。

[24] 注意 `/turtlesim` 的 `/turtle1/rotate_absolute` 动作列在 **Action Servers** 下。这意味着 `/turtlesim` 响应该动作并为其提供反馈。

[25] `/teleop_turtle` 节点的 `/turtle1/rotate_absolute` 列在 **Action Clients** 下，意味着它为该动作名发送目标。要看到这一点，运行：

```
$ ros2 node info /teleop_turtle
/teleop_turtle
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Service Servers:
    /teleop_turtle/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /teleop_turtle/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /teleop_turtle/get_parameters: rcl_interfaces/srv/GetParameters
    /teleop_turtle/list_parameters: rcl_interfaces/srv/ListParameters
    /teleop_turtle/set_parameters: rcl_interfaces/srv/SetParameters
    /teleop_turtle/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:

  Action Clients:
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
```

*4 ros2 action list*

[26] 要识别 ROS 图中的所有动作，运行：

```
$ ros2 action list
/turtle1/rotate_absolute
```

[27] 这是目前 ROS 图中唯一的动作。它控制海龟的旋转，如你前面所见。你也已经从 `ros2 node info <node_name>` 命令知道，这个动作有一个动作客户端（属于 `/teleop_turtle`）和一个动作服务器（属于 `/turtlesim`）。

*4.1 ros2 action list -t*

[28] 动作有类型，和话题、服务类似。要查 `/turtle1/rotate_absolute` 的类型，运行：

```
$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]
```

[29] 每个动作名右边的方括号里（这里只有 `/turtle1/rotate_absolute`）是动作类型 `turtlesim/action/RotateAbsolute`。当你从命令行或代码里执行动作时，会需要它。

*5 ros2 action type*

[30] 如果你想检查某个动作的动作类型，运行：

```
$ ros2 action type /turtle1/rotate_absolute
turtlesim/action/RotateAbsolute
```

*6 ros2 action info*

[31] 你可以用下面的命令进一步内省 `/turtle1/rotate_absolute` 动作：

```
$ ros2 action info /turtle1/rotate_absolute
Action: /turtle1/rotate_absolute
Action clients: 1
    /teleop_turtle
Action servers: 1
    /turtlesim
```

[32] 这印证了我们前面对每个节点运行 `ros2 node info` 得到的结论：`/teleop_turtle` 节点有该动作的动作客户端，`/turtlesim` 节点有该动作的动作服务器。

*7 ros2 interface show*

[33] 在你自己发送或执行动作目标之前，还需要一份信息：动作类型的结构。

[34] 回想一下，你在运行 `ros2 action list -t` 时已经确认了 `/turtle1/rotate_absolute` 的类型。在终端里输入下面这条带动作类型的命令：

```
$ ros2 interface show turtlesim/action/RotateAbsolute
```

[35] 它会返回：

```
# The desired heading in radians
float32 theta
---
# The angular displacement in radians to the starting position
float32 delta
---
# The remaining rotation in radians
float32 remaining
```

[36] 这条消息中第一条 `---` 之上的部分，是目标请求的结构（数据类型和名字）。下一部分是结果的结构。最后一部分是反馈的结构。

*8 ros2 action send_goal*

[37] 现在我们从命令行发送一个动作目标，语法如下：

```
$ ros2 action send_goal <action_name> <action_type> <values>
```

[38] `<values>` 需要是 YAML 格式。

[39] 盯着 turtlesim 窗口，在终端里输入：

```
$ ros2 action send_goal /turtle1/rotate_absolute turtlesim/action/RotateAbsolute "{theta: 1.57}"
Waiting for an action server to become available...
Sending goal:
   theta: 1.57

Goal accepted with ID: f8db8f44410849eaa93d3feb747dd444

Result:
  delta: -1.568000316619873

Goal finished with status: SUCCEEDED
```

[40] 你应该能看到海龟在旋转。

[41] 所有目标都有一个唯一 ID，显示在返回消息里。你还能看到结果，一个名为 `delta` 的字段，它是相对起始位置的角位移。

[42] 要看到这个目标的反馈，在 `ros2 action send_goal` 命令后加上 `--feedback`：

```
$ ros2 action send_goal /turtle1/rotate_absolute turtlesim/action/RotateAbsolute "{theta: -1.57}" --feedback
Sending goal:
   theta: -1.57

Goal accepted with ID: e6092c831f994afda92f0086f220da27

Feedback:
  remaining: -3.1268222332000732

Feedback:
  remaining: -3.1108222007751465

…

Result:
  delta: 3.1200008392333984

Goal finished with status: SUCCEEDED
```

[43] 你会持续收到反馈，即剩余的弧度数，直到目标完成。

**小结**

[44] 动作像服务，但允许你执行长时间运行的任务，提供规律反馈，并且可以被取消。

[45] 机器人系统很可能会用动作来做导航。一个动作目标可以告诉机器人前往某个位置。机器人向该位置导航的过程中，可以沿途发送更新（即反馈），到达目的地后再发一条最终结果消息。

[46] Turtlesim 有一个动作服务器，动作客户端可以向它发送目标来旋转海龟。本教程中，你内省了那个动作 `/turtle1/rotate_absolute`，从而更好地理解动作是什么、如何工作。

**下一步**

[47] 现在你已经覆盖了 ROS 2 的所有核心概念。这一组教程的最后几节会介绍一些让 ROS 2 更易用的工具和技巧，从 Using Rqt Console 开始。

**相关内容**

[48] 你可以在这里阅读更多关于 ROS 2 动作设计决策的内容。

### 读法补充

**动作的三段结构就是它和服务的全部差别**：服务只有 request / response 两段，调用完就结束；动作有 goal / feedback / result 三段，中间可以持续反馈，可以取消，服务端还可以中止。别把 feedback 当成“结果的多次副本”——feedback 是**过程中**的进度，result 是**结束时**的最终结论，两者字段可以完全不同（`RotateAbsolute` 里 feedback 是 `remaining`，result 是 `delta`）。

**术语**

| 英文 | 意思 | 注意 |
|---|---|---|
| goal | 目标：客户端要求服务端做的事 | 有唯一 ID |
| feedback | 反馈：执行过程中的周期更新 | 不是最终结果 |
| result | 结果：目标结束时返回的最终数据 | 与 feedback 字段不同 |
| cancel | 取消：客户端主动停止 | 由客户端发起 |
| abort | 中止：服务端主动停止 | 由服务端发起，客户端收到的是“被中止” |
| SUCCEEDED | 目标成功结束 | 只是“这个目标结束了”，不代表物理上到了你要的位置 |

**长句拆解**

- [18] `Not only can the client-side (...) stop a goal, but the server-side (...) can as well.` `Not only ... but ... as well` 是“不仅……而且……”；`can` 提前是因为 `Not only` 置于句首引起部分倒装。
- [20] `It could have chosen something else, like reject the new goal or execute the second goal after the first one finished.` `could have chosen` 是虚拟语气，“本来可以选择”；`like` 后面跟两个动词原形，举例说明“别的做法”。

**读的时候注意**

- `Goal accepted with ID: ...` 只说明**目标被接受**，不说明执行成功；真正的结论要看 `Result:` 和 `Goal finished with status:`。第 4 题问“打印 goal accepted 能否当作轨迹已经到达的证据”，答案就是不能——它只是“收到并接受”，既没有反馈，也没有结果。
- `canceled`（客户端取消）和 `aborting`（服务端中止）是两种不同的结局。前者是你按了 F，后者是服务端收到新目标后自己决定不干了。读日志时要分清是谁停的。
- `ros2 action info` 的输出同时给出 clients 和 servers 数量，这比 `node info` 更直接地回答“这个动作有几个人在发目标、几个人在服务”。
- 动作内部确实是用话题和服务实现的，但**不要**因此就用 `topic echo` 去读动作的 goal/feedback——它们有自己的一套隐藏话题名和封装。要看就用 `ros2 action` 或 `ros2 interface show`。

---

<a id="pubsub"></a>

## 5. Writing a simple publisher and subscriber (Python)（写一个简单的发布者与订阅者）

原文：[Writing-A-Simple-Py-Publisher-And-Subscriber.rst](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.rst)

**Goal:** Create and run a publisher and subscriber node using Python.

**Tutorial level:** Beginner

**Time:** 20 minutes

### 原文

**Background**

[1] In this tutorial, you will create nodes that pass information in the form of string messages to each other over a topic. The example used here is a simple "talker" and "listener" system; one node publishes data and the other subscribes to the topic so it can receive that data.

[2] The code used in these examples can be found here.

**Prerequisites**

[3] In previous tutorials, you learned how to create a workspace and create a package.

[4] A basic understanding of Python is recommended, but not entirely necessary.

**Tasks**

*1 Create a package*

[5] Open a new terminal and source your ROS 2 installation so that `ros2` commands will work.

[6] Navigate into the `ros2_ws` directory created in a previous tutorial.

[7] Recall that packages should be created in the `src` directory, not the root of the workspace. So, navigate into `ros2_ws/src`, and run the package creation command:

```
$ ros2 pkg create --build-type ament_python --license Apache-2.0 py_pubsub
```

[8] Your terminal will return a message verifying the creation of your package `py_pubsub` and all its necessary files and folders.

*2 Write the publisher node*

[9] Navigate into `ros2_ws/src/py_pubsub/py_pubsub`. Recall that this directory is a Python package with the same name as the ROS 2 package it's nested in.

[10] Download the example talker code by entering the following command:

```
$ wget https://raw.githubusercontent.com/ros2/examples/jazzy/rclpy/topics/minimal_publisher/examples_rclpy_minimal_publisher/publisher_member_function.py
```

[11] Now there will be a new file named `publisher_member_function.py` adjacent to `__init__.py`.

[12] Open the file using your preferred text editor.

```python
import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

*2.1 Examine the code*

[13] The first lines of code after the comments import rclpy so its Node class can be used.

```python
import rclpy
from rclpy.node import Node
```

[14] The next statement imports the built-in std_msgs/msg/String message type that the node uses to structure the data that it passes on the topic.

```python
from std_msgs.msg import String
```

[15] These lines represent the node's dependencies. Recall that dependencies have to be added to `package.xml`, which you'll do in the next section.

[16] Next, the `MinimalPublisher` class is created, which inherits from (or is a subclass of) Node.

```python
class MinimalPublisher(Node):
```

[17] Following is the definition of the class's constructor. `super().__init__` calls the Node class's constructor and gives it your node name, in this case `minimal_publisher`.

[18] `create_publisher` declares that the node publishes messages of type std_msgs/msg/String (imported from the `std_msgs.msg` module), over a topic named `topic`, and that the "queue size" is 10. Queue size is a required Quality of Service (QoS) setting that limits the amount of queued messages if a subscriber is not receiving them fast enough.

[19] Next, `create_timer` is used to create a callback that executes every 0.5 seconds. `self.i` is a counter used in the callback.

```python
def __init__(self):
    super().__init__('minimal_publisher')
    self.publisher_ = self.create_publisher(String, 'topic', 10)
    timer_period = 0.5  # seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.i = 0
```

[20] `timer_callback` creates a message with the counter value appended, publishes it, and prints it to the console with `get_logger()`'s `info()` function.

```python
def timer_callback(self):
    msg = String()
    msg.data = 'Hello World: %d' % self.i
    self.publisher_.publish(msg)
    self.get_logger().info('Publishing: "%s"' % msg.data)
    self.i += 1
```

[21] Lastly, the main function is defined.

```python
def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()
```

[22] First the rclpy library is initialized, then the node is created, and then it "spins" the node (using `spin()`) so its callbacks are called.

### 译文

**背景**

[1] 本教程中，你会创建一些节点，它们以字符串消息的形式，通过一个话题互相传递信息。这里用的例子是一个简单的“说话者”（talker）和“收听者”（listener）系统：一个节点发布数据，另一个节点订阅该话题，从而接收数据。

[2] 这些示例用到的代码可以在这里找到。

**前置条件**

[3] 前面的教程里，你学会了如何创建工作空间和创建包。

[4] 建议对 Python 有基本了解，但不是完全必需。

**任务**

*1 创建包*

[5] 打开新终端，source 你的 ROS 2 安装，这样 `ros2` 命令才能用。

[6] 进入前面教程创建的 `ros2_ws` 目录。

[7] 回想一下，包应该创建在 `src` 目录里，而不是工作空间的根目录。所以进入 `ros2_ws/src`，运行创建包的命令：

```
$ ros2 pkg create --build-type ament_python --license Apache-2.0 py_pubsub
```

[8] 终端会返回一条消息，确认包 `py_pubsub` 及其所有必要文件和文件夹已创建。

*2 写发布者节点*

[9] 进入 `ros2_ws/src/py_pubsub/py_pubsub`。回想一下，这个目录是一个 Python 包，名字和它嵌套在其中的 ROS 2 包相同。

[10] 输入下面的命令，下载示例 talker 代码：

```
$ wget https://raw.githubusercontent.com/ros2/examples/jazzy/rclpy/topics/minimal_publisher/examples_rclpy_minimal_publisher/publisher_member_function.py
```

[11] 现在，`__init__.py` 旁边会多出一个名为 `publisher_member_function.py` 的新文件。

[12] 用你喜欢的文本编辑器打开它。

```python
import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

*2.1 逐段看代码*

[13] 注释之后的第一行代码导入 rclpy，以便使用它的 `Node` 类。

```python
import rclpy
from rclpy.node import Node
```

[14] 接下来这条语句导入内置的 `std_msgs/msg/String` 消息类型，节点用它来组织在话题上传递的数据。

```python
from std_msgs.msg import String
```

[15] 这几行代表节点的依赖。回想一下，依赖必须加到 `package.xml` 里，下一节你就来做这件事。

[16] 接着创建 `MinimalPublisher` 类，它继承（或者说派生）自 `Node`。

```python
class MinimalPublisher(Node):
```

[17] 下面是该类构造函数的定义。`super().__init__` 调用 `Node` 类的构造函数，并把你的节点名传给它，这里是 `minimal_publisher`。

[18] `create_publisher` 声明该节点发布 `std_msgs/msg/String` 类型的消息（从 `std_msgs.msg` 模块导入），话题名为 `topic`，并且“队列长度”为 10。队列长度是一个必需的服务质量（QoS）设置，用于在订阅者接收不够快时限制排队消息的数量。

[19] 接下来，用 `create_timer` 创建一个每 0.5 秒执行一次的回调。`self.i` 是回调里用到的计数器。

```python
def __init__(self):
    super().__init__('minimal_publisher')
    self.publisher_ = self.create_publisher(String, 'topic', 10)
    timer_period = 0.5  # seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.i = 0
```

[20] `timer_callback` 创建一条消息，把计数器的值附加进去，发布它，并用 `get_logger()` 的 `info()` 函数打印到控制台。

```python
def timer_callback(self):
    msg = String()
    msg.data = 'Hello World: %d' % self.i
    self.publisher_.publish(msg)
    self.get_logger().info('Publishing: "%s"' % msg.data)
    self.i += 1
```

[21] 最后定义 main 函数。

```python
def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()
```

[22] 首先初始化 rclpy 库，然后创建节点，再让节点“自旋”（用 `spin()`），这样它的回调就会被调用。

### 原文（续：2.2 依赖 — 小结）

*2.2 Add dependencies*

[23] Navigate one level back to the `ros2_ws/src/py_pubsub` directory, where the `setup.py`, `setup.cfg`, and `package.xml` files have been created for you.

[24] Open `package.xml` with your text editor.

[25] As mentioned in the previous tutorial, make sure to fill in the `<description>`, `<maintainer>` and `<license>` tags:

```xml
<description>Examples of minimal publisher/subscriber using rclpy</description>
<maintainer email="you@email.com">Your Name</maintainer>
<license>Apache-2.0</license>
```

[26] After the lines above, add the following dependencies corresponding to your node's import statements:

```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
```

[27] This declares the package needs rclpy and std_msgs when its code is executed.

[28] Make sure to save the file.

*2.3 Add an entry point*

[29] Open the `setup.py` file.

[30] Again, match the `maintainer`, `maintainer_email`, `description` and `license` fields to your `package.xml`:

```python
maintainer='YourName',
maintainer_email='you@email.com',
description='Examples of minimal publisher/subscriber using rclpy',
license='Apache-2.0',
```

[31] Add the following line within the `console_scripts` brackets of the `entry_points` field:

```python
entry_points={
        'console_scripts': [
                'talker = py_pubsub.publisher_member_function:main',
        ],
},
```

[32] Don't forget to save.

*2.4 Check setup.cfg*

[33] The contents of the `setup.cfg` file should be correctly populated automatically, like so:

```ini
[develop]
script_dir=$base/lib/py_pubsub
[install]
install_scripts=$base/lib/py_pubsub
```

[34] This is simply telling setuptools to put your executables in `lib`, because `ros2 run` will look for them there.

[35] You could build your package now, source the local setup files, and run it, but let's create the subscriber node first so you can see the full system at work.

*3 Write the subscriber node*

[36] Return to `ros2_ws/src/py_pubsub/py_pubsub` to create the next node. Enter the following code in your terminal:

```
$ wget https://raw.githubusercontent.com/ros2/examples/jazzy/rclpy/topics/minimal_subscriber/examples_rclpy_minimal_subscriber/subscriber_member_function.py
```

[37] Now the directory should have these files:

```
__init__.py  publisher_member_function.py  subscriber_member_function.py
```

*3.1 Examine the code*

[38] Open the `subscriber_member_function.py` with your text editor.

```python
import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

[39] The subscriber node's code is nearly identical to the publisher's.

[40] The constructor creates a subscriber with the same arguments as the publisher using `create_subscription`.

```python
self.subscription = self.create_subscription(
    String,
    'topic',
    self.listener_callback,
    10)
```

[41] Recall from the topics tutorial that the topic name and message type used by the publisher and subscriber must match to allow them to communicate.

[42] The subscriber's constructor and callback don't include any timer definition, because it doesn't need one. Its callback gets called as soon as it receives a message.

[43] The callback definition simply prints an info message to the console, along with the data it received. Recall that the publisher defines `msg.data = 'Hello World: %d' % self.i`

```python
def listener_callback(self, msg):
    self.get_logger().info('I heard: "%s"' % msg.data)
```

[44] The `main` definition is almost exactly the same, replacing the creation and spinning of the publisher with the subscriber.

```python
minimal_subscriber = MinimalSubscriber()

rclpy.spin(minimal_subscriber)
```

[45] Since this node has the same dependencies as the publisher, there's nothing new to add to `package.xml`. The `setup.cfg` file can also remain untouched.

*3.2 Add an entry point*

[46] Reopen `setup.py` and add the entry point for the subscriber node below the publisher's entry point. The `entry_points` field should now look like this:

```python
entry_points={
        'console_scripts': [
                'talker = py_pubsub.publisher_member_function:main',
                'listener = py_pubsub.subscriber_member_function:main',
        ],
},
```

[47] Make sure to save the file, and then your pub/sub system should be ready.

*4 Build and run*

[48] You likely already have the rclpy and std_msgs packages installed as part of your ROS 2 system.

[49] It's good practice to run rosdep in the root of your workspace (`ros2_ws`) to check for missing dependencies before building:

```
$ rosdep install -i --from-path src --rosdistro jazzy -y
```

[50] Still in the root of your workspace, `ros2_ws`, build your new package:

```
$ colcon build --packages-select py_pubsub
```

[51] Open a new terminal, navigate to `ros2_ws`, and source the setup files:

```
$ source install/setup.bash
```

[52] Now run the talker node. The terminal should start publishing info messages every 0.5 seconds, like so:

```
$ ros2 run py_pubsub talker
[INFO] [minimal_publisher]: Publishing: "Hello World: 0"
[INFO] [minimal_publisher]: Publishing: "Hello World: 1"
[INFO] [minimal_publisher]: Publishing: "Hello World: 2"
[INFO] [minimal_publisher]: Publishing: "Hello World: 3"
[INFO] [minimal_publisher]: Publishing: "Hello World: 4"
...
```

[53] Open another terminal, source the setup files from inside `ros2_ws` again, and then start the listener node. The listener will start printing messages to the console, starting at whatever message count the publisher is on at that time, like so:

```
$ ros2 run py_pubsub listener
[INFO] [minimal_subscriber]: I heard: "Hello World: 10"
[INFO] [minimal_subscriber]: I heard: "Hello World: 11"
[INFO] [minimal_subscriber]: I heard: "Hello World: 12"
[INFO] [minimal_subscriber]: I heard: "Hello World: 13"
[INFO] [minimal_subscriber]: I heard: "Hello World: 14"
```

[54] Enter `Ctrl+C` in each terminal to stop the nodes from spinning.

**Summary**

[55] You created two nodes to publish and subscribe to data over a topic. Before running them, you added their dependencies and entry points to the package configuration files.

**Next steps**

[56] Next you'll create another simple ROS 2 package using the service/client model. Again, you can choose to write it in either C++ or Python.

**Related content**

[57] There are several ways you could write a publisher and subscriber in Python; check out the `minimal_publisher` and `minimal_subscriber` packages in the ros2/examples repo.

### 译文（续：2.2 依赖 — 小结）

*2.2 添加依赖*

[23] 回到上一级 `ros2_ws/src/py_pubsub` 目录，`setup.py`、`setup.cfg` 和 `package.xml` 已经为你创建好了。

[24] 用文本编辑器打开 `package.xml`。

[25] 如上一节教程所述，确保填写 `<description>`、`<maintainer>` 和 `<license>` 标签：

```xml
<description>Examples of minimal publisher/subscriber using rclpy</description>
<maintainer email="you@email.com">Your Name</maintainer>
<license>Apache-2.0</license>
```

[26] 在上面几行之后，添加与节点 import 语句对应的依赖：

```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
```

[27] 这声明了包在代码执行时需要 rclpy 和 std_msgs。

[28] 确保保存文件。

*2.3 添加入口点*

[29] 打开 `setup.py`。

[30] 同样，让 `maintainer`、`maintainer_email`、`description` 和 `license` 字段与 `package.xml` 保持一致：

```python
maintainer='YourName',
maintainer_email='you@email.com',
description='Examples of minimal publisher/subscriber using rclpy',
license='Apache-2.0',
```

[31] 在 `entry_points` 字段的 `console_scripts` 方括号内添加下面一行：

```python
entry_points={
        'console_scripts': [
                'talker = py_pubsub.publisher_member_function:main',
        ],
},
```

[32] 别忘了保存。

*2.4 检查 setup.cfg*

[33] `setup.cfg` 的内容应该已自动正确填充，如下：

```ini
[develop]
script_dir=$base/lib/py_pubsub
[install]
install_scripts=$base/lib/py_pubsub
```

[34] 这只是告诉 setuptools 把你的可执行文件放到 `lib` 里，因为 `ros2 run` 会在那里找它们。

[35] 你现在就可以构建包、source 本地 setup 文件并运行它，但我们先创建订阅者节点，这样你能看到完整的系统如何工作。

*3 写订阅者节点*

[36] 回到 `ros2_ws/src/py_pubsub/py_pubsub` 创建下一个节点。在终端输入下面的代码：

```
$ wget https://raw.githubusercontent.com/ros2/examples/jazzy/rclpy/topics/minimal_subscriber/examples_rclpy_minimal_subscriber/subscriber_member_function.py
```

[37] 现在目录里应该有这些文件：

```
__init__.py  publisher_member_function.py  subscriber_member_function.py
```

*3.1 逐段看代码*

[38] 用文本编辑器打开 `subscriber_member_function.py`。

```python
import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

[39] 订阅者节点的代码和发布者几乎一样。

[40] 构造函数用 `create_subscription`、以和发布者相同的参数创建订阅者。

```python
self.subscription = self.create_subscription(
    String,
    'topic',
    self.listener_callback,
    10)
```

[41] 回想话题教程：发布者和订阅者使用的话题名与消息类型必须匹配，它们才能通信。

[42] 订阅者的构造函数和回调没有定义定时器，因为它不需要。它一收到消息，回调就会被调用。

[43] 回调定义只是向控制台打印一条 info 消息，以及它收到的数据。回想发布者定义了 `msg.data = 'Hello World: %d' % self.i`。

```python
def listener_callback(self, msg):
    self.get_logger().info('I heard: "%s"' % msg.data)
```

[44] `main` 的定义几乎完全相同，只是把发布者的创建和自旋换成了订阅者。

```python
minimal_subscriber = MinimalSubscriber()

rclpy.spin(minimal_subscriber)
```

[45] 由于这个节点与发布者依赖相同，`package.xml` 里没有新东西要加。`setup.cfg` 也可以保持不变。

*3.2 添加入口点*

[46] 重新打开 `setup.py`，在发布者入口点下面添加订阅者节点的入口点。`entry_points` 字段现在应该是这样：

```python
entry_points={
        'console_scripts': [
                'talker = py_pubsub.publisher_member_function:main',
                'listener = py_pubsub.subscriber_member_function:main',
        ],
},
```

[47] 确保保存，然后你的发布/订阅系统就准备好了。

*4 构建并运行*

[48] 你可能已经作为 ROS 2 系统的一部分安装了 rclpy 和 std_msgs 包。

[49] 一个好习惯是：在构建之前，在工作空间根目录 `ros2_ws` 运行 rosdep，检查缺失的依赖：

```
$ rosdep install -i --from-path src --rosdistro jazzy -y
```

[50] 仍然在工作空间根目录 `ros2_ws`，构建你的新包：

```
$ colcon build --packages-select py_pubsub
```

[51] 打开新终端，进入 `ros2_ws`，source setup 文件：

```
$ source install/setup.bash
```

[52] 现在运行 talker 节点。终端应该开始每 0.5 秒发布一条 info 消息：

```
$ ros2 run py_pubsub talker
[INFO] [minimal_publisher]: Publishing: "Hello World: 0"
[INFO] [minimal_publisher]: Publishing: "Hello World: 1"
[INFO] [minimal_publisher]: Publishing: "Hello World: 2"
[INFO] [minimal_publisher]: Publishing: "Hello World: 3"
[INFO] [minimal_publisher]: Publishing: "Hello World: 4"
...
```

[53] 打开另一个终端，再次在 `ros2_ws` 里 source setup 文件，然后启动 listener 节点。listener 会开始向控制台打印消息，从发布者当时所在的计数开始：

```
$ ros2 run py_pubsub listener
[INFO] [minimal_subscriber]: I heard: "Hello World: 10"
[INFO] [minimal_subscriber]: I heard: "Hello World: 11"
[INFO] [minimal_subscriber]: I heard: "Hello World: 12"
[INFO] [minimal_subscriber]: I heard: "Hello World: 13"
[INFO] [minimal_subscriber]: I heard: "Hello World: 14"
```

[54] 在每个终端按 `Ctrl+C` 停止节点自旋。

**小结**

[55] 你创建了两个节点，通过一个话题发布和订阅数据。运行它们之前，你把依赖和入口点加到了包的配置文件里。

**下一步**

[56] 接下来你会用服务/客户端模型创建另一个简单的 ROS 2 包。同样，你可以选择用 C++ 或 Python 写。

**相关内容**

[57] 用 Python 写发布者和订阅者有好几种方式；看看 ros2/examples 仓库里的 `minimal_publisher` 和 `minimal_subscriber` 包。

### 读法补充

**代码的主线只有一条**：`main` 里 `rclpy.init` → 构造节点（构造函数里注册发布者/订阅者/定时器）→ `rclpy.spin(node)` 把控制权交给执行器 → 回调被调用。**没有 `spin`，你注册的回调一个都不会跑**；`spin` 不是“启动后台线程”，它本身就是当前线程里的事件循环，按 `Ctrl+C` 才退出。

**术语**

| 英文 | 意思 | 备注 |
|---|---|---|
| talker / listener | 说话者 / 收听者 | 官方示例的叫法，就是 publisher / subscriber |
| queue size | 队列长度，`create_publisher(..., 10)` 的 10 | QoS 的一项；不是“缓冲区字节数” |
| timer period | 定时器周期，`0.5` 秒 | 是“期望”周期，实际受调度影响 |
| entry point | 入口点：`talker = py_pubsub.publisher_member_function:main` | 把可执行名映射到模块里的函数 |
| exec_depend | 执行期依赖 | `package.xml` 里声明运行时需要哪些包 |
| spin | 自旋：让执行器持续处理就绪的回调 | 不是“旋转” |

**长句拆解**

- [18] `create_publisher declares that the node publishes messages of type ... over a topic named ..., and that the "queue size" is 10.` 主干是 `declares that A and that B`，两个 `that` 从句并列；中间 `over a topic named 'topic'` 是方式状语。
- [42] `The subscriber's constructor and callback don't include any timer definition, because it doesn't need one. Its callback gets called as soon as it receives a message.` 第二句的 `as soon as` 是“一……就……”，不是“尽快”。

**读的时候注意**

- 两个节点用的是**相对话题名** `'topic'`。相对名会解析到当前命名空间下（默认是 `/`），所以两边都解析成 `/topic`，才能对上。如果你给其中一个加了命名空间，另一个没加，名字就对不上了——这就是“同名话题为什么收不到”的第一类原因。
- listener 从 `Hello World: 10` 开始，不是从 0 开始。因为话题默认是 `VOLATILE` 持久性：它只接收**订阅之后**发布的消息，不会补发历史。这一点直接关系到第 3 题“四行可能在发现完成前就发完”的问题。
- `self.subscription` 那行 `# prevent unused variable warning` 是给 linter 看的，但保留引用本身也有意义：你之后可能要用它（例如 `destroy_subscription()`），而且对象被回收后回调也就不在了。
- `destroy_node()` 之后的 `rclpy.shutdown()` 负责关掉上下文。真实项目里通常放在 `try/finally` 里，避免异常时跳过清理；官方最小示例为了短，省略了异常处理。
- `colcon build` 之后必须 `source install/setup.bash`，否则 `ros2 run py_pubsub talker` 会报“包找不到”。这不是代码问题，是环境没叠加上。

<a id="jointstate"></a>

## 6. `sensor_msgs/msg/JointState` 定义

原文：[`sensor_msgs/msg/JointState.msg`](https://github.com/ros2/common_interfaces/blob/jazzy/sensor_msgs/msg/JointState.msg)（jazzy 分支）。这段注释不在教程正文里，但它是第 2、3 题的直接依据，而且 `ros2 interface show sensor_msgs/msg/JointState` 打印出来的就是它（你环境检查时已经看到过）。

**原文**

```text
# This is a message that holds data to describe the state of a set of torque controlled joints.
#
# The state of each joint (revolute or prismatic) is defined by:
#  * the position of the joint (rad or m),
#  * the velocity of the joint (rad/s or m/s) and
#  * the effort that is applied in the joint (Nm or N).
#
# Each joint is uniquely identified by its name
# The header specifies the time at which the joint states were recorded. All the joint states
# in one message have to be recorded at the same time.
#
# This message consists of a multiple arrays, one for each part of the joint state.
# The goal is to make each of the fields optional. When e.g. your joints have no
# effort associated with them, you can leave the effort array empty.
#
# All arrays in this message should have the same size, or be empty.
# This is the only way to uniquely associate the joint name with the correct
# states.

std_msgs/Header header

string[] name
float64[] position
float64[] velocity
float64[] effort
```

**译文（逐行对应）**

```text
# 这条消息承载的数据，用来描述一组力矩控制关节的状态。
#
# 每个关节（旋转关节或移动关节）的状态由以下三项定义：
#  * 关节的位置（弧度或米），
#  * 关节的速度（弧度/秒 或 米/秒），以及
#  * 施加在该关节上的力/力矩（牛·米 或 牛）。
#
# 每个关节由它的名字唯一标识。
# header 指明这些关节状态是在什么时刻记录的。一条消息里的所有关节状态
# 必须在同一时刻记录。
#
# 这条消息由多个数组组成，关节状态的每一部分各用一个数组。
# 这样做的目的是让每个字段都是可选的。例如，当你的关节没有对应的
# effort 时，可以把 effort 数组留空。
#
# 这条消息里的所有数组长度应当相同，或者为空。
# 这是把关节名字与正确状态唯一对应起来的唯一办法。

std_msgs/Header header

string[] name
float64[] position
float64[] velocity
float64[] effort
```

**字段表**

| 字段 | 类型 | 含义 | 单位 | 可为空 |
|---|---|---|---|---|
| `header` | `std_msgs/Header` | `stamp` 是采样时刻，`frame_id` 可写参考坐标系 | 秒（`stamp`） | 否（但字段内容可以为空） |
| `name` | `string[]` | 关节名，唯一标识该关节 | 无 | 是 |
| `position` | `float64[]` | 关节位置 | 旋转关节 rad，移动关节 m | 是 |
| `velocity` | `float64[]` | 关节速度 | rad/s 或 m/s | 是 |
| `effort` | `float64[]` | 关节上施加的力/力矩 | 旋转关节 N·m，移动关节 N | 是 |

`std_msgs/Header` 本身只有两个字段：`builtin_interfaces/Time stamp` 和 `string frame_id`。在 `JointState` 里 `frame_id` 通常留空，因为关节状态未必属于某一个坐标系；重要的是 `stamp`。

### 读法补充

**“多个数组 + 一个名字数组”的设计，含义是“同一行对应同一关节”。** 第 i 个关节的名字是 `name[i]`，它的位置是 `position[i]`、速度是 `velocity[i]`、力矩是 `effort[i]`。所以：

- 数组**不是按名字排序的**，也没有“缺哪个关节就填 NaN”的约定。想按名字取值，必须自己建 `{name: index}` 的映射。第 2 题 `positions_in_order` 做的就是这件事。
- “所有数组长度相同，或者为空”是**同一条消息内部**的约束。它不保证两条不同的消息之间长度一致：这一帧可能有 7 个关节，下一帧可能只有 5 个（机器人换模式、某个驱动掉线）。所以第 3 题记录时不能假设帧与帧的 `name` 顺序相同。
- “要么长度相同，要么为空”这句话反过来读：**空数组是合法的**。如果发布者没有速度信息，`velocity` 就是 `[]`，而不是补一串 0。补 0 是把“不知道”说成“速度为零”，在控制里是错误信息，不是缺省值。你的校验函数应该区分“数组为空（允许）”和“数组非空但长度不对（报错）”。
- 单位写成“rad or m”是因为同一个消息类型同时服务旋转关节和移动关节；**看名字猜不出单位**，要靠机器人模型（URDF）或驱动文档。第 4 题里“十秒轨迹”这类判断之所以要看任务而不是看消息类型，也是同一个道理。
- 真实系统里 `name` 常见三种写法：`joint1`、带命名空间的 `arm/joint1`、带前导斜杠 `/joint1`。它们**不是同一个字符串**，映射表按字符串精确匹配，所以第 2 题要防“名字相似但不相等”。参考答案里把“缺关节”和“重复名”都当错误处理，就是在守这条边界。

<a id="cheatsheet"></a>

## 7. 命令速查：按“我想知道什么”排

命令后面括号里是它回答的问题。完整原文在上面的教程里，这里只做索引，不替代原文。

**节点**

| 命令 | 回答的问题 |
|---|---|
| `ros2 run <包> <可执行文件>` | 怎么启动一个可执行文件 |
| `ros2 node list` | 图里现在有哪些节点（名字是完整名，带命名空间） |
| `ros2 node list --no-daemon` | 同上，但不走守护进程缓存，刚启动/刚退出时更可信 |
| `ros2 node info <节点名>` | 这个节点订阅/发布/提供/调用什么（六类连接 + 服务） |
| `ros2 run pkg exe --ros-args -r __node:=新名` | 启动时改节点名 |
| `--ros-args -r 旧话题:=新话题` | 启动时改话题名 |

**话题**

| 命令 | 回答的问题 |
|---|---|
| `ros2 topic list` | 有哪些话题 |
| `ros2 topic list -t` | 有哪些话题，各自什么类型 |
| `ros2 topic echo <话题>` | 内容长什么样（没有发布者时它会一直等） |
| `ros2 topic info <话题>` | 类型 + 发布者数量 + 订阅者数量 |
| `ros2 topic info <话题> --verbose` | 上面这些 + 每个端点所在节点/命名空间 + QoS |
| `ros2 topic hz <话题>` | 消息到达频率 |
| `ros2 topic bw <话题>` | 带宽与消息数 |
| `ros2 topic find <类型>` | 哪些话题用这个类型 |
| `ros2 topic pub <话题> <类型> '<YAML>'` | 手动发一条（默认 1 Hz 持续发） |
| `... --once` | 只发一条 |
| `... --rate 5` | 改发布频率 |
| `... -w 2` | 等到有 2 个订阅者再发 |
| `ros2 interface show <类型>` | 类型的字段结构 |

**服务**

| 命令 | 回答的问题 |
|---|---|
| `ros2 service list` | 有哪些服务 |
| `ros2 service list -t` | 有哪些服务，各自什么类型 |
| `ros2 service type <服务名>` | 这个服务什么类型 |
| `ros2 service info <服务名>` | 类型 + 客户端/服务端数量 |
| `ros2 service find <类型>` | 哪些服务用这个类型 |
| `ros2 service call <服务名> <类型> '<YAML>'` | 调一次；`Empty` 类型可以不写参数 |
| `ros2 interface show <服务类型>` | `---` 上面是请求，下面是响应 |

**动作**

| 命令 | 回答的问题 |
|---|---|
| `ros2 action list` | 有哪些动作 |
| `ros2 action list -t` | 有哪些动作，各自什么类型 |
| `ros2 action type <动作名>` | 这个动作什么类型 |
| `ros2 action info <动作名>` | 类型 + 动作客户端数 + 动作服务器数 |
| `ros2 interface show <动作类型>` | 三段：goal / result / feedback |
| `ros2 action send_goal <动作名> <类型> '<YAML>'` | 发一个目标并等结果 |
| `... --feedback` | 同时打印反馈 |

**构建与运行（Python 包）**

| 命令 | 回答的问题 |
|---|---|
| `ros2 pkg create --build-type ament_python <包名>` | 新建一个 Python 包 |
| `rosdep install --from-paths src --ignore-src -y --rosdistro jazzy` | 缺不缺依赖 |
| `colcon build`（在工作空间根目录） | 编译/安装包 |
| `source install/setup.bash` | 让当前终端找得到新包 |
| `ros2 pkg executables <包名>` | 这个包暴露了哪些可执行文件 |

<a id="glossary"></a>

## 8. 术语总表

| 英文 | 中文 | 在本材料里的具体所指 |
|---|---|---|
| ROS graph | ROS 图 | 所有节点与它们之间连接的集合 |
| node | 节点 | 一个承担单一职责的进程内实体 |
| executable | 可执行文件 | 被 `ros2 run` 启动的那个程序，可含多个节点 |
| package | 包 | 代码与配置的发布单位，如 `turtlesim`、`py_pubsub` |
| namespace | 命名空间 | 名字前缀，如 `/learn_ch2/joint_states` 里的 `/learn_ch2` |
| remapping | 重映射 | 启动时把默认名字换成别的名字 |
| topic | 话题 | 持续流动的数据通道，发布/订阅模型 |
| message / msg | 消息 | 话题上传输的数据结构，如 `geometry_msgs/msg/Twist` |
| publisher / subscriber | 发布者 / 订阅者 | 主动发 / 被动收 |
| queue size（depth） | 队列长度 | 订阅端积压上限，QoS 的一项 |
| QoS | 服务质量 | reliability、durability、history、depth 等策略组合 |
| service | 服务 | 一次请求、一次响应的通信 |
| request / response | 请求 / 响应 | 服务类型里 `---` 分隔的两半 |
| client / server | 客户端 / 服务端 | 发起调用的一方 / 提供服务的一方 |
| action | 动作 | 长任务：goal + feedback + result，可取消 |
| goal / feedback / result | 目标 / 反馈 / 结果 | 动作的三段数据 |
| cancel / abort | 取消 / 中止 | 客户端主动停 / 服务端因故停 |
| introspection | 内省 | 不修改程序、从外部查看结构（`node info`、`interface show`） |
| interface | 接口 | 消息、服务、动作的类型定义总称 |
| YAML | — | `topic pub`、`service call`、`action send_goal` 里参数的写法 |
| topic echo | — | 把话题上的消息打印出来 |
| timestamp / stamp | 时间戳 | `header.stamp`，采样时刻 |
| spin | 自旋 | 让执行器持续处理回调，`rclpy.spin(node)` |
| callback | 回调 | 收到消息/定时器到点时被调用的函数 |
| executor | 执行器 | 调度回调的机制，`rclpy.spin` 背后就是它 |
| ament_python | — | Python 包的构建类型 |
| colcon | — | 工作空间构建工具 |
| entry point | 入口点 | `setup.py` 里把可执行名映射到 `模块:函数` |

<a id="mapping"></a>

## 9. 和 ROS-01 四道练习的对应

这不是答案，只是“做哪题该读哪节”。答案在 `参考答案/ROS-01_参考答案.md`。

| 练习 | 先读 | 读完应该能回答 |
|---|---|---|
| 第 1 题 名字与调用顺序 | 第 1 节 [14]–[29]；第 2 节 [20]–[24]、[32]–[34] | 节点完整名由哪两部分拼成；`node info` 列出的六类连接分别是什么；为什么“包名 + 可执行名”不等于“节点名” |
| 第 2 题 `positions_in_order` | 第 6 节全部；第 2 节 [37]–[44] | `name[i]` 与 `position[i]` 怎么对应；数组为空和长度不等分别意味着什么；缺关节、重复关节该报错还是返回缺省 |
| 第 3 题 `state_recorder` | 第 5 节全部；第 2 节 [74]–[77]；第 6 节 | 订阅者要在构造函数里注册什么；`spin` 不做会怎样；一帧里 `name` 顺序变了会出什么问题；`hz` 偏低说明什么 |
| 第 4 题 选交互方式 | 第 2 节 [1]–[3]；第 3 节 [1]–[3]、[45]–[48]；第 4 节 [1]–[7]、[49]–[56] | 持续数据流/一次性查询/长任务各自匹配哪种通信；`goal accepted` 只证明什么，不证明什么 |

<a id="howto"></a>

## 10. 读完之后的自检

全部读完大约需要 2.5–3 小时（命令行四节 1.5 小时，发布/订阅 1 小时，JointState 20 分钟）。如果时间紧，先读第 1、2、5 节和第 6 节，第 3、4 节可以放到第 4 题之前再读。

合上材料，试着回答下面这些；答不上来的，回到对应编号重读那一段：

1. 一个可执行文件里能不能有两个节点？节点名和可执行文件名是什么关系？
2. `ros2 node list` 显示 `/turtlesim`，`ros2 run turtlesim turtlesim_node` 里为什么没有 `/turtlesim` 这个词？
3. `ros2 topic info /turtle1/cmd_vel --verbose` 里的 publisher count 和 subscription count 分别指什么？`topic echo` 会不会让 subscription count 变大？
4. `ros2 topic pub` 不加 `--once` 时，按 `Ctrl+C` 之前它会做什么？
5. `geometry_msgs/msg/Twist` 里 `linear` 和 `angular` 各有几个分量？海龟前进改哪个？
6. 服务和话题最本质的区别是什么？“服务是同步的、话题是异步的”这个说法哪里不准确？
7. 动作的 `feedback` 和 `result` 有什么区别？为什么不能把 result 当成 feedback 用？
8. 客户端按了取消，服务端一定会停吗？服务端在什么情况下会 abort？
9. `create_subscription` 的第三个位置参数（示例里的 10）是什么？调大调小分别有什么后果？
10. 订阅者从 `Hello World: 10` 开始打印，为什么不是从 0？
11. `JointState` 的 `velocity` 是空数组，和 `velocity` 是一串 0，语义上差在哪里？
12. 一帧 `JointState` 里 `name = ['a', 'b']`、`position = [0.1]`，这是合法消息吗？你的函数应该怎么处理？

最后一条：这些命令你不需要背。需要的是形成条件反射——**遇到“收不到数据”，先 `node info` 看连接，再 `topic info --verbose` 看名字、类型、QoS 三样是否对得上**。
