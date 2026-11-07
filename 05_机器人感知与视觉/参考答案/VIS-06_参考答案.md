# VIS-06：提示与参考答案

[返回题目](../讲义/VIS-06_手眼标定与坐标闭合.md) · [复盘记录](../练习与复盘记录.md)

本节依赖第三章 rigid_inverse、is_rigid_transform，以及 VIS-04 的 pose_matrix；SciPy 的旋转表示在第三章已使用。

<a id="ex1"></a>

## 第 1 题

| 布局 | 传入第一组 | 传入第二组 | 输出解释 |
|---|---|---|---|
| 相机固定外部、板在工具上 | G_i⁻¹=T_tool_base_i | C_i=T_camera_board_i | Y=T_base_camera |
| 相机在工具上、板固定外部 | G_i=T_base_tool_i | C_i=T_camera_board_i | T_tool_camera |

每个等式要由实际安装关系支持。把布局换掉后，直接照用同一矩阵名会破坏物理含义。

<a id="ex2"></a>

## 第 2 题

无噪声生成公式 G_i=Y C_i X⁻¹。只把生成后的 G_i/C_i 作为求解输入；Y/X 真值留在评分侧。

下面是局部眼在手外求解器。它做最低输入检查及旋转多样性粗筛，不代替真实采集与完整误差评估：

```python
from scipy.spatial.transform import Rotation

def require_pose(T):
    T = np.asarray(T, dtype=float)
    if not is_rigid_transform(T):
        raise ValueError("finite proper 4x4 rigid transform required")
    return T

def rotation_excitation(poses):
    poses = [require_pose(T) for T in poses]
    if len(poses) < 3:
        raise ValueError("at least three poses required")
    R0 = poses[0][:3, :3]
    vectors = np.asarray([
        cv.Rodrigues(R0.T @ T[:3, :3])[0].reshape(3) for T in poses[1:]
    ])
    return np.linalg.svd(vectors, compute_uv=False)

def estimate_eye_to_hand(base_tool, camera_board, min_excitation=1e-5):
    G = [require_pose(T) for T in base_tool]
    C = [require_pose(T) for T in camera_board]
    if len(G) != len(C) or len(G) < 3:
        raise ValueError("at least three paired poses required")
    if not np.isfinite(min_excitation) or min_excitation <= 0:
        raise ValueError("positive excitation threshold required")
    singular = rotation_excitation(G)
    if len(singular) < 2 or singular[1] <= min_excitation:
        raise ValueError("rotation diversity screen failed")
    inverse_G = [rigid_inverse(T) for T in G]
    R, t = cv.calibrateHandEye(
        [T[:3, :3] for T in inverse_G], [T[:3, 3].reshape(3, 1) for T in inverse_G],
        [T[:3, :3] for T in C], [T[:3, 3].reshape(3, 1) for T in C],
        method=cv.CALIB_HAND_EYE_PARK,
    )
    Y = np.eye(4)
    Y[:3, :3], Y[:3, 3] = R, np.asarray(t).reshape(3)
    return require_pose(Y)
```

1e-5 是该合成练习的粗筛阈值，不是通用采集合格线。通过粗筛仍可能病态、有错配或模型误差，必须继续验证。

<a id="ex3"></a>

## 第 3 题

只有平移时旋转激励接近零；同轴旋转只有一条主要方向，本粗筛会拒绝。反向或错配时可能仍返回一个有限矩阵，但留出闭合/合成真值误差会暴露问题。

若板也固定在外部，T_tool_board 不再固定于运动工具，Y C_i=G_i X 的 X 常量假设不成立。先检查物理安装，不能靠多拍几张修复错误方程。

<a id="ex4"></a>

## 第 4 题

在标定集计算 `X_i=G_i⁻¹ Y_hat C_i`，求一个代表 X_hat，然后冻结。旋转不能逐元素随便平均；本例用 SciPy 的旋转均值：

```python
def mean_pose(poses):
    poses = [require_pose(T) for T in poses]
    if not poses:
        raise ValueError("nonempty pose list required")
    result = np.eye(4)
    result[:3, :3] = Rotation.from_matrix(np.asarray([T[:3, :3] for T in poses])).mean().as_matrix()
    result[:3, 3] = np.mean([T[:3, 3] for T in poses], axis=0)
    return result

def pose_error(reference, estimate):
    reference, estimate = require_pose(reference), require_pose(estimate)
    translation = np.linalg.norm(estimate[:3, 3]-reference[:3, 3])
    relative_rotation = estimate[:3, :3] @ reference[:3, :3].T
    return {"translation_m": float(translation),
            "rotation_rad": float(Rotation.from_matrix(relative_rotation).magnitude())}
```

对留出样本计算 pose_error(Y_hat @ C_i,G_i @ X_hat)，旋转用 rad2deg 展示。闭合小仍不能完全排除共享的系统误差；真实精度还需独立基准。

进入规划用 `T_base_target=Y_hat @ T_camera_target`，再接 `T_target_goal` 得到 T_base_goal。目标、工具/TCP、接近方向与碰撞约束分别定义；不要用已知真值替换估计输出。

