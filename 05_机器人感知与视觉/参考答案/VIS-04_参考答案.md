# VIS-04：提示与参考答案

[返回题目](../讲义/VIS-04_标记物与PnP位姿.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

目标原点在相机的 (0,0,0.8) m；相机在目标的 (0,0,-0.8) m。目标点变成 (0.1,0,0.8)，本章 K 下像素为 (395,240)。

<a id="ex2"></a>

## 第 2 题

复用 fit_view_pose 得到 rvec/tvec，再组装：

```python
def pose_matrix(rvec, tvec):
    rvec, tvec = np.asarray(rvec, dtype=float), np.asarray(tvec, dtype=float)
    if rvec.size != 3 or tvec.size != 3 or not np.isfinite(rvec).all() or not np.isfinite(tvec).all():
        raise ValueError("finite three-element rotation and translation vectors required")
    R, _ = cv.Rodrigues(rvec.reshape(3))
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, tvec.reshape(3)
    return T

def detect_aruco_gray(gray, dictionary_id=None):
    if not isinstance(gray, np.ndarray) or gray.ndim != 2 or gray.size == 0 or gray.dtype != np.uint8:
        raise ValueError("nonempty uint8 grayscale image required")
    if not hasattr(cv, "aruco"):
        raise RuntimeError("aruco module unavailable in this environment")
    dictionary_id = cv.aruco.DICT_4X4_50 if dictionary_id is None else dictionary_id
    dictionary = cv.aruco.getPredefinedDictionary(dictionary_id)
    if hasattr(cv.aruco, "ArucoDetector"):
        parameters = cv.aruco.DetectorParameters()
        return cv.aruco.ArucoDetector(dictionary, parameters).detectMarkers(gray)
    parameters = cv.aruco.DetectorParameters_create()
    return cv.aruco.detectMarkers(gray, dictionary, parameters=parameters)
```

本机实际核对的是 4.6 的旧分支；新版分支使用时按对应文档核对。返回的 corners/ids/rejected 需要逐个配对解释；空检测不能继续走 PnP。

若按 IPPE_SQUARE 的物体坐标约定，四点为：

```python
def square_marker_points(length_m):
    if not np.isfinite(length_m) or length_m <= 0:
        raise ValueError("positive physical marker side required")
    h = length_m/2
    return np.array([[-h, h, 0], [h, h, 0], [h, -h, 0], [-h, -h, 0]], dtype=float)
```

点序应和所用标记检测器的角点身份对应。画轴可用 cv.drawFrameAxes；先说明标记坐标轴朝向，不要求它的 +y 与相机 +y 同向。

<a id="ex3"></a>

## 第 3 题

理想相同点序与模型下，物体点与平移一起乘 2，投影不变；因此可得到相同旋转、约两倍平移且重投影仍小。尺度必须由正确的实物几何或额外观测给出。

变到基座还需 T_base_camera：`T_base_target=T_base_camera @ T_camera_target`。原始 tvec 只是目标原点的相机坐标。

<a id="ex4"></a>

## 第 4 题

可分别输出 no_detection、insufficient_correspondence、correspondence_inconsistent、ambiguous_pose、stale_observation 等解释清楚的状态。错点序有时仍可拟合出低残差的另一姿态，因此也要检查物体帧定义、轴图和跨帧固定关系。

预测/沿用结果需要原始观测时间、估计时间、来源与有效期；不能刷新时间戳把旧结果伪装成新测量。拒绝进入规划与底层实际停止仍按第二章/第四章接口分别处理。

