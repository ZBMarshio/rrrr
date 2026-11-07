# VIS-02：提示与参考答案

[返回题目](../讲义/VIS-02_相机模型与投影反投影.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

像素 (380,271)。同时缩放 X/Y/Z 后比值相同，像素不变；单目单点无法单靠它确定沿射线的尺度。

<a id="ex2"></a>

## 第 2 题

以下仅支持无 skew 的标准针孔 K 与无畸变坐标，依赖 NumPy：

```python
def require_camera_matrix(K):
    K = np.asarray(K, dtype=float)
    if K.shape != (3, 3) or not np.isfinite(K).all():
        raise ValueError("finite 3x3 camera matrix required")
    if min(K[0, 0], K[1, 1]) <= 0:
        raise ValueError("positive focal lengths required")
    expected = np.array([[K[0, 0], 0, K[0, 2]], [0, K[1, 1], K[1, 2]], [0, 0, 1]])
    if not np.allclose(K, expected, atol=1e-12, rtol=0):
        raise ValueError("standard zero-skew pinhole intrinsics required")
    return K

def project_ideal(points_camera, K, min_z=1e-8):
    points = np.asarray(points_camera, dtype=float)
    K = require_camera_matrix(K)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) == 0 or not np.isfinite(points).all():
        raise ValueError("nonempty finite Nx3 points required")
    if not np.isfinite(min_z) or min_z <= 0 or np.any(points[:, 2] <= min_z):
        raise ValueError("positive depth above threshold required")
    normalized = points[:, :2]/points[:, 2, None]
    return normalized*np.array([K[0, 0], K[1, 1]])+K[:2, 2]

def backproject_ideal(pixels, z, K):
    pixels, z = np.asarray(pixels, dtype=float), np.asarray(z, dtype=float)
    K = require_camera_matrix(K)
    if pixels.ndim != 2 or pixels.shape[1] != 2 or len(pixels) == 0 or z.shape != (len(pixels),):
        raise ValueError("Nx2 pixels and matching N depths required")
    if not np.isfinite(pixels).all() or not np.isfinite(z).all() or np.any(z <= 0):
        raise ValueError("finite pixels and positive Z required")
    xy = (pixels-K[:2, 2])/np.array([K[0, 0], K[1, 1]])*z[:, None]
    return np.column_stack((xy, z))
```

图像内检查另用 0≤u<width、0≤v<height。这个函数没有相机视场或遮挡判断。

<a id="ex3"></a>

## 第 3 题

相机点 (0.1,0,1) m，理想像素 (380,240)。目标原点所在平面 z=0 不代表它在相机光心平面；直接代入是漏了外参。

T_target_camera 复用第三章 rigid_inverse，平移为 (0,0,-1) m。不要把 tvec 原样命名成“相机位置”。

<a id="ex4"></a>

## 第 4 题

局部函数明确输入原始像素，输出相机点；dist 应与相机模型匹配：

```python
def backproject_distorted(pixels, z, K, dist):
    pixels, z = np.asarray(pixels, dtype=float), np.asarray(z, dtype=float)
    K = require_camera_matrix(K)
    dist = np.asarray(dist, dtype=float).reshape(-1)
    if pixels.ndim != 2 or pixels.shape[1] != 2 or len(pixels) == 0 or z.shape != (len(pixels),):
        raise ValueError("Nx2 pixels and matching N Z required")
    if not np.isfinite(pixels).all() or not np.isfinite(z).all() or np.any(z <= 0):
        raise ValueError("finite pixels and positive depth required")
    if dist.size != 5 or not np.isfinite(dist).all():
        raise ValueError("this exercise requires five distortion coefficients")
    normalized = cv.undistortPoints(pixels.reshape(-1, 1, 2), K, dist).reshape(-1, 2)
    return np.column_stack((normalized*z[:, None], z))
```

undistortPoints 是数值反解，往返误差不必精确为零；在有限视场与合理系数下选容差核对。很强畸变、模型错配或错误内参都需要重新检查。

