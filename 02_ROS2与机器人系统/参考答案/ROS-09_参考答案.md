# ROS-09：提示与参考答案

[返回题目](../讲义/ROS-09_传感器消息与驱动边界.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

像素排列为：第一行红、绿；第二行蓝、白。每行最后两字节是本题的填充。

```python
import numpy as np

def decode_rgb8(msg):
    if msg.encoding != "rgb8":
        raise ValueError("this exercise only supports rgb8")
    h, w, step = msg.height, msg.width, msg.step
    if h <= 0 or w <= 0 or step < w * 3:
        raise ValueError("invalid image dimensions or step")
    raw = bytes(msg.data)
    if len(raw) != h * step:
        raise ValueError("image data length mismatch")
    rows = np.frombuffer(raw, dtype=np.uint8).reshape(h, step)
    return rows[:, :w * 3].reshape(h, w, 3).copy()
```

copy 让结果独立。这里只处理 8 位 RGB，不能将该实现直接用于单通道深度、Bayer、压缩图像或任意端序格式。发布合成消息时还应按本章约定填时间和 frame_id；本题仅做离线布局检查。

<a id="ex2"></a>

## 第 2 题

纯缩放比例为 0.5，fx/fy/cx/cy 相应乘 0.5，并更新分辨率元信息。更精确的像素中心约定按实际图像变换处理。

裁剪还改变主点偏移；去畸变/校正图可能对应新的内参/投影矩阵。原始图的 k 与校正后图的 p 或新相机矩阵不能仅因尺寸相同而互换，检查处理管线输出。

<a id="ex3"></a>

## 第 3 题

有效值为 1.0 m 与 2.0 m，中间为无效。可以用有效掩码或 NaN 表示，空间算法显式跳过/拒绝；不当作目标位于相机原点。

核对深度与 RGB 是否在同一像素坐标、使用哪一套内参、是否已对齐/去畸变、采样时间差与坐标关系。以上毫米规则来自本题设备说明，不从 uint16 数据类型本身推断。

<a id="ex4"></a>

## 第 4 题

提示：保留跨 chunk 的半帧；找不到完整帧头时，末尾 AA 仍可能是下一个头的第一字节。

```python
import math

def decode_angle_chunks(chunks):
    buffer = bytearray()
    result = []
    for chunk in chunks:
        buffer.extend(chunk)
        while True:
            start = buffer.find(b"\xAA\x55")
            if start < 0:
                buffer[:] = b"\xAA" if buffer[-1:] == b"\xAA" else b""
                break
            if start:
                del buffer[:start]
            if len(buffer) < 5:
                break
            frame = bytes(buffer[:5])
            if (sum(frame[:4]) & 0xFF) != frame[4]:
                del buffer[0]
                continue
            raw = int.from_bytes(frame[2:4], "little", signed=True)
            result.append(math.radians(raw * 0.01))
            del buffer[:5]
    return result
```

E8 03 解码为 +1000，18 FC 为 -1000，分别是 ±10°，约 ±0.174532925 rad。

真实驱动还应记录丢帧/校验失败、残留半帧、状态与采样时间，并处理连接与超时。这题只验证固定长度教学协议的分段解析，不覆盖真实设备通信的全部问题。

