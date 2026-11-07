# SIM-06：提示与参考答案

[返回题目](../讲义/SIM-06_模型与接口适配.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

结果 [-0.4,0.2] rad。以下函数要求来源/目标集合完全相同；更大 JointState 消息应先按明确的规划组筛选，额外名字不能静默忽略：

```python
def map_named_values(source_names, source_values, target_names):
    source, target = list(source_names), list(target_names)
    if not source or not target or any(not isinstance(n, str) or not n for n in source+target):
        raise ValueError("nonempty joint names required")
    if len(set(source)) != len(source) or len(set(target)) != len(target) or set(source) != set(target):
        raise ValueError("unique matching joint-name sets required")
    values = np.asarray(source_values, dtype=float)
    if values.shape != (len(source),) or not np.isfinite(values).all():
        raise ValueError("finite named values required")
    lookup = dict(zip(source, values))
    return np.asarray([lookup[n] for n in target], dtype=float)
```

<a id="ex2"></a>

## 第 2 题

q_device=[-0.1,-0.6] rad，反算回原值：

```python
def affine_joint_map(values, signs, offsets_rad, *, inverse=False):
    q, s, b = [np.asarray(v, dtype=float) for v in (values, signs, offsets_rad)]
    if q.ndim != 1 or q.size == 0 or s.shape != q.shape or b.shape != q.shape:
        raise ValueError("matching nonempty joint vectors required")
    if any(not np.isfinite(v).all() for v in (q, s, b)) or not np.all(np.isin(s, [-1, 1])):
        raise ValueError("finite values and signs +/-1 required")
    return s*(q-b) if inverse else s*q+b
```

速度在同一固定映射下只乘 s，不加位置偏置。原始度先转 rad 再应用以 rad 声明的偏置；力矩不能未经传动/功率检查照搬位置变换。

<a id="ex3"></a>

## 第 3 题

xyzw=(0,0,√0.5,√0.5)→wxyz=(√0.5,0,0,√0.5)。只做顺序转换的局部函数：

```python
def reorder_quaternion(q, source="xyzw", target="wxyz"):
    q = np.asarray(q, dtype=float)
    if source not in ("xyzw", "wxyz") or target not in ("xyzw", "wxyz"):
        raise ValueError("supported quaternion order required")
    if q.shape != (4,) or not np.isfinite(q).all() or not np.isclose(np.linalg.norm(q), 1, atol=1e-6, rtol=0):
        raise ValueError("finite unit quaternion required")
    return q[[source.index(axis) for axis in target]].copy()
```

本函数拒绝无效输入，不自动修复。工具坐标轴改变或基座变换需要完整坐标关系，不能只重排四个数。

<a id="ex4"></a>

## 第 4 题

复用第一章文件/日志，第二章轨迹验证，以及第五章 frame/标定/时间检查。至少保存参考与实际来源，不把原始真值替换成“估计目标”。

运行到哪层就按哪层报告：文件可解析、框架接收、物理状态跟踪和真机任务结果分别验证。

