# CTRL-01：提示与参考答案

[返回题目](../讲义/CTRL-01_离散PID与反馈.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

新积分 0.032 rad·s，raw=1.6+0.064-0.08=1.584 N·m，未饱和，command 相同。

下面的局部函数也供 CTRL-02 使用；抗饱和是候选积分会加深饱和时拒绝该次积分的一种教学写法：

```python
import math

def pid_step(error, velocity, integral, dt, *, kp, ki, kd, limit,
             reference_velocity=0.0, anti_windup=False):
    values = (error, velocity, integral, dt, kp, ki, kd, limit, reference_velocity)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("finite PID inputs required")
    if dt <= 0 or limit <= 0 or min(kp, ki, kd) < 0:
        raise ValueError("invalid PID configuration")
    candidate = integral + error*dt
    raw = kp*error + ki*candidate + kd*(reference_velocity-velocity)
    deepens_saturation = (raw > limit and error > 0) or (raw < -limit and error < 0)
    next_integral = integral if anti_windup and deepens_saturation else candidate
    raw = kp*error + ki*next_integral + kd*(reference_velocity-velocity)
    command = max(-limit, min(limit, raw))
    return command, next_integral, raw
```

Ki≥0 是本函数约定。积分、raw 与 applied 都有独立意义；D 的速度来源要核对。抗饱和策略还有其他实现，不把这段代码当成唯一标准。

<a id="ex2"></a>

## 第 2 题

先自己写闭环，再用以下参考结构核对。它依赖上面的 pid_step；reference(t) 返回两个标量 (q_ref,qd_ref)，使用半隐式 Euler 和采样保持：

```python
from collections import deque
import numpy as np

def simulate_joint(reference=None, gains=(8.0, 0.0, 0.8), *, duration=3.0,
                   h=0.001, control_steps=5, torque_limit=2.0, load=0.0,
                   anti_windup=False, delay_ticks=0):
    if not np.isfinite([duration, h, load]).all() or duration <= 0 or h <= 0:
        raise ValueError("invalid simulation time or load")
    if not isinstance(control_steps, int) or control_steps < 1:
        raise ValueError("control_steps must be positive integer")
    if not isinstance(delay_ticks, int) or delay_ticks < 0:
        raise ValueError("delay_ticks must be non-negative integer")
    steps = round(duration/h)
    if steps < 1 or abs(steps*h-duration) > 1e-9:
        raise ValueError("duration must be an integer number of h steps")
    kp, ki, kd = gains
    reference = reference or (lambda t: (0.5, 0.0))
    q = qd = integral = command = applied = raw = 0.0
    pending = deque([0.0]*delay_ticks)
    fields = ("t", "q", "qd", "ref", "ref_vel", "u_cmd", "u_applied", "u_raw", "integral")
    log = {name: [] for name in fields}
    for k in range(steps+1):
        t = k*h
        q_ref, v_ref = map(float, reference(t))
        if not np.isfinite([q_ref, v_ref]).all():
            raise ValueError("invalid reference")
        if k % control_steps == 0:
            command, integral, raw = pid_step(
                q_ref-q, qd, integral, h*control_steps,
                kp=kp, ki=ki, kd=kd, limit=torque_limit,
                reference_velocity=v_ref, anti_windup=anti_windup,
            )
            pending.append(command)
            applied = pending.popleft()
        values = (t, q, qd, q_ref, v_ref, command, applied, raw, integral)
        for name, value in zip(fields, values):
            log[name].append(value)
        if k == steps:
            break
        acceleration = (applied - 0.1*qd - load) / 0.05
        qd += h*acceleration
        q += h*qd
        if not np.isfinite([q, qd]).all():
            raise FloatingPointError("simulation diverged")
    return {name: np.asarray(values) for name, values in log.items()}
```

delay_ticks 以控制周期计数，0 表示当次命令立即应用。该函数只限幅力矩，未建机械位置止挡、完整电机或 2R 耦合模型。函数片段由你组织成项目。

验收：q 来自模型推进；控制更新间 u 保持；raw/command/applied 可分别追溯；P/PD 只改 kd；相同输入新运行可复跑。

<a id="ex3"></a>

## 第 3 题

均匀采样时，可用 sqrt(mean(error²)) 与 max(abs(error))；尾部窗口提前选定。阶跃专用的一个指标片段：

```python
import numpy as np

def step_metrics(log, target=0.5, initial=0.0, band_fraction=0.02, hold_time=0.2):
    t, q = np.asarray(log["t"]), np.asarray(log["q"])
    amplitude = target-initial
    if amplitude == 0 or band_fraction <= 0 or hold_time < 0:
        raise ValueError("nonzero step and valid metric parameters required")
    error = target-q
    normalized = (q-initial)/amplitude
    tolerance = abs(amplitude)*band_fraction
    outside = np.flatnonzero(np.abs(error) > tolerance)
    candidate = int(outside[-1]+1) if outside.size else 0
    settling = None
    if candidate < len(t) and t[-1]-t[candidate] >= hold_time:
        settling = float(t[candidate]-t[0])
    return {
        "rmse_rad": float(np.sqrt(np.mean(error**2))),
        "max_error_rad": float(np.max(np.abs(error))),
        "overshoot_percent": float(max(0.0, np.max(normalized)-1.0)*100),
        "settling_s_in_window": settling,
    }
```

这只适用于已验证的恒定阶跃与均匀日志，不能直接套到变化轨迹。settling 只是当前观测窗口的结论；末尾不足保持时长就不宣布稳定。误差可能一开始最大，统计时明确是否包含该样本。

<a id="ex4"></a>

## 第 4 题

稳态 qd=qdd=0 且未饱和，PD 有 Kp*(q_ref-q)=load，因此误差 load/Kp=0.025 rad。若饱和/未稳定，这个推导的前提不满足。

可比较 gains=(8,0,0.8) 与 (8,4,0.8)，load=0.2、相同长窗口，例如 10 s。观察积分是否逐渐提供负载补偿；不预填你自己的误差，不承诺任意 Ki 都稳定。

