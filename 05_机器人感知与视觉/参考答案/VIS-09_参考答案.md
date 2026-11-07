# VIS-09：提示与参考答案

[返回题目](../讲义/VIS-09_视觉伺服SLAM与触觉导读.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

v_camera=0.5×0.8×20/600≈0.0133333 m/s。udot=-10 px/s，前向一步 e_next=19.8 px。

```python
def servo_feature_step(error_px, dt, *, focal_px=600.0, depth=0.8,
                       gain=0.5, velocity_limit=0.02):
    values = (error_px, dt, focal_px, depth, gain, velocity_limit)
    if not np.isfinite(values).all() or min(dt, focal_px, depth, gain, velocity_limit) <= 0:
        raise ValueError("finite feature and positive model parameters required")
    desired_velocity = gain*depth*error_px/focal_px
    camera_velocity = float(np.clip(desired_velocity, -velocity_limit, velocity_limit))
    feature_rate = -focal_px/depth*camera_velocity
    return camera_velocity, float(error_px+dt*feature_rate)
```

它只更新理想模型，不向机器人发指令。无饱和时 e_next=(1-λdt)e；过大步长也可能使离散关系不稳定。物体沿 +x 运动时，相机坐标点的变化符号不同，要重新写模型。

<a id="ex2"></a>

## 第 2 题

对同一 R，`R(2P)+2t=2(RP+t)`；归一化投影会约掉 2。已知尺寸/基线或米制深度可提供尺度，前提是单位、几何与时间对应。

学习式深度可能带有训练先验，也需要在实际域验证尺度和误差；不能只看到深度图外观合理就当可靠米制量。

<a id="ex3"></a>

## 第 3 题

接触图像至少需要设备/分辨率/曝光、采样时间、标定版本、参考无接触图、图像到接触状态的模型与有效范围。六维力还要单位、坐标/作用点、零偏/工具重力和变换。

从图像到物理力需要额外模型与验证，再经工具/传感器到基座的关系转换。滑移分数同样不应直接命名为速度或力。

<a id="ex4"></a>

## 第 4 题

没有统一论文答案。合格阅读卡能说清观测如何支持状态/表征、怎样影响决策、依赖什么假设，以及怎样对照基线判断有效。

下一项实验应可小规模完成，例如固定图像序列验证一次坐标/尺度/时延，而不是仅因论文用了多个模块就同时搭建全部环境。

