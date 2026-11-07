# CTRL-07：提示与参考答案

[返回题目](../讲义/CTRL-07_阻抗导纳与力反馈.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

A 接近通过力矩实现的关节阻抗结构，但完整行为还取决于动力学与实现；B 接近导纳外环加运动内环。A 的执行端需要适用的力矩/力接口，B 需要可靠外力输入和可跟踪的运动接口。

位置、速度估计、外力测量/估计均有自身条件。内环、限幅、通信与传感滤波会共同影响最终表现；不能单凭控制器名字判断真实性能。

<a id="ex2"></a>

## 第 2 题

接触时令 K(x_ref-x)=k_env(x-x_wall)，解：

`x=(K x_ref+k_env x_wall)/(K+k_env)`。

| K/(N/m) | x/m | 压缩量/m | 接触力幅值/N |
|---|---|---|---|
| 100 | 0.50454545 | 0.00454545 | 4.54545455 |
| 1000 | 0.525 | 0.025 | 25 |

```python
def wall_equilibrium(x_ref, stiffness, *, wall=0.5, environment_stiffness=1000.0):
    values = (x_ref, stiffness, wall, environment_stiffness)
    if not np.isfinite(values).all() or min(stiffness, environment_stiffness) <= 0:
        raise ValueError("finite values and positive stiffnesses required")
    if x_ref <= wall:
        return float(x_ref), 0.0
    x = (stiffness*x_ref+environment_stiffness*wall)/(stiffness+environment_stiffness)
    compression_force = environment_stiffness*(x-wall)
    return float(x), float(compression_force)
```

这是给定弹簧与软墙模型的静态平衡；未包含动态峰值和真实装置限制。

<a id="ex3"></a>

## 第 3 题

静态位移 10/100=0.1 m。D=2 sqrt(MK)=20，是该连续一维模型的临界阻尼；零初始状态下：

`x(t)=0.1[1-(1+10t)exp(-10t)]`。

半隐式 Euler 的局部更新：

```python
def admittance_step(x, xd, force, dt, *, mass=1.0, damping=20.0,
                    stiffness=100.0, x0=0.0):
    values = (x, xd, force, dt, mass, damping, stiffness, x0)
    if not np.isfinite(values).all() or dt <= 0 or mass <= 0 or min(damping, stiffness) < 0:
        raise ValueError("invalid admittance inputs")
    acceleration = (force-damping*xd-stiffness*(x-x0))/mass
    next_velocity = xd+dt*acceleration
    return x+dt*next_velocity, next_velocity
```

对 0≤t≤2 s 比较数值与解析解，并减半 dt 观察误差变化。虚拟模型稳定不等于与真实内环、传感与环境耦合后也满足同样结论。

<a id="ex4"></a>

## 第 4 题

优先核对单位与符号/坐标、传感零偏与工具重力处理、测量时间与滤波延迟、输入接口和实际跟踪误差。也要确认虚拟参数及初始状态。

外力/K 只在相应模型的静态、其他项可忽略时解释偏移。虚拟位移是外环状态，位置命令是发送值，TCP 实际位置来自观测，三者应分别记录。

