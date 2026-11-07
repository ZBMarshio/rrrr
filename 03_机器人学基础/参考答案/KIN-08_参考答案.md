# KIN-08：提示与参考答案

[返回题目](../讲义/KIN-08_动力学与静力学直觉.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

负载通常改变惯性与重力等项；高速运动会使速度相关项更明显；姿态改变质量分布相对转轴与重力力臂；阻尼在该模型中给 b qd。

多个关节共同带动连杆，某一关节加速可能需要其他关节参与，M 因而可有耦合项并随构型变化。

水平 2R 的理想质心高度不随这些 q 改变，重力势能对 q 的导数为零；重量由结构支撑承担，不等于重力不存在。

<a id="ex2"></a>

## 第 2 题

```python
import math

def pendulum_acceleration(q, qd, torque, *, mass=1.0, lc=0.2, inertia=0.05,
                          damping=0.02, gravity=9.81):
    if not all(math.isfinite(v) for v in (q, qd, torque, mass, lc, inertia, damping, gravity)):
        raise ValueError("finite pendulum parameters required")
    if mass <= 0 or lc <= 0 or inertia <= 0 or damping < 0 or gravity < 0:
        raise ValueError("invalid pendulum parameters")
    return (torque - damping*qd - mass*gravity*lc*math.cos(q)) / inertia
```

初始 qdd=-1.962/0.05=-39.24 rad/s²；仅 I 翻倍变为 -19.62。若同形状质量和 I 一起翻倍，此刻 tau=qd=0，自由重力加速度不变。

q=-π/2 为向下平衡，附近小偏移有恢复趋势；q=π/2 为向上平衡，理想点力矩为零但小偏移有离开趋势。精确初值没有扰动时，不能要求数值程序凭空显示失稳。

<a id="ex3"></a>

## 第 3 题

J=[[-0.2,-0.2],[0.3,0]]，tau_external=(-1.3,-0.4) N·m，delta_x=(0.0002,0.0003) m。

两边线性虚功均为 -0.0005 J。若无重力/其他项且静止，tau_actuator=(1.3,0.4) N·m 抵消外力。这是环境对机器人施力的约定。

用实际有限步 FK 位移计算做功会有高阶差异；缩小步长后应与局部虚功关系更接近。

<a id="ex4"></a>

## 第 4 题

能量函数：

```python
import math

def pendulum_energy(q, qd, *, mass=1.0, lc=0.2, inertia=0.05, gravity=9.81):
    return 0.5*inertia*qd*qd + mass*gravity*lc*math.sin(q)
```

从运动方程得到 dE/dt=tau*qd-b*qd²。无输入、无阻尼时为零；正阻尼时非正。

你可先实现半隐式 Euler：先按当前加速度更新 qd，再用新 qd 更新 q；这是数值近似，不会精确守恒。比较更小步长与理论关系，必要时再查更高阶积分器。

输出时间、q、qd、E、步长、阻尼与最大能量偏差；不预填你的仿真结果。这里是独立竖直摆模型，不能当成水平 2R 的实测数据。

