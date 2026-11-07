# KIN-09：给以后读论文和库留一个入口

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#kin-09) · [提示与答案](../参考答案/KIN-09_参考答案.md)

<a id="intro"></a>

## 导读

**为什么学这一节。** 读机器人库和论文时，旋量、李群和矩阵指数会反复出现。本节先给这些对象一个几何位置，帮助你知道什么时候值得深入。

**学完会有什么变化。** 从看到符号就跳过整段推导，进到能识别旋转/位姿与其生成量，核对排列、坐标和空间雅可比的含义。

**接下来能做什么。** 可以阅读指数积FK和相关库接口，为以后位姿优化、动作表示或[CTRL-08](../../04_机器人控制与运动规划/讲义/CTRL-08_最优控制与MPC导读.md#intro)中的模型方法补理论入口；当前先做到识别与核对。

## 本节是选读

先能认出对象、方向和约定，不要求 W03/W06 学完整套李群推导。以后使用空间雅可比、优化位姿或研究动作表示时再深入。

| 作者资料 | 选读 |
|---|---|
| [Modern Robotics 3.3.2/3.3.3](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-3-3-exponential-coordinates-of-rigid-body-motion/) | twist、指数坐标、SE(3) 与 se(3) 的对应 |
| [第 4.1.1/4.1.2 视频目录](https://modernrobotics.northwestern.edu/nu-gm-book-resource/) | 空间/本体指数积，先看固定轴与零位 |
| [作者 Python 库](https://github.com/NxRLab/ModernRobotics/tree/master/packages/Python) | VecTose3、MatrixExp6、FKinSpace、JacobianSpace，按函数查 |

作者代码用于教学核对，不能因此视为所有生产场景的数值实现。

## 先认识两种不同对象

```text
SE(3) 中的位姿 T = [R p; 0 1]
se(3) 中的 twist 矩阵 [V] = [[omega] v; 0 0]
```

[omega] 是叉乘矩阵，不是合法旋转矩阵；底行也不同。矩阵指数将相应运动的生成量变成有限刚体变换，不能把逐元素 exp 当作矩阵指数。

本节沿 Modern Robotics 采用 V=[omega;v]，角速度在前。别的库可能反过来，先核对排列。

## 同一台 2R 的另一种 FK 写法

零位 M 是 x 平移 0.5 m。两个空间转轴都沿 z；第二轴经过 r=(0.3,0,0)：

```text
S1 = (0,0,1, 0,0,0)
S2 = (0,0,1, 0,-0.3,0)
T(q) = exp([S1] q1) exp([S2] q2) M
```

转动轴单位方向 omega，经过点 r 时，纯转动螺旋的 v=-omega×r。这个 v 不等于“某个末端点的坐标差”。

## 为什么不能把空间雅可比的下三行直接当位置雅可比

按这里的定义：

```text
[V_space] = Tdot @ inverse(T)
v_space = pdot - omega_space × p
因此 pdot = v_space + omega_space × p
```

只动基座原点处的第一轴时，S1 的 v 部分为零，但远处末端显然会沿圆周运动。末端速度来自 omega×p，这就给了一个具体反例。

本体 twist 中 v_body=R.T@pdot；空间/本体转换可以用 Adjoint，进一步推导以后学。位置、角速度和 twist 的差别先用例子记住。

## 练习

<a id="ex1"></a>

### 第 1 题：叉乘矩阵不是旋转矩阵。约 20 分钟，选读

写 skew3(omega)，检查 skew3(omega)@v 等于 cross(omega,v)。说明它与 R 在形状相同之外有什么区别，se(3) 与 T 的底行是什么。

<a id="ex2"></a>

### 第 2 题：与作者库的 FK 对照。约 25 分钟，选读

按上面定义写 M 与 Slist，两根螺旋作为列。使用已有作者库或其明确版本的源码，对照三组关节角的 FKinSpace 和自己的 fk_pose。

不必为 W03 提前安装库；先做手算/矩阵链对照也可以，库检查另记。

<a id="ex3"></a>

### 第 3 题：空间雅可比转换成位置导数。约 25 分钟，选读

取 q=(0.4,-0.6)，从作者 JacobianSpace 得到每列 omega_i、v_i，使用 pdot_i=v_i+omega_i×p，取 xy 两行，再与自己的 jacobian_xy 对照。

说明直接取原矩阵下三行为什么会错。

<a id="ex4"></a>

### 第 4 题：同样沿 x 加 0.1，是谁的 x？约 20 分钟，选读

当前 T 的朝向为绕 z 正转 90°，位置为 (1,0,0) m。Delta 是沿自身 x 平移 0.1 m 的刚体平移矩阵。

比较 Delta@T 与 T@Delta 的新位置，解释基座增量与末端局部增量。这种动作定义差异会怎样影响后续控制、RL 或模仿学习的数据接口？

## 直觉与回顾

这些符号的价值是统一表示，不是让简单问题必须变复杂。你已经能验证二维例子，再看指数积时，可以不断问“它和我原来的哪一段运动对应”。

以后遇到论文里的 action/pose delta，先确认坐标与左右乘，往往比先记住方法缩写更有用。复盘写一个已经能辨认的对象和一个暂时留待深入的推导。

