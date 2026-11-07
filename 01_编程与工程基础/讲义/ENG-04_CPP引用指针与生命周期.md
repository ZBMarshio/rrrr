# ENG-04：C++ 函数操作谁，对象能活多久

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#eng-04) · [提示与答案](../参考答案/ENG-04_参考答案.md) · [下一节](ENG-05_CPP容器类与所有权.md)

<a id="intro"></a>

## 导读

**为什么学这一节。** C++代码里，一个参数传递方式就可能决定原数据是否被修改；一个对象离开作用域，也可能让后续访问失效。理解这些关系比记住符号更有用。

**学完会有什么变化。** 从只按语法辨认星号和引用号，进到能回答函数操作谁、地址指向谁，以及返回后对象是否仍然存在。

**接下来能做什么。** 可以读懂小型C++节点的数据传递，继续学习[ENG-05](ENG-05_CPP容器类与所有权.md#intro)的资源所有权，为阅读[ROS-08](../../02_ROS2与机器人系统/讲义/ROS-08_ros2_control与执行接口.md#intro)接口实现做准备。

## 本节何时学、学到哪里

与第一阶段 W05 的 C++ ROS 节点一起使用。先能读普通函数、引用、指针、const 和对象作用域；不用先通读整门 C++ 课程。

| 资料 | 选读范围 |
|---|---|
| [LearnCpp：Lvalue references](https://www.learncpp.com/cpp-tutorial/lvalue-references/) | 引用绑定、赋值与传参；缺 const 引用时按文内相邻章节补 |
| [LearnCpp：Introduction to pointers](https://www.learncpp.com/cpp-tutorial/introduction-to-pointers/) | 地址、解引用、空指针与失效指针 |
| [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) | F.16/F.17 传参；F.43 不返回指向局部对象的指针/引用；R.1 资源与对象生命周期 |

本章示例按 C++17 编译；ROS 项目遵守它自己的编译标准与配置。

## 从函数调用走一遍

下面是完整小程序，可在自己的练习目录保存为 `references.cpp`：

```cpp
#include <iostream>

void by_value(double q) {
    q += 1.0;
}

void by_reference(double& q) {
    q += 1.0;
}

int main() {
    double position = 0.2;
    by_value(position);
    std::cout << position << '\n';
    by_reference(position);
    const double& observed = position;
    std::cout << observed << '\n';
}
```

`by_value` 收到一份 double 的值，修改形参不会改调用者的 position。`by_reference` 的 q 是调用者对象的别名。observed 通过 const 引用读取同一个对象，不能通过这个引用写它。

`const` 的约束要看写在谁身上。只读引用不意味着原对象永远不会被别的合法路径修改。

## 指针、引用和生命周期的几个边界

| 写法 | 现在怎样理解 |
|---|---|
| `double q` | 自己的数值对象 |
| `double& r = q` | q 的另一个名字，普通引用不能改绑到另一个对象 |
| `double* p = &q` | 保存 q 地址的指针；可改指向，使用前需有有效对象 |
| `const double* p` | 通过 p 不可修改目标，可让 p 指向别处 |
| `double* const p` | p 不能改指向，可通过它修改非 const 目标 |

进一步注意：

- 小型只读数值如 double，按值传递通常很直接；大容器只读输入常用 const 引用。不要见参数就全部加引用。
- 指针自身按值传入函数，也可能通过解引用修改原对象；“按值传递”先看复制的到底是数值还是地址。
- 引用没有自动延长一般被引用对象寿命的能力。少数临时对象绑定规则以后专门学习；先避免返回局部对象的引用。
- 未初始化数值、悬空指针和越界可能产生未定义行为。偶然输出正确，不是正确性证据；不要为此题主动运行未定义行为。
- 使用 `nullptr` 表示空指针。普通裸指针先理解为访问某对象的通道；谁负责销毁必须另外说明，下一节用所有权表示。
- 作用域结束时，自动对象的析构发生；RAII 将资源释放绑定到对象寿命。不要简单记成“C++ 全部手动释放”。

## 如何运行小例子

确认当前目录是练习目录，再运行：

```bash
g++ -std=c++17 -Wall -Wextra -Wpedantic -g references.cpp -o references
./references
```

第一条是编译，第二条才执行。没有 g++ 时先记录环境缺口；安装与现有项目环境一起处理，不用为了阅读例子更换整套工具链。

## 练习

<a id="ex1"></a>

### 第 1 题：被改变的是哪个 q？约 15 分钟

预测完整例子的两行输出。再在自己的代码里加入 `void by_pointer(double* q)`，让它检查非空后给目标加 1.0；用 `&position` 调用。

解释为什么参数里复制了指针，调用者的数值仍会改变。给它传 nullptr 时，你选择什么行为？先声明再实现。

<a id="ex2"></a>

### 第 2 题：const 限制了什么？约 15 分钟

```cpp
double a = 0.1;
double b = 0.2;
const double* p = &a;
double* const fixed = &a;
```

下面每行独立判断：`*p = 0.5;`、`p = &b;`、`*fixed = 0.5;`、`fixed = &b;`。

不合法的行一次只编译一行，观察诊断，再恢复到能编译的版本。不要同时堆四个错误增加干扰。

<a id="ex3"></a>

### 第 3 题：返回值离开函数后还存在吗？约 15 分钟

只阅读，不执行下面的错误片段：

```cpp
const double& bad_position() {
    double local = 0.2;
    return local;
}
```

解释 local 何时销毁。改成一个安全地返回位置数值的函数，并说明为什么“不复制任何东西”并不值得成为这道题的目标。

<a id="ex4"></a>

### 第 4 题：写一个有明确输入边界的小函数。后续约 30 分钟

自己实现 `double clamp_position(double q, double lower, double upper)`：

- 三个数必须有限，lower <= upper，否则抛 `std::invalid_argument`。
- 有效输入返回限制到区间内的位置。
- q 在区间内不变，边界包含在区间内，不修改调用者。

检查低于下界、区间内、高于上界、相等边界、反向边界和 NaN。解释为什么这里三个 double 按值传递已经合适。

本题验证的是数值函数，不是完整机器人限位方案；真实控制还要考虑时序、速度、状态和平台规则。

## 直觉与回顾

引用像给同一份东西起别名，指针像持有它的地址。地址还写在纸上，房间里的东西也可能已经搬走；生命周期问题关心的正是这个落差。

阅读 C++ 时，可以在脑中不断问两句：“这个名字现在指向谁？”“下一次使用时它还在吗？”很多看上去复杂的符号，会因此回到具体对象与时间上。

写下一个你原来依赖直觉、现在能用生命周期解释的例子，并说明它会怎样出现在节点、消息或回调里。

