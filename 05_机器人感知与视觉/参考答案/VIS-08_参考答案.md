# VIS-08：提示与参考答案

[返回题目](../讲义/VIS-08_时序误差与评测.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

时间量级 0.2×0.08=0.016 m。小角度杠杆量级 0.6×π/180≈0.010472 m。

这是条件化估算。完全静止的目标与固定坐标链没有该相对运动位移，但旧数据仍可能不满足任务的新鲜度/状态要求。误差方向与实际运动和变换有关。

<a id="ex2"></a>

## 第 2 题

方差近似 `(0.8/600)²×1²+(60/600)²×0.01²`，标准差约 0.001666667 m。

```python
def lateral_sigma(z, focal_px, pixel_offset, sigma_pixel, sigma_z):
    values = (z, focal_px, pixel_offset, sigma_pixel, sigma_z)
    if not np.isfinite(values).all() or min(z, focal_px) <= 0 or min(sigma_pixel, sigma_z) < 0:
        raise ValueError("valid depth, focal length and noise scales required")
    return float(np.sqrt((z/focal_px*sigma_pixel)**2+(pixel_offset/focal_px*sigma_z)**2))
```

若深度偏置 +0.01 m，此例 X 偏置约 +0.001 m；标准差本身不包含该偏差。可同时报告均值偏差、离散程度与 RMSE，不把独立无偏假设套到所有误差。

<a id="ex3"></a>

## 第 3 题

复用 [is_fresh](../../02_ROS2与机器人系统/参考答案/ROS-06_参考答案.md#ex4)，但它单独只检查给定时钟下的时间差。重复图像 ID、采样时间、标定/图像契约、定位有效性另检。

可将旧帧/倒退记为 observation_stale 或 clock_mismatch，错参数记为 calibration_mismatch，无检测记为 no_detection。拒绝目标后是否取消正在执行的动作，要按实际系统状态与接口处理，不在感知函数里假定完成。

<a id="ex4"></a>

## 第 4 题

先明确误差数组只来自有有效独立真值的样本，失败次数另外保留，不能静默删除 NaN 让报告变好：

```python
def position_error_summary(errors_m):
    errors = np.asarray(errors_m, dtype=float)
    if errors.ndim != 1 or errors.size == 0 or not np.isfinite(errors).all() or np.any(errors < 0):
        raise ValueError("nonempty finite nonnegative position errors required")
    return {"count": int(errors.size), "mean_m": float(np.mean(errors)),
            "median_m": float(np.median(errors)), "p95_m": float(np.percentile(errors, 95)),
            "max_m": float(np.max(errors))}
```

附预定总数、有效真值样本数、成功数、失败阶段、重试规则和版本。没有独立空间真值时，保留重投影/一致性与接口结果，把真实空间精度标为未验证。

