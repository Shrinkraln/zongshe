import json
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener, TransformException
from nav_msgs.msg import Odometry
from sensor_msgs.msg import BatteryState


class RobotStateMonitor(Node):
    def __init__(self):
        super().__init__('robot_state_monitor')

        # TF Buffer & Listener Setup（手册 P11）
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Data Storage
        self.robot_state = {}

        # 订阅里程计数据（手册 P12）
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # 订阅电池状态（手册 P12）
        self.create_subscription(BatteryState, '/battery_state', self.battery_callback, 10)

        # 定时器：每秒更新状态
        self.create_timer(1.0, self.timer_callback)

        self.get_logger().info('Robot State Monitor started')

    def odom_callback(self, msg):
        self.robot_state['pose'] = {
            'x': round(msg.pose.pose.position.x, 3),
            'y': round(msg.pose.pose.position.y, 3)
        }
        self.robot_state['velocity'] = {
            'linear': round(msg.twist.twist.linear.x, 3),
            'angular': round(msg.twist.twist.angular.z, 3)
        }

    def battery_callback(self, msg):
        self.robot_state['battery'] = round(msg.percentage, 1)

    def validate_transform(self, t):
        """数据验证函数（手册 P19）：检查坐标是否在合理范围内"""
        x = t.transform.translation.x
        y = t.transform.translation.y
        z = t.transform.translation.z
        if abs(x) > 100 or abs(y) > 100 or abs(z) > 0.5:
            self.get_logger().warn(f'Transform out of range: x={x}, y={y}, z={z}')
            return False
        return True

    def timer_callback(self):
        # TF 一致性检查（手册 P13）
        # 注意：用 odom→base_link，因为当前没有启动 Nav2 所以没有 map frame
        try:
            t = self.tf_buffer.lookup_transform(
                'odom', 'base_link',
                Time())

            if self.validate_transform(t):
                self.robot_state['tf_odom_to_base'] = {
                    'x': round(t.transform.translation.x, 3),
                    'y': round(t.transform.translation.y, 3),
                    'z': round(t.transform.translation.z, 3)
                }
        except TransformException as ex:
            self.get_logger().debug(f'Could not transform: {ex}')

        # 查询 base_link→rplidar_link（雷达相对位置）
        try:
            t2 = self.tf_buffer.lookup_transform(
                'base_link', 'rplidar_link',
                Time())
            self.robot_state['tf_base_to_lidar'] = {
                'x': round(t2.transform.translation.x, 3),
                'y': round(t2.transform.translation.y, 3),
                'z': round(t2.transform.translation.z, 3)
            }
        except TransformException as ex:
            self.get_logger().debug(f'Lidar transform: {ex}')

        # JSON 序列化输出（手册 P14：为云平台做准备）
        if self.robot_state:
            state_json = json.dumps(self.robot_state, indent=2)
            self.get_logger().info(f'State Update: {state_json}')


def main(args=None):
    rclpy.init(args=args)
    node = RobotStateMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()