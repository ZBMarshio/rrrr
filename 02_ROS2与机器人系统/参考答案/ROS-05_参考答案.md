# ROS-05：提示与参考答案

[返回题目](../讲义/ROS-05_TF2与坐标查询.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

第一条返回 T_base_camera，用于相机坐标的量转到基座；第二条返回 T_camera_base，是相反方向。

相机坐标目标点使用第一条。lookup 只查询关系，之后还需正确应用变换；点、方向向量、姿态等对象的变换规则也不能混用，方向向量不加平移。

<a id="ex2"></a>

## 第 2 题

```python
import numpy as np

T = np.array([
    [0.0, -1.0, 0.0, 1.0],
    [1.0,  0.0, 0.0, 0.0],
    [0.0,  0.0, 1.0, 0.5],
    [0.0,  0.0, 0.0, 1.0],
])
p_camera = np.array([1.0, 0.0, 2.0, 1.0])
p_base = T @ p_camera
p_back = np.linalg.inv(T) @ p_base
```

得到基座点 `(1,1,2.5)` m，逆变换恢复原点坐标。四元数可为 `(0,0,sqrt(0.5),sqrt(0.5))`；整体取反表示相同旋转。

旋转矩阵需满足 R.T@R≈I、det(R)≈1，末行是 [0,0,0,1]；这些只是数值一致性检查，最终还要核对实际坐标含义。

<a id="ex3"></a>

## 第 3 题

查：原数据 stamp 与当前时钟域是否一致；所请求帧名和 TF 路径；动态变换缓存覆盖；发布频率/延迟；是否使用 sim time；回调是否阻塞 Listener。

固定相机与固定基座之间，安装不变的静态外参可跨时刻使用。但基座在移动、相机装在手上、或目标要转到运动末端坐标时，路径上可能仍有动态边。

用 t=10.2 的动态关系解释 t=10.0 的点，会引入与运动相关的误差。不能因为查询成功就把它当作修复。

<a id="ex4"></a>

## 第 4 题

在已创建 Buffer 和 TransformListener 的节点中，回调局部可为：

```python
from rclpy.time import Time
from tf2_ros import TransformException

def on_point(self, msg):
    stamp = Time.from_msg(msg.header.stamp)
    try:
        transform = self.tf_buffer.lookup_transform(
            "base_link", msg.header.frame_id, stamp,
        )
    except TransformException as exc:
        self.get_logger().warning(f"point transform unavailable: {exc}")
        return
    self.handle_point_with_transform(msg, transform)
```

最后一行是你实现的点变换与记录接口，不是 TF2 内置函数。此片段默认不阻塞等待；根据任务选择有界缓存/重试，保留原时间，不能静默复用上一帧结果。

离线插入已知 TransformStamped 时，用 header.frame_id="base_link"、child_frame_id="camera_optical"，平移/四元数按第 2 题，查询并应用到已知点。只做离线 Buffer 通过时，Listener 网络接收仍未验证。

