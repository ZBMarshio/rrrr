import math

from sensor_msgs.msg import JointState

def positions_in_order(msg, expected_names):
    """校验一条 JointState，并按 expected_names 的顺序返回新的 float 列表。"""
    names = list(msg.name)
    if not names or len(names) != len(set(names)):
        raise ValueError("empty or duplicate joint names")
    if len(msg.position) != len(names):
        raise ValueError("position/name length mismatch")
    if len(expected_names) != len(set(expected_names)):
        raise ValueError("duplicate expected names")

    for field in ("position", "velocity", "effort"):
        values = list(getattr(msg, field))
        if values and len(values) != len(names):
            raise ValueError(f"{field} length mismatch")
        if not all(math.isfinite(float(v)) for v in values):
            raise ValueError(f"non-finite {field}")

    by_name = dict(zip(names, msg.position))
    missing = set(expected_names) - by_name.keys()
    if missing:
        raise ValueError(f"missing joints: {sorted(missing)}")

    return [float(by_name[name]) for name in expected_names]


def expect_value_error(msg, expected_names):
    try:
        positions_in_order(msg, expected_names)
    except ValueError as exc:
        print(f"  rejected: {exc}")
    else:
        raise AssertionError("expected ValueError")


if __name__ == "__main__":
    msg = JointState()
    msg.name = ["joint_2", "joint_1"]
    msg.position = [-0.2, 0.1]
    print(positions_in_order(msg, ["joint_1", "joint_2"]))

    expect_value_error(msg, ["joint_1", "joint_3"])  # 缺关节

    dup = JointState()  # 重复名字
    dup.name = ["joint_1", "joint_1"]
    dup.position = [0.1, 0.2]
    expect_value_error(dup, ["joint_1"])

    short = JointState()  # 长度不一致
    short.name = ["joint_1", "joint_2"]
    short.position = [0.1]
    expect_value_error(short, ["joint_1"])

    nan = JointState()  # NaN
    nan.name = ["joint_1"]
    nan.position = [float("nan")]
    expect_value_error(nan, ["joint_1"])

    empty = JointState()  # 空 velocity 允许通过
    empty.name = ["joint_1", "joint_2"]
    empty.position = [0.1, -0.2]
    assert positions_in_order(empty, ["joint_2"]) == [-0.2]
    print("all tests passed")
