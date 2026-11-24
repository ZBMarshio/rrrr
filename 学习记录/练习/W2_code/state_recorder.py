import csv
from pathlib import Path

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState

from positions_in_order import positions_in_order


class StateRecorder(Node):
    def __init__(self):
        super().__init__("state_recorder")
        self.expected_names = ["joint_1", "joint_2"]
        self.csv_path = Path(__file__).parent / "joint_states_log.csv"
        self.csv_file = self.csv_path.open("w", encoding="utf-8", newline="")
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(["stamp_ns", "received_ns", "joint_1_rad", "joint_2_rad"])

        self.sub = self.create_subscription(
            JointState, "joint_states", self.on_state, 10
        )
        self.get_logger().info(f"recording to {self.csv_path}")

    def on_state(self, msg):
        received_ns = self.get_clock().now().nanoseconds
        try:
            positions = positions_in_order(msg, self.expected_names)
        except ValueError as exc:
            self.get_logger().warning(f"rejected state: {exc}")
            return
        stamp_ns = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
        self.writer.writerow([stamp_ns, received_ns, *positions])
        self.csv_file.flush()

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = StateRecorder()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
