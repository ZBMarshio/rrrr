# SIM-08：提示与参考答案

[返回题目](../讲义/SIM-08_Gymnasium与环境接口.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

Pendulum-v1 动作为单个力矩，观测为 cos(theta)、sin(theta)、角速度；默认动力学与本章转子不同。用 float32、shape=(1,) 的零动作；实际核对采用 max_episode_steps=5、seed=7、render_mode=None，末步截断且未自然终止。

相同 seed 与动作序列在该固定环境版本下复现观测；env.action_space.sample() 若另用，要单独控制其种子。

<a id="ex2"></a>

## 第 2 题

数学映射得到 [-2,0,2]。单位由接口契约给出，可能是力矩或其他量，公式自己不能判断：

```python
def scale_normalized_action(action, lower, upper):
    a, lo, hi = [np.asarray(v, dtype=float) for v in (action, lower, upper)]
    if a.ndim != 1 or a.size == 0 or lo.shape != a.shape or hi.shape != a.shape:
        raise ValueError("matching nonempty action vectors required")
    if any(not np.isfinite(v).all() for v in (a, lo, hi)) or np.any(lo >= hi):
        raise ValueError("finite action and ordered limits required")
    if np.any(a < -1) or np.any(a > 1):
        raise ValueError("normalized action outside [-1,1]")
    return lo+(a+1)*0.5*(hi-lo)
```

此局部函数返回浮点数学值；交给具体环境前按其 action_space 明确 dtype，并检查范围/形状。是否限幅是上层明确策略，本例选择拒绝越界。

<a id="ex3"></a>

## 第 3 题

普通转移为 10.9，真正终止为 1，外部截断在本例假设下仍为 10.9。

```python
def episode_flags(task_success, task_failure, step_count, max_steps):
    if not isinstance(task_success, bool) or not isinstance(task_failure, bool):
        raise ValueError("boolean task events required")
    if not isinstance(step_count, int) or not isinstance(max_steps, int) or step_count < 0 or max_steps < 1:
        raise ValueError("valid integer counters required")
    terminated = task_success or task_failure
    truncated = step_count >= max_steps and not terminated
    return terminated, truncated

def bootstrap_target(reward, gamma, next_value, terminated):
    if not isinstance(terminated, bool) or not np.isfinite([reward, gamma, next_value]).all() or not 0 <= gamma <= 1:
        raise ValueError("finite value target inputs required")
    return float(reward if terminated else reward+gamma*next_value)
```

episode_flags 是本题的终端优先约定；一些包装器在同一步也会返回两个 True。只要真正终止为 True，本例目标不 bootstrap；实际算法还要处理有效结束前观测与自身估计方式。

<a id="ex4"></a>

## 第 4 题

卡片首先说明任务、观测与动作的来源/单位/频率，再写初态、复位、reward 和独立成功条件。检查目标/速度/剩余时间是否需要进入观测。

完整 Env、训练算法与评测组织由你实现。本章只验证基础 API 与边界逻辑，不声称完成机器人 RL 环境或训练。

