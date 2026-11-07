# VIS-05：提示与参考答案

[返回题目](../讲义/VIS-05_深度RGBD与点云.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

结果 [1,NaN,2] m。第二台设备需要使用其声明的 scale；编码 dtype 本身不能决定单位。

```python
def depth_to_meters(raw, scale_m):
    raw = np.asarray(raw, dtype=float)
    if raw.ndim < 1 or raw.size == 0 or not np.isfinite(scale_m) or scale_m <= 0:
        raise ValueError("nonempty depth array and positive meters-per-unit scale required")
    valid = np.isfinite(raw) & (raw > 0)
    output = np.full(raw.shape, np.nan)
    output[valid] = raw[valid]*scale_m
    return output
```

此教学契约定义非有限与非正值无效；设备的其他特殊值另加检查。反投影得到 (0.1,0.05,1) m，距离 sqrt(1.0125)≈1.006231 m，Z 仍为 1 m。

<a id="ex2"></a>

## 第 2 题

深度像素 (320,240)，变换到颜色相机的点是 (0.05,0,1)，颜色像素 (350,240)。即使宽高相同，也相差 30 px。

实际对齐要处理两套内参/畸变、外参、遮挡、重投影和时间。只将深度数组 resize 成 RGB 大小，没有完成这条几何关系。

<a id="ex3"></a>

## 第 3 题

按行优先，有效像素 (0,0)、(0,1)、(1,1)，相机点分别 (-0.25,-0.25,1)、(-0.5,0.5,2)、(0.25,0.25,1) m。

```python
def ideal_depth_cloud(depth_m, K):
    depth = np.asarray(depth_m, dtype=float)
    K = require_camera_matrix(K)
    if depth.ndim != 2 or depth.size == 0:
        raise ValueError("nonempty HxW axial-depth map required")
    valid = np.isfinite(depth) & (depth > 0)
    v, u = np.nonzero(valid)
    pixels = np.column_stack((u, v))
    if len(pixels) == 0:
        return np.empty((0, 3)), pixels, valid
    return backproject_ideal(pixels, depth[valid], K), pixels, valid
```

该函数只支持已匹配 K 的理想/去畸变深度图；返回空点云不能被当作有效目标。点云后续处理应保留过滤前后数量和来源。

<a id="ex4"></a>

## 第 4 题

先确认像素属于目标，再检查该区域深度有效性、范围与分布。掩码也可能错，几何/多视角约束同样需要模型和时间一致。

没有有效深度时应返回失败或切换有条件支持的估计来源，并标注来源。滤波只能利用已有信息，不能凭空恢复真实表面。

