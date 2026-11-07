# SIM-03：提示与参考答案

[返回题目](../讲义/SIM-03_时间渲染与接触.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

500 次物理推进、100 次控制更新、25 次显示采样，按半开区间约定计数。若记录初始状态及每次 step 后状态，共 501 行，末时刻 0.5 s。

<a id="ex2"></a>

## 第 2 题

在本节整数步保持循环中，非整数比应明确拒绝；其他调度器可以有自己的时间策略，但需说明误差和状态时间。

```python
def control_stride(physics_dt, control_dt, atol=1e-10):
    if not np.isfinite([physics_dt, control_dt, atol]).all() or min(physics_dt, control_dt, atol) <= 0:
        raise ValueError("positive finite time configuration required")
    stride = round(control_dt/physics_dt)
    if stride < 1 or abs(stride*physics_dt-control_dt) > atol:
        raise ValueError("control period must be an integer number of physics steps")
    return stride
```

本章图的显示抽样只读取已算出的日志，不再次推进 data。真实在线渲染若引入共享状态/调度变化，应另查具体实现。

<a id="ex3"></a>

## 第 3 题

自由落体估算 `sqrt(2*(0.3-0.05)/9.81)≈0.225762 s`，碰撞离散检查与软接触响应不保证恰好等于此值。

```python
def contact_report(model, data):
    records = []
    for index in range(data.ncon):
        contact = data.contact[index]
        wrench = np.zeros(6)
        mj.mj_contactForce(model, data, index, wrench)
        records.append({
            "geom1": model.geom(int(contact.geom1)).name,
            "geom2": model.geom(int(contact.geom2)).name,
            "distance_m": float(contact.dist),
            "normal_force_N": float(wrench[0]),
        })
    return records
```

这里 force[0] 是所用接触坐标下的法向分量；完整六维量与传感器/世界坐标的转换另推导。先使 data 的派生量与当前状态同步，逐接触记录，不盲目把所有接触力相加当 TCP 力。

<a id="ex4"></a>

## 第 4 题

保持 solver、材料、初态、观察窗口一致；比较接触开始、最大压入、力峰值与尾部状态。步长减小后的收敛趋势和物理真实性分开验证；具体参考结果见核对记录。

