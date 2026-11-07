# SIM-02：提示与参考答案

[返回题目](../讲义/SIM-02_执行器与控制语义.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

局部名称/地址检查：

```python
def hinge_addresses(model, joint_name):
    joint = model.joint(joint_name)
    joint_id = int(joint.id)
    if int(model.jnt_type[joint_id]) != int(mj.mjtJoint.mjJNT_HINGE):
        raise ValueError("hinge joint required")
    return joint_id, int(model.jnt_qposadr[joint_id]), int(model.jnt_dofadr[joint_id])
```

2R 的两组地址恰巧为 0/1；这不是通用规律。球落地是 7/6/0：没有 actuator，仍会受重力运动。

<a id="ex2"></a>

## 第 2 题

直接 motor、gear=1 且没有其他执行器时，0.2 对应 0.2 N·m；ctrl=10 在本模型内部被限制后，广义作用为 2 N·m。ctrl 存储仍可能是 10，不能拿它单独证明实际作用。

同一输入 0.2、gear=2 时，执行器力到关节的广义作用为 0.4 N·m。传动比例改变后，位置伺服的目标解释也需要重新核对。

<a id="ex3"></a>

## 第 3 题

在副本中使用这一 actuator 元素，其他模型参数保持一致：

```xml
<position name="position_1" joint="joint_1" gear="1" kp="8" kv="0.8"
          ctrllimited="true" ctrlrange="-1.5 1.5"
          forcelimited="true" forcerange="-2 2"/>
```

小模型中力为 kp*(q_ref-q)-kv*qd，再经配置限制与传动；position 会趋向其位置参考，常力矩 motor 并不把 0.3 rad 当目标。初始瞬间 q 仍来自模型状态。

<a id="ex4"></a>

## 第 4 题

第四章示例 PID 输出 N·m，连接本章 gear=1 的 motor；若 backend 接收位置，要让它接收位置参考并明确下层伺服。归一化动作还需显式反归一化；不能将 PID 力矩原样发送成角度。

