# ENG-05：读懂容器、对象接口和所有权

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#eng-05) · [前置](ENG-04_CPP引用指针与生命周期.md) · [提示与答案](../参考答案/ENG-05_参考答案.md)

<a id="intro"></a>

## 导读

**为什么学这一节。** 关节数组、节点成员和回调常同时出现。容器组织数据，类表达接口，所有权决定对象存活；分开理解后，一长行代码才容易读。

**学完会有什么变化。** 从遇到vector、shared_ptr就整句跳过，进到能检查元素顺序、复制或引用、资源持有关系与回调寿命。

**接下来能做什么。** 可以组织简单C++数据对象，阅读ROS容器与回调代码，追踪[ROS-08](../../02_ROS2与机器人系统/讲义/ROS-08_ros2_control与执行接口.md#intro)中控制器和硬件对象怎样被持有。

## 目标与资料

跟 W05 的 ROS 节点一起读：看出 vector 保存了什么，函数是否修改对象，shared_ptr 为什么出现在接口里，回调依赖谁继续存活。

| 资料 | 选读范围 |
|---|---|
| [LearnCpp：vector 入门](https://www.learncpp.com/cpp-tutorial/introduction-to-stdvector-and-list-constructors/) | 定义、列表构造与大小；循环与下标按实际代码补 |
| [LearnCpp：classes 入门](https://www.learncpp.com/cpp-tutorial/introduction-to-classes/) | 成员数据、成员函数、访问控制；constructor/const member functions 按标题查 |
| [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) | R.3 裸指针、R.20/R.21 所有权、R.22/R.23 make_*、R.24 循环引用 |

先用标准库容器，不自己实现动态数组；模板元编程、复杂继承与自定义分配器以后再学。

## 把三件事分开看

1. **数据组织：** vector 是一段按顺序管理的元素；map 是按键查找的关联容器。关节顺序应来自明确接口，不来自你对容器排列的猜测。
2. **对象接口：** 类把状态与行为放在一起。构造函数建立有效状态，成员函数表达允许的操作，const 成员函数限制通过本对象接口的修改。
3. **资源所有权：** 谁负责让对象继续存在、最终何时销毁？unique_ptr 表示独占所有权；shared_ptr 允许共同持有；裸指针/引用通常只访问而不负责所有权。

这三件事可能同时出现在一行 ROS 代码里，但可以逐项读。

## 重点细节

- `vector<double> a(3, 0.5)` 表示三个 0.5；`vector<double> b{3, 0.5}` 表示两个元素 3.0、0.5。括号选择会改变含义。
- `for (auto x : values)` 在这里复制每个 double；要修改元素用 `auto&`，只读复杂元素常用 `const auto&`。
- `vector::at` 做范围检查并可能抛异常；`operator[]` 不替你检查。边界错误不能靠“这次没崩溃”通过验收。
- vector 扩容可能让指向旧元素的指针、引用和迭代器失效；理解其风险即可，先不深挖全部失效规则。
- `map[key]` 在缺键时会插入默认值。只是检查设备有没有某关节时，优先 find/at 等符合意图的接口。
- `std::move` 本身是允许移动的转换；unique_ptr 的移动构造才完成所有权转移。移动后不要继续当作仍持有该资源来解引用。
- shared_ptr 的引用计数管理不等于所指对象的并发访问安全；智能指针也不会自动解决坐标、时序和数据竞争。
- lambda 中 `[this]` 保存 this 指针，不自动延长对象寿命。看到回调时先找注册者、执行者和对象持有者，不只背捕获语法。

## 练习

<a id="ex1"></a>

### 第 1 题：容器里到底装了几个值？约 20 分钟

独立预测下列各段：

1. `std::vector<double> a(3, 0.5);` 与 `std::vector<double> b{3, 0.5};` 的 size 和内容。
2. `v = {0.1, 0.2}` 后，`for (auto x : v) { x = 0.0; }` 能否清零 v？
3. 把 auto x 改为 auto& x 后呢？为什么？

写自己的 main 打印结果；若编译器提示某个 x 只写不用，结合警告理解数据没有回到哪里。

<a id="ex2"></a>

### 第 2 题：关节名存在，不代表顺序一致。约 20 分钟

某接口规定命令顺序为 `{"joint_2", "joint_1"}`，当前状态 map 内容为 `{{"joint_1",0.1},{"joint_2",0.2}}`。

自己生成符合接口顺序的 vector，并明确处理缺键。然后回答：直接遍历 map 得到的结果是否一定符合命令顺序？查询 `state["joint_3"]` 会不会改变 map？

<a id="ex3"></a>

### 第 3 题：把所有权画出来。约 20 分钟

阅读这个独立片段，头文件为 memory、utility：

```cpp
struct Joint {
    double position = 0.0;
};
auto owner = std::make_unique<Joint>();
owner->position = 0.2;
auto next = std::move(owner);
auto shared = std::make_shared<Joint>();
auto also_shared = shared;
```

回答：

1. 哪些智能指针此时持有对象？owner 能否解引用？
2. 为什么不能用 `auto next = owner;` 复制 unique_ptr？
3. 此处两个 shared_ptr 都销毁后，对象何时释放？如果对象间形成 shared_ptr 环呢？

先画图再运行合法部分，不主动执行空指针解引用。

<a id="ex4"></a>

### 第 4 题：一个简单类的接口。后续约 30 分钟

自己写 `Sampler`，保存最近一条两关节 vector：

- 构造后有两个零位置。
- `update(const std::vector<double>& values)` 检查长度和有限性后复制数据；无效时抛异常且旧状态保持不变。
- `state() const` 返回 `const std::vector<double>&`。

验证更新后改变调用者的输入 vector 不会改变内部状态。解释 state 返回引用为何依赖 Sampler 寿命，以及保存引用期间再次 update 后是否还能把它当作“更新前快照”。

## 最低验收

W05 先能读 vector 与常见指针接口，说明一个回调所用对象由谁持有；用第 1、3 题检查。第 2、4 题随后与关节顺序和接口适配一起做。

## 直觉与回顾

所有权关心“谁负责保管到最后”，访问方式关心“谁现在可以看或改”。拿到一份地址，不一定接过了保管责任；接过 unique_ptr 则明确接过了责任。shared_ptr 让多人共同保管，也增加了弄清最后释放时刻的工作。

类接口像对外承诺：别人能给什么、会得到什么、失败后状态怎样。一个很小的类只要把这些说清，就比为了“面向对象”增加多层继承更容易使用。

请用这节的一个例子解释“复制数据”和“共同持有对象”有什么不同，再找到你的 ROS 代码里一处相应写法。

