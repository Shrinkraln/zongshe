#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_inject.py —— 第4课失效注入①（动态障碍）课程工具骨架：向激光扫描注入一个虚拟障碍回波，输出 /scan_injected。
仅用于孪生侧，不得接入实车 /scan 链路。
用法：python3 scan_inject.py --bearing 0 --dist 1.5 --width 0.4   # 在机器人坐标系中 bearing(°) 方向、dist(m) 处放置宽 width(m) 的障碍
Nav2 侧把 scan 话题重映射为 /scan_injected。注入方式：受影响束的 range 取 min(原值, 注入距离)——即"更近处出现了障碍"。
按 /inject 话题（std_msgs/Bool）可开关注入，便于"注入前回基线"。"""
import argparse, math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool


class ScanInject(Node):
    def __init__(self, bearing_deg, dist, width):
        super().__init__("scan_inject")
        self.bearing = math.radians(bearing_deg); self.dist = dist; self.width = width
        self.enabled = True
        qos = QoSProfile(depth=5, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sub = self.create_subscription(LaserScan, "/scan", self.cb, qos)
        self.pub = self.create_publisher(LaserScan, "/scan_injected", qos)
        self.create_subscription(Bool, "/inject", lambda m: setattr(self, "enabled", bool(m.data)), 10)

    def cb(self, m):
        out = LaserScan()
        out.header = m.header
        out.angle_min, out.angle_max, out.angle_increment = m.angle_min, m.angle_max, m.angle_increment
        out.time_increment, out.scan_time = m.time_increment, m.scan_time
        out.range_min, out.range_max = m.range_min, m.range_max
        ranges = list(m.ranges)
        if self.enabled and self.dist > 0:
            half_ang = math.atan2(self.width / 2.0, self.dist)          # 障碍张角的一半
            for i in range(len(ranges)):
                ang = m.angle_min + i * m.angle_increment
                d = math.atan2(math.sin(ang - self.bearing), math.cos(ang - self.bearing))
                if abs(d) <= half_ang:
                    r = ranges[i]
                    ranges[i] = self.dist if (math.isnan(r) or r > self.dist) else r   # 更近处出现障碍
        out.ranges = ranges
        out.intensities = list(m.intensities) if m.intensities else []
        self.pub.publish(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bearing", type=float, default=0.0, help="障碍方位（°，机器人坐标系，0=正前方）")
    ap.add_argument("--dist", type=float, default=1.5, help="障碍距离（m）")
    ap.add_argument("--width", type=float, default=0.4, help="障碍宽度（m）")
    a = ap.parse_args()
    rclpy.init()
    node = ScanInject(a.bearing, a.dist, a.width)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()


if __name__ == "__main__":
    main()
