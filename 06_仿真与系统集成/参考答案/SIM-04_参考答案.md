# SIM-04：提示与参考答案

[返回题目](../讲义/SIM-04_MoveIt模型场景与执行.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

答案取决于实际选定示例。应能从 launch 追到模型/语义配置、规划与限制文件、控制器配置及反馈来源。仅有 move_group 包文件不能证明 Panda 配置或整套演示可运行。

<a id="ex2"></a>

## 第 2 题

复用第二章 is_fresh。下面只是教学用位置请求门控，不检查真实 IK、碰撞或规划可行性：

```python
def plan_request_gate(request, *, groups, frame, scene_id, last_state_ns, now_ns, max_age_ns):
    if not isinstance(request, dict):
        return False, "request_type"
    if request.get("group") not in groups:
        return False, "unknown_group"
    if request.get("frame") != frame:
        return False, "frame_mismatch"
    if request.get("scene_id") != scene_id:
        return False, "scene_mismatch"
    if not is_fresh(last_state_ns, now_ns, max_age_ns):
        return False, "state_stale_or_clock_mismatch"
    try:
        goal = np.asarray(request.get("goal_xyz"), dtype=float)
    except (TypeError, ValueError):
        return False, "invalid_goal"
    if goal.shape != (3,) or not np.isfinite(goal).all():
        return False, "invalid_goal"
    return True, "requires_framework_checks"
```

context 和同源整数 ns 时间由输入层验证。通过之后，完整姿态/任务约束、当前机器人状态、场景有效性、IK、碰撞、轨迹与执行仍需检查。

<a id="ex3"></a>

## 第 3 题

合格记录含 planning frame、group、TCP/link、场景、起始状态、目标、限制、预算、规划结果和执行后端。错误码由实际运行决定，不预填。

本次没有运行 MoveIt 完整示例。小函数或第四章碰撞反例不能代替框架规划证据；也不能关闭碰撞检查来换取成功。

<a id="ex4"></a>

## 第 4 题

复用第二章轨迹验证与控制链，SIM-06 处理名称/单位。规划成功、动画播放、action 返回与实际任务到达分别记录；仅记录其中一个不自动证明其他项。

