# SIM-01：提示与参考答案

[返回题目](../讲义/SIM-01_模型加载循环与状态.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

单关节 nq=nv=nu=1；2R 为 2/2/2。MuJoCo 的 qpos/qvel/ctrl 维度一般不必相同，SIM-02 再用自由关节检查。

```python
from pathlib import Path
import mujoco as mj
import numpy as np

def load_model(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError("existing MJCF file required")
    model = mj.MjModel.from_xml_path(str(path.resolve()))
    return model, mj.MjData(model)
```

<a id="ex2"></a>

## 第 2 题

以下局部复位函数只支持全部为 hinge/slide 的模型；不要用它处理 freejoint：

```python
def reset_hinge_state(model, data, position, velocity=None):
    if model.nq != model.nv or any(
        int(kind) not in (int(mj.mjtJoint.mjJNT_HINGE), int(mj.mjtJoint.mjJNT_SLIDE)) for kind in model.jnt_type
    ):
        raise ValueError("this helper supports scalar hinge/slide joints only")
    q = np.asarray(position, dtype=float)
    v = np.zeros(model.nv) if velocity is None else np.asarray(velocity, dtype=float)
    if q.shape != (model.nq,) or v.shape != (model.nv,) or not np.isfinite(q).all() or not np.isfinite(v).all():
        raise ValueError("finite state with model-matching shape required")
    mj.mj_resetData(model, data)
    data.qpos[:], data.qvel[:] = q, v
    mj.mj_forward(model, data)

def state_snapshot(data):
    return {"time_s": float(data.time), "qpos": data.qpos.copy(),
            "qvel": data.qvel.copy(), "ctrl": data.ctrl.copy(),
            "qfrc_actuator": data.qfrc_actuator.copy()}

def advance_control(model, data, control, substeps=1):
    control = np.asarray(control, dtype=float)
    if control.shape != (model.nu,) or not np.isfinite(control).all():
        raise ValueError("finite actuator-order control vector required")
    if not isinstance(substeps, int) or substeps < 1:
        raise ValueError("positive integer substeps required")
    data.ctrl[:] = control
    for _ in range(substeps):
        mj.mj_step(model, data)
    mj.mj_forward(model, data)
    return state_snapshot(data)
```

单关节初始 tip 为 (0.25 cos0.2,0.25 sin0.2,0) m。100 个 0.001 s 步后时间为 0.1 s；forward 不改变 time。此函数验证形状/有限性，应用边界及模型内部限幅分别核对。

这里将数组类型值与绑定枚举都转成 int 再比较，避免 NumPy 标量与原生绑定枚举在成员判断中的类型差异。

<a id="ex3"></a>

## 第 3 题

复用第三章 fk_xy，比较 data.site("tool0").xpos[:2]；相同 q、长度、零位与轴方向下应一致。当前 MJCF world 与本题的数学基座共原点/轴；接 ROS 后还需明确 world/base 关系。

<a id="ex4"></a>

## 第 4 题

日志使用 state_snapshot 中的 copy。复位还要检查外部控制器积分、延迟队列与计数，SIM-07 展开；mj_resetData 不负责你的 Python 对象状态。

