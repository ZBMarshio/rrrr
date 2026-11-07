# MATH-01：提示与参考答案

[返回题目](../讲义/MATH-01_矩阵坐标基与形状.md) · [复盘](../练习与复盘记录.md)

<a id="ex1"></a>

## 第1题

R 的两列 [0,1]、[-1,0] 是 B 两根单位轴在 A 中的分量。R*p_B=[0.1,0.2] m，p_A=[0.5,0.3] m；逆向 `p_B=R.T@(p_A-t)`。平移先减掉，再旋转回去。

<a id="ex2"></a>

## 第2题

v_A=[0,1]。方向无位置单位时，加米制 t 还混合了量纲。对于位置差：

`(R*p2+t)-(R*p1+t)=R*(p2-p1)`。

这里坐标系关系静态；运动坐标系下速度变换还涉及坐标系自身运动，后续按具体定义学习。

<a id="ex3"></a>

## 第3题

```python
import numpy as np

def transform_points_2d(points, rotation, translation):
    p, r, t = [np.asarray(x, dtype=np.float64) for x in (points, rotation, translation)]
    if p.ndim != 2 or p.shape[1] != 2 or r.shape != (2,2) or t.shape != (2,):
        raise ValueError("points[N,2], R[2,2], t[2] required")
    if not all(np.isfinite(x).all() for x in (p,r,t)):
        raise ValueError("finite inputs required")
    if not np.allclose(r.T@r, np.eye(2), atol=1e-10, rtol=0) or not np.isclose(np.linalg.det(r),1.,atol=1e-10,rtol=0):
        raise ValueError("proper planar rotation required")
    return p @ r.T + t
```

本函数按二维刚体变换检查 R。一般线性映射应使用别的接口，不能把缩放矩阵作为旋转混入。空点集可返回 [0,2]，这里不把它当实验统计样本。

<a id="ex4"></a>

## 第4题

R 正交且 det=1，逆等于转置并保持长度。S.T=diag(2,1)，inv(S)=diag(0.5,1)，二者不同。坐标轴尺度不同或非正交时，需要处理相应基与度量；本阶段机器人刚体坐标先用正交单位基。
