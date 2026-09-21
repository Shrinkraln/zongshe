#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_mask.py —— 第4课失效注入②（感知降级）课程工具骨架：屏蔽激光扫描的一段连续视场，输出 /scan_masked。
仅用于孪生侧（Embodied-SimLite + ros_bridge），不得接入实车 /scan 链路。
用法：python3 scan_mask.py --sector 30 [--center 90]   # 屏蔽以 center(°) 为中心、占总视场 sector% 的连续扇区
Nav2 侧把 scan 话题重映射为 /scan_masked（或在 params 中改 scan_topic）。
被屏蔽的束设为 NaN（多数 Nav2 costmap 配置视为无返回）。"""
import argparse, math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan


class ScanMask(Node):
    def __init__(self, sector_pct, center_deg):
        super().__init__("scan_mask")
        self.sector_pct = sector_pct
        self.center = math.radians(center_deg)
        qos = QoSProfile(depth=5, reliability=ReliabilityPolicy.BEST_EFFORT)  # 桥接为 BEST_EFFORT
        self.sub = self.create_subscription(LaserScan, "/scan", self.cb, qos)
        self.pub = self.create_publisher(LaserScan, "/scan_masked", qos)
        self.n = 0

    def cb(self, m):
        out = LaserScan()
        out.header = m.header
        out.angle_min, out.angle_max, out.angle_increment = m.angle_min, m.angle_max, m.angle_increment
        out.time_increment, out.scan_time = m.time_increment, m.scan_time
        out.range_min, out.range_max = m.range_min, m.range_max
        ranges = list(m.ranges)
        total = len(ranges)
        half = int(total * self.sector_pct / 100.0 / 2)
        ci = int(round((self.center - m.angle_min) / m.angle_increment)) % max(total, 1)
        for k in range(-half, half + 1):
            ranges[(ci + k) % total] = float("nan")   # 被遮挡：无返回
        out.ranges = ranges
        out.intensities = list(m.intensities) if m.intensities else []
        self.pub.publish(out)
        self.n += 1
        if self.n % 50 == 0:
            self.get_logger().info(f"masked {2*half+1}/{total} beams (≈{self.sector_pct}%) around {math.degrees(self.center):.0f}°")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sector", type=float, default=30.0, help="屏蔽的连续视场占比（%）")
    ap.add_argument("--center", type=float, default=0.0, help="屏蔽扇区中心方位（°，0=正前方）")
    a = ap.parse_args()
    rclpy.init()
    node = ScanMask(a.sector, a.center)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()


if __name__ == "__main__":
    main()
