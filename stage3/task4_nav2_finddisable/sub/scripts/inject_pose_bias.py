#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inject_pose_bias.py —— 第4课注入③一键工具（真值读取 + /initialpose 偏置发布合并）。

作用：一次执行完成「读真值 → 加偏置 → 发布 /initialpose」，输出合并为一份，
     减少真值读出与注入之间的手工抄录延迟（车在动，读值越快越新鲜）。
契约：与 truth_probe.py 同源——GET /health 取 robot_truth；
     发布侧同 set_initial_pose.py——PoseWithCovarianceStamped 到 /initialpose。
纪律：注入后 AMCL 估计与真值的差即为注入偏置（另用 truth_probe 复核，两条证据链独立）。

用法（条件 B：位置＋朝向偏置 1 m / 30°，本课③默认参数）：
  python3 inject_pose_bias.py --host 127.0.0.1
可调偏置（默认 +1.0 m x / +0.0 m y / +30° yaw）：
  python3 inject_pose_bias.py --host 127.0.0.1 --dx 1.0 --dy 0.0 --yaw-bias 30

依赖：rclpy（ROS2 环境 source 后运行）；真值部分仅 stdlib。
"""

import argparse
import json
import math
import urllib.request

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped


def probe_truth(host: str, port: int) -> dict:
    url = f"http://{host}:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise SystemExit(f"[inject_pose_bias] 真值查询失败 {url}: {e}\n"
                         f"  检查：网关是否在跑 nav_gateway.py？IP/端口是否正确？")
    truth = data.get("robot_truth")
    if truth is None:
        raise SystemExit(f"[inject_pose_bias] 响应无 robot_truth 字段：{json.dumps(data, ensure_ascii=False)}")
    return data, truth


def norm_deg(deg: float) -> float:
    """归一到 [-180, 180)。"""
    return (deg + 180.0) % 360.0 - 180.0


def main() -> None:
    ap = argparse.ArgumentParser(description="读真值 → 加偏置 → 发布 /initialpose（注入③一键）")
    ap.add_argument("--host", required=True, help="笔记本（网关）IP")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--dx", type=float, default=1.0, help="x 偏置（m，默认 +1.0）")
    ap.add_argument("--dy", type=float, default=0.0, help="y 偏置（m，默认 0）")
    ap.add_argument("--yaw-bias", type=float, default=30.0, help="朝向偏置（度，默认 +30）")
    ap.add_argument("--frame", default="map")
    ap.add_argument("--cov", type=float, default=0.25, help="x/y 初始协方差（m²，默认 0.25）")
    args = ap.parse_args()

    # ① 读真值
    data, truth = probe_truth(args.host, args.port)
    tx, ty, tdeg = truth["x"], truth["y"], truth["theta_deg"]

    # ② 加偏置
    bx = tx + args.dx
    by = ty + args.dy
    bdeg = norm_deg(tdeg + args.yaw_bias)
    byaw = math.radians(bdeg)

    # ③ 发布 /initialpose
    rclpy.init()
    node = rclpy.create_node("inject_pose_bias")
    pub = node.create_publisher(PoseWithCovarianceStamped, "/initialpose", 10)
    msg = PoseWithCovarianceStamped()
    msg.header.frame_id = args.frame
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.pose.pose.position.x = bx
    msg.pose.pose.position.y = by
    msg.pose.pose.orientation.z = math.sin(byaw / 2.0)
    msg.pose.pose.orientation.w = math.cos(byaw / 2.0)
    msg.pose.covariance[0] = args.cov        # x 方差
    msg.pose.covariance[7] = args.cov        # y 方差
    msg.pose.covariance[35] = 0.0685         # yaw 方差（≈7.5°）
    # ③ 发布 /initialpose——必须存活 ≥3s 并重复发布：
    # 2026-09-22 实测 DDS 端点发现延迟 ~1.2s，发布后仅存活 0.5s（原 set_initial_pose.py
    # 同款写法）消息全部丢失、AMCL 零接收 → ③ 主试曾因此无效（findings #35）。
    import time
    for _ in range(30):
        pub.publish(msg)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(0.1)
    node.destroy_node()
    rclpy.shutdown()

    # ④ 合并输出（供记录表/变更登记直接抄录）
    print(f"真值 (x, y, θ°) = ({tx:.3f}, {ty:.3f}, {tdeg:.1f})  "
          f"[tick_n={data.get('tick_n')}]")
    print(f"注入偏置 = (+{args.dx:g} m x, {args.dy:+g} m y, {args.yaw_bias:+g}° yaw)")
    print(f"已发布 /initialpose: x={bx:.3f} y={by:.3f} yaw={bdeg:.1f}° "
          f"(frame={args.frame}, cov={args.cov})")


if __name__ == "__main__":
    main()
