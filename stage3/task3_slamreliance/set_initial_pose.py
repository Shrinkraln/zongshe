#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""set_initial_pose.py —— 第3课 AMCL 初始位姿发布工具（避开 ros2 topic pub 的 YAML 引号坑）。

条件A（正确初始位姿）：直接用小车当前真值：
  python3 set_initial_pose.py --x 2.278 --y 0.102 --yaw-deg -136.3
条件B（初始位姿偏置1m，位置＋朝向）：在真值基础上自行加偏置：
  python3 set_initial_pose.py --x <真值x+偏置> --y <真值y+偏置> --yaw-deg <真值朝向+偏置>
可选 --frame map（默认）、--cov 初始协方差（默认 0.25m/0.0685rad，符合课程口径）。

依赖：rclpy（ROS2 环境 source 后运行）。
"""

import argparse
import math
import sys

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped


def main():
    ap = argparse.ArgumentParser(description="发布 AMCL /initialpose（PoseWithCovarianceStamped）")
    ap.add_argument("--x", type=float, required=True)
    ap.add_argument("--y", type=float, required=True)
    ap.add_argument("--yaw-deg", type=float, default=None, help="朝向角（度）")
    ap.add_argument("--yaw-rad", type=float, default=None, help="朝向角（弧度，与 --yaw-deg 二选一）")
    ap.add_argument("--frame", default="map")
    ap.add_argument("--cov", type=float, default=0.25, help="x/y 方差（m²，默认 0.25）")
    args = ap.parse_args()

    if args.yaw_deg is None and args.yaw_rad is None:
        ap.error("必须给 --yaw-deg 或 --yaw-rad")
    yaw = math.radians(args.yaw_deg) if args.yaw_deg is not None else args.yaw_rad

    rclpy.init()
    node = rclpy.create_node("set_initial_pose")
    pub = node.create_publisher(PoseWithCovarianceStamped, "/initialpose", 10)

    msg = PoseWithCovarianceStamped()
    msg.header.frame_id = args.frame
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.pose.pose.position.x = args.x
    msg.pose.pose.position.y = args.y
    msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
    msg.pose.pose.orientation.w = math.cos(yaw / 2.0)
    msg.pose.covariance[0] = args.cov        # x 方差
    msg.pose.covariance[7] = args.cov        # y 方差
    msg.pose.covariance[35] = 0.0685         # yaw 方差（≈7.5°）

    pub.publish(msg)
    # 等一小会儿确保发出去（AMCL 订阅 transient 与否都可收到）
    rclpy.spin_once(node, timeout_sec=0.5)
    print(f"已发布 /initialpose: x={args.x} y={args.y} "
          f"yaw={math.degrees(yaw):.1f}° (frame={args.frame}, cov={args.cov})")
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
