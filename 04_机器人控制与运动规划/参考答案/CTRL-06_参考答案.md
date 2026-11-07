# CTRL-06：提示与参考答案

[返回题目](../讲义/CTRL-06_碰撞与运动规划.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

中点两连杆是 [0,0]→[0.3,0]→[0.5,0] m；障碍中心在第二条线段上，发生碰撞。TCP 与圆心仍相距 0.1 m，所以只检查 TCP 会漏掉它。

<a id="ex2"></a>

## 第 2 题

几何核对片段，依赖 NumPy 与第三章 fk_xy。碰到膨胀后的边界也算无效：

```python
def point_segment_distance(point, a, b):
    point, a, b = [np.asarray(v, dtype=float) for v in (point, a, b)]
    if any(v.shape != (2,) or not np.isfinite(v).all() for v in (point, a, b)):
        raise ValueError("finite 2D points required")
    direction = b-a
    length2 = float(direction @ direction)
    fraction = 0.0 if length2 == 0 else float(np.clip((point-a) @ direction/length2, 0, 1))
    return float(np.linalg.norm(point-(a+fraction*direction)))

def configuration_free(q, *, center=(0.4, 0.0), radius=0.04, padding=0.015,
                       lower=(-1.6, -2.4), upper=(1.6, 2.4)):
    q, center, lower, upper = [np.asarray(v, dtype=float) for v in (q, center, lower, upper)]
    if any(v.shape != (2,) or not np.isfinite(v).all() for v in (q, center, lower, upper)):
        raise ValueError("finite 2R geometry required")
    if not np.isfinite([radius, padding]).all() or min(radius, padding) < 0 or np.any(lower > upper):
        raise ValueError("invalid obstacle or bounds")
    if np.any(q < lower) or np.any(q > upper):
        return False
    base = np.zeros(2)
    elbow = 0.3*np.array([np.cos(q[0]), np.sin(q[0])])
    tcp = fk_xy(q)
    minimum = min(point_segment_distance(center, base, elbow),
                  point_segment_distance(center, elbow, tcp))
    return minimum > radius+padding

def edge_free(qa, qb, resolution=0.02):
    qa, qb = np.asarray(qa, dtype=float), np.asarray(qb, dtype=float)
    if qa.shape != (2,) or qb.shape != (2,) or not np.isfinite([qa, qb]).all():
        raise ValueError("finite 2R endpoints required")
    if not np.isfinite(resolution) or resolution <= 0:
        raise ValueError("positive joint-space resolution required")
    intervals = max(1, int(np.ceil(np.max(np.abs(qb-qa))/resolution)))
    return all(configuration_free(qa+s*(qb-qa)) for s in np.linspace(0, 1, intervals+1))
```

resolution 表示相邻采样的最大单关节变化/rad。这不是工作空间距离，也不是连续碰撞证明。函数只支持本题固定模型，正式系统用框架支持的模型和检查器。

<a id="ex3"></a>

## 第 3 题

给定绕行候选在本题离散检查下各边有效；中间 q2=2.4 rad 正好到达本题上界，没有额外关节余量。它用于展示检查机制，不是可直接移植的实机方案。

路点折角还不是平滑时间轨迹。若插值改变几何路径，必须检查改变后的路径；时间安排也要满足速度、加速度和执行接口约束。

<a id="ex4"></a>

## 第 4 题

验收应包括场景可复建、请求与结果成对保存、失败有证据。三类请求结果取决于你的模型与限制，不预写某个错误码。

若碰撞请求意外成功，先核对障碍是否真的进入规划场景、坐标和尺寸是否正确、是否被允许碰撞配置排除。不能为了“规划成功”直接关闭相关碰撞检查。

本章仅核对了小场景数值检查，没有运行 MoveIt 规划演示。软件包存在、场景可视化、实际规划和硬件执行是不同验证层次。

