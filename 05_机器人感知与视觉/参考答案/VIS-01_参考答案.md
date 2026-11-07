# VIS-01：提示与参考答案

[返回题目](../讲义/VIS-01_图像像素与OpenCV.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

`image[50,100]=[0,0,255]` 表示该像素为红色。显示为 RGB 时可用 cv.cvtColor(image,cv.COLOR_BGR2RGB)；直接写 image[100,50] 会改到 (u=50,v=100)。

<a id="ex2"></a>

## 第 2 题

这是本练习明确的输入契约，不是说 OpenCV 不能处理其他图像：

```python
import cv2 as cv
import numpy as np

def require_bgr8(image):
    if not isinstance(image, np.ndarray):
        raise ValueError("decoded image array required; check imread result")
    if image.ndim != 3 or image.shape[2] != 3 or min(image.shape[:2]) == 0:
        raise ValueError("nonempty HxWx3 image required")
    if image.dtype != np.uint8:
        raise ValueError("uint8 BGR contract required")
    return image
```

None 应在访问 shape、cvtColor 或进入检测器之前发现。灰度/浮点数据若确有需求，应设计对应契约与转换，而不是静默猜测输入。

<a id="ex3"></a>

## 第 3 题

切片通常共享存储，copy 后独立。HWC→CHW 用 `image.transpose(2,0,1)`，它改变轴顺序；reshape 不表达同一含义。

uint8 算术可能溢出/回绕。可以先转换为适合计算的 float32 或更宽整数，明确范围后再处理。像素数值归一化与通道转置是两件事。

<a id="ex4"></a>

## 第 4 题

新 K 为 `[[300,0,140],[0,310,110],[0,0,1]]`。理想投影原来 (380,271)，题设映射后为 (170,125.5)。

```python
def pixel_affine_intrinsics(K, sx, sy, u0=0.0, v0=0.0):
    K = np.asarray(K, dtype=float)
    if K.shape != (3, 3) or not np.isfinite(K).all():
        raise ValueError("finite 3x3 intrinsics required")
    if not np.isfinite([sx, sy, u0, v0]).all() or min(sx, sy) <= 0:
        raise ValueError("positive scales and finite crop offsets required")
    A = np.array([[sx, 0, -sx*u0], [0, sy, -sy*v0], [0, 0, 1]])
    return A @ K
```

本函数只对应题设映射。去畸变/校正可产生不同的新 K；图像已经移除畸变时，PnP 不再重复使用原畸变。ROI 裁剪后主点也要对应最终像素坐标。

