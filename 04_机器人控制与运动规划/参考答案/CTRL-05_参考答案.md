# CTRL-05：提示与参考答案

[返回题目](../讲义/CTRL-05_末端到达与轨迹跟踪.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

最低记录可以是：base 下 tool0 的位置目标/m、关节顺序/rad、IK success/reason/residual、轨迹 T、接口量/单位、带时间的 q_actual、实际 TCP 误差、结束原因。

理想情况下 q_actual 接近 q_ref，末尾接近 q_goal；代码里仍要分别保存。执行结束、控制器报告成功、任务误差合格是需要关联核对的证据。

<a id="ex2"></a>

## 第 2 题

复用 fk_xy。离线片段：

```python
def joint_line_samples(q_start, q_end, count=101):
    start, end = np.asarray(q_start, dtype=float), np.asarray(q_end, dtype=float)
    if start.shape != (2,) or end.shape != (2,) or not np.isfinite([start, end]).all():
        raise ValueError("finite 2R configurations required")
    if not isinstance(count, int) or count < 2:
        raise ValueError("at least two samples required")
    s = np.linspace(0.0, 1.0, count)
    joints = start[None, :] + s[:, None]*(end-start)[None, :]
    points = np.asarray([fk_xy(q) for q in joints])
    return s, joints, points
```

点到线段距离采用投影后夹紧到 [0,1]；CTRL-06 有局部函数可复用。结果不为零意味着关节直线与 TCP 直线不同，不是 IK 或控制器出错。

<a id="ex3"></a>

## 第 3 题

下面依赖第三章已经验证的 solve_ik_position；保持其返回信息，不另写求解器：

```python
def cartesian_ik_samples(points, q0, *, lower=(-1.6, -2.4), upper=(1.6, 2.4)):
    points = np.asarray(points, dtype=float)
    previous = np.asarray(q0, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) == 0:
        raise ValueError("nonempty Nx2 path required")
    if previous.shape != (2,) or not np.isfinite(points).all() or not np.isfinite(previous).all():
        raise ValueError("finite 2R inputs required")
    joints, infos = [], []
    for index, target in enumerate(points):
        q, info = solve_ik_position(target, previous, lower=lower, upper=upper)
        infos.append(info)
        if not info["success"]:
            return np.asarray(joints).reshape(-1, 2), {
                "success": False, "failed_index": index, "reason": info["reason"], "points": infos,
            }
        joints.append(q.copy())
        previous = q
    return np.asarray(joints), {
        "success": True, "failed_index": None, "reason": "sampled_path_solved", "points": infos,
    }
```

同时核对实际 FK 残差和 `max(abs(diff(q,axis=0)))`。差分速度还需明确相邻参考点的时间差；之后重新平滑/时间参数化仍要检查几何偏离、限位与碰撞。

这些样本求解成功，不等于获得了连续无碰撞、动力学可行并实际跟踪成功的路径。

<a id="ex4"></a>

## 第 4 题

此处 `J=[[-0.2,-0.2],[0.3,0]]` m/rad，解得 qd=[0,-0.1] rad/s。以 ε 秒推进 q+ε qd，FK 差分应接近目标速度；ε 过大时忽略的曲率开始明显。

位置接口可生成带时间且经过限制检查的关节位置参考；反馈仍来自模型或硬件。误差闭环必须使用实际观测；单纯沿参考积分是一种参考生成。

