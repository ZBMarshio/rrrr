# VIS-03：提示与参考答案

[返回题目](../讲义/VIS-03_内参标定与独立验证.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

前两点 (0,0,0)、(0.025,0,0)，第 9 点 (0.2,0,0)，第 10 点 (0,0.025,0)，最后 (0.2,0.125,0) m。角点跨度 0.2×0.125 m，整个实物板通常更大。

```python
def board_points(pattern=(9, 6), square_m=0.025):
    if len(pattern) != 2 or any(not isinstance(v, int) or v < 2 for v in pattern):
        raise ValueError("two integer inner-corner counts >=2 required")
    if not np.isfinite(square_m) or square_m <= 0:
        raise ValueError("positive square length in meters required")
    cols, rows = pattern
    xy = np.array([(x, y) for y in range(rows) for x in range(cols)], dtype=float)
    return np.column_stack((xy*square_m, np.zeros(len(xy))))
```

物体点整体放大 1000 倍时，估计平移也可放大 1000 倍而保持投影；重投影检查不自动发现这种单位错误。

<a id="ex2"></a>

## 第 2 题

从自己的角点检测/数据记录开始。下面只负责标准针孔模型的数值输入与调用，不含完整采集程序：

```python
def calibrate_from_corners(object_sets, pixel_sets, image_wh, flags=0):
    if len(image_wh) != 2 or any(not isinstance(v, int) or v <= 0 for v in image_wh):
        raise ValueError("positive integer (width,height) required")
    if len(object_sets) != len(pixel_sets) or len(object_sets) < 3:
        raise ValueError("at least three paired views required; diversity checked separately")
    objects, images = [], []
    for obj, pix in zip(object_sets, pixel_sets):
        obj, pix = np.asarray(obj, dtype=float), np.asarray(pix, dtype=float)
        if obj.ndim != 2 or obj.shape[1] != 3 or len(obj) < 6 or pix.shape != (len(obj), 2):
            raise ValueError("each view requires paired Nx3/Nx2 arrays")
        if not np.isfinite(obj).all() or not np.isfinite(pix).all():
            raise ValueError("finite calibration points required")
        if np.any(pix < 0) or np.any(pix >= np.asarray(image_wh)):
            raise ValueError("observed corners must lie within the declared image")
        objects.append(obj.astype(np.float32))
        images.append(pix.astype(np.float32).reshape(-1, 1, 2))
    rms, K, dist, rvecs, tvecs = cv.calibrateCamera(
        objects, images, tuple(image_wh), None, None, flags=flags,
    )
    require_camera_matrix(K)
    if not np.isfinite(rms) or not np.isfinite(dist).all():
        raise RuntimeError("non-finite calibration result")
    return {"rms_px": float(rms), "K": K, "dist": dist.reshape(-1),
            "rvecs": rvecs, "tvecs": tvecs, "image_wh": tuple(image_wh), "flags": flags}
```

至少三组输入只是本函数的形式检查，不能证明可辨识。输入坏姿态、错误模型或过多自由参数，仍可能返回数值结果。合成对照中固定 k3=0 时显式用 CALIB_FIX_K3，不能把这一选择默认迁移到真实镜头。

<a id="ex3"></a>

## 第 3 题

两点 RMS=sqrt((1²+3²)/2)=sqrt(5)≈2.236068 px；norm(errors)/2≈1.581139 px，二者不同。

```python
def reprojection_rmse(observed, predicted):
    observed, predicted = np.asarray(observed, dtype=float), np.asarray(predicted, dtype=float)
    if observed.ndim != 2 or observed.shape[1] != 2 or len(observed) == 0 or predicted.shape != observed.shape:
        raise ValueError("matching nonempty Nx2 arrays required")
    if not np.isfinite(observed).all() or not np.isfinite(predicted).all():
        raise ValueError("finite image points required")
    return float(np.sqrt(np.mean(np.sum((observed-predicted)**2, axis=1))))

def fit_view_pose(object_points, pixels, K, dist):
    obj, pix = np.asarray(object_points, dtype=float), np.asarray(pixels, dtype=float)
    K, dist = require_camera_matrix(K), np.asarray(dist, dtype=float).reshape(-1)
    if obj.ndim != 2 or obj.shape[1] != 3 or len(obj) < 4 or pix.shape != (len(obj), 2):
        raise ValueError("paired Nx3/Nx2 points required")
    if not np.isfinite(obj).all() or not np.isfinite(pix).all() or dist.size != 5 or not np.isfinite(dist).all():
        raise ValueError("finite points and five standard distortion coefficients required")
    rank = np.linalg.matrix_rank(obj-obj.mean(axis=0))
    if rank < 2 or (rank == 3 and len(obj) < 6):
        raise ValueError("non-collinear planar points or >=6 nonplanar points required")
    ok, rvec, tvec = cv.solvePnP(obj, pix, K, dist, flags=cv.SOLVEPNP_ITERATIVE)
    if not ok or not np.isfinite(rvec).all() or not np.isfinite(tvec).all():
        raise RuntimeError("PnP did not produce a finite hypothesis")
    R, _ = cv.Rodrigues(rvec)
    camera_points = obj @ R.T+tvec.reshape(3)
    if np.any(camera_points[:, 2] <= 1e-8):
        raise RuntimeError("PnP hypothesis has nonpositive depth")
    projected, _ = cv.projectPoints(obj, rvec, tvec, K, dist)
    return rvec.reshape(3), tvec.reshape(3), reprojection_rmse(pix, projected.reshape(-1, 2))
```

留出时向 fit_view_pose 传入冻结的 K/dist。该函数保留一个 ITERATIVE 解，不处理全部平面位姿歧义，详见 VIS-04。

<a id="ex4"></a>

## 第 4 题

参数文件应至少包括相机/镜头标识、image_wh、是否原图/校正图、畸变模型、K/dist、新 K/ROI（若使用）、板规格/单位、数据 ID、标定版本与误差定义。

纯图像坐标变换可按 VIS-01 映射更新 K；对焦、光学设置变化或更换相机需重新评估/标定。剔除样本需要具体原因与记录；真实空间精度留给独立基准验证。

