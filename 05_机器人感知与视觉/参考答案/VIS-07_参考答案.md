# VIS-07：提示与参考答案

[返回题目](../讲义/VIS-07_检测分割与定位接口.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

交集面积 1、并集 7，IoU=1/7≈0.142857。本题连续坐标面积不加 1：

```python
def box_iou(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if any(box.shape != (4,) or not np.isfinite(box).all() or np.any(box[2:] <= box[:2]) for box in (a, b)):
        raise ValueError("finite nondegenerate xyxy boxes required")
    extent = np.maximum(0.0, np.minimum(a[2:], b[2:])-np.maximum(a[:2], b[:2]))
    intersection = float(np.prod(extent))
    union = float(np.prod(a[2:]-a[:2])+np.prod(b[2:]-b[:2])-intersection)
    return intersection/union
```

<a id="ex2"></a>

## 第 2 题

原图框 [100,60,300,260]。只在输出仍属于 letterbox 空间时逆变换：

```python
def undo_letterbox(box, scale, pad_xy, image_wh):
    box = np.asarray(box, dtype=float)
    pad, wh = np.asarray(pad_xy, dtype=float), np.asarray(image_wh, dtype=float)
    if box.shape != (4,) or not np.isfinite(box).all() or np.any(box[2:] <= box[:2]):
        raise ValueError("finite xyxy box required")
    if pad.shape != (2,) or wh.shape != (2,) or not np.isfinite([pad, wh]).all():
        raise ValueError("finite padding and image size required")
    if not np.isfinite(scale) or scale <= 0 or np.any(pad < 0) or np.any(wh <= 0):
        raise ValueError("positive scale/size and nonnegative padding required")
    result = (box-np.tile(pad, 2))/scale
    result = np.clip(result, np.zeros(4), np.tile(wh, 2))
    if np.any(result[2:] <= result[:2]):
        raise ValueError("box outside image after de-padding")
    return result
```

本函数对应等比例缩放加 padding 的明确模型；其他裁剪/非等比变换要另写。输出裁剪后的框也需要保留截断信息用于解释。

<a id="ex3"></a>

## 第 3 题

precision=4/6≈0.6667，recall=4/5=0.8。六个输出包含两个误检，同时还漏了一个；重复预测不增加已匹配真值的计数。

这是一组给定匹配下的算术，不是完整检测 benchmark。真实报告还要声明类别、IoU 阈值、score 阈值、数据集合和无目标图像。

<a id="ex4"></a>

## 第 4 题

最少记录图像 ID/尺寸/处理状态、观测时间与时钟、frame、模型/权重/预处理版本、类别与实例、原图空间框/掩码、score、定位来源、K/dist/外参版本和输出状态。

仅二维框一般不足以确定三维平移和旋转。已知尺寸、易验证的标记物适合建立初始几何基线；替换成自然物体后，重新验证检测、深度来源和姿态约束。此章未运行神经网络推理或下载权重。

