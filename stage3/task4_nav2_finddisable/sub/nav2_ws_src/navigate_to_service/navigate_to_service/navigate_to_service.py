# -*- coding: utf-8 -*-
"""navigate_to 服务 —— 第4课 navigate_to 封装（PPT P8 契约 / P15 骨架）。

契约（P8）：
  请求 x, y, theta（目标位姿）；响应 result ∈ {SUCCEEDED, FAILED, TIMEOUT}
  + reason（可读文字） + elapsed（用时 s）。
  失败必须带原因；超时先取消再返回（顺序不可颠倒）；缺字段拒绝执行（不自动补默认值）。

实现要点（P15 骨架）：
  ① 组装目标位姿 → Nav2 NavigateToPose 动作客户端；
  ② 预算 60 s 耗尽 → 先 cancel_goal → 确认目标终止 → 再返回 TIMEOUT；
  ③ 翻译结果：成功 → SUCCEEDED；Nav2 报失败 → FAILED + 可读原因；预算耗尽 → TIMEOUT。
  另：下发前用 GetMap 预检 in_bounds / is_occupied（第 8 课规则① 的行为样板），
      障碍内目标数秒内即返回 "FAILED：目标位于障碍物内"（P18 有依据的失败反馈）。

AI 起草（P13 案例②）：无无限重试；失败带原因；缺字段拒绝执行；超时先取消再返回。
"""

import math
import time

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import GoalStatus

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose as Nav2Action
from nav_msgs.srv import GetMap
from navigate_to_interfaces.srv import NavigateTo

BUDGET_S = 60.0          # 超时预算（P8/P15）
ACCEPT_TIMEOUT_S = 5.0   # 动作接受等待
CANCEL_WAIT_S = 10.0     # 取消后等待目标终止
OCCUPIED_THRESH = 65     # nav2 默认 occupied_thresh 0.65 → 65/100

# nav2_msgs ComputePathToPose 结果错误码 → 可读文字（P8：reason 必须可读，错误码不算）
NAV2_ERR_TEXT = {
    30001: "规划超时",
    30002: "起点超出地图边界",
    30003: "目标超出地图边界",
    30004: "起点位于障碍物内",
    30005: "目标位于障碍物内",
    30006: "规划失败",
}


class NavigateToService(Node):

    def __init__(self):
        super().__init__("navigate_to_server")
        cb_group = ReentrantCallbackGroup()
        # 对上：服务 /navigate_to（P15）
        # 注意：回调不得命名 handle——rclpy.Node.handle 是只读属性（返回底层 C 句柄），
        # 同名方法会遮蔽它，导致基类 __init__ 中 `with self.handle:` 抛 AttributeError。
        self.srv = self.create_service(
            NavigateTo, "/navigate_to", self._on_navigate_to, callback_group=cb_group)
        # 对下：Nav2 NavigateToPose 动作客户端
        self.nav2_cli = ActionClient(self, Nav2Action, "/navigate_to_pose")
        # 预检：地图服务（in_bounds / is_occupied）
        self.map_cli = self.create_client(GetMap, "/map_server/map")

    def _check_goal(self, x, y):
        """预检：目标在地图内且非障碍。返回 (ok, fail_reason)。"""
        if not self.map_cli.wait_for_service(timeout_sec=3.0):
            self.get_logger().warn("[navigate_to] /map_server/map 不可用，跳过预检")
            return True, ""
        fut = self.map_cli.call_async(GetMap.Request())
        rclpy.spin_until_future_complete(self, fut, timeout_sec=3.0)
        if not fut.done():
            self.get_logger().warn("[navigate_to] GetMap 超时，跳过预检")
            return True, ""
        om = fut.result().map
        cx = int(round((x - om.info.origin.position.x) / om.info.resolution))
        cy = int(round((y - om.info.origin.position.y) / om.info.resolution))
        if not (0 <= cx < om.info.width and 0 <= cy < om.info.height):
            return False, "目标超出地图边界"
        v = om.data[cy * om.info.width + cx]
        if v < 0 or v >= OCCUPIED_THRESH:
            return False, "目标位于障碍物内"
        return True, ""

    def _on_navigate_to(self, req, resp):
        t0 = time.monotonic()
        resp.elapsed = 0.0

        # P13 案例②：缺字段拒绝执行，不自动补默认值
        if not all(math.isfinite(v) for v in (req.x, req.y, req.theta)):
            resp.result = "FAILED"
            resp.reason = "请求字段缺失或非法"
            self.get_logger().error(
                f"[navigate_to] 拒绝执行（字段非法）：x={req.x} y={req.y} theta={req.theta}")
            return resp

        # 预检：in_bounds / is_occupied（P18：有依据的失败反馈，数秒返回）
        ok, fail_reason = self._check_goal(req.x, req.y)
        if not ok:
            resp.result = "FAILED"
            resp.reason = fail_reason
            resp.elapsed = round(time.monotonic() - t0, 2)
            self.get_logger().info(
                f"[navigate_to] ({req.x:.2f},{req.y:.2f},{req.theta:.2f}) → "
                f"FAILED[{resp.elapsed}s] {fail_reason}")
            return resp

        # ① 组装目标位姿（P15）
        if not self.nav2_cli.wait_for_server(timeout_sec=ACCEPT_TIMEOUT_S):
            resp.result = "FAILED"
            resp.reason = "Nav2 导航服务未就绪"
            resp.elapsed = round(time.monotonic() - t0, 2)
            return resp
        goal_msg = Nav2Action.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = req.x
        goal_msg.pose.pose.position.y = req.y
        goal_msg.pose.pose.orientation.z = math.sin(req.theta / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(req.theta / 2.0)
        self.get_logger().info(
            f"[navigate_to] 目标 ({req.x:.2f},{req.y:.2f},{req.theta:.2f}) 已下发，预算 {BUDGET_S:.0f}s")

        goal_future = self.nav2_cli.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, goal_future, timeout_sec=ACCEPT_TIMEOUT_S)
        if not goal_future.done():
            resp.result = "FAILED"
            resp.reason = "导航目标未被接受（超时）"
            resp.elapsed = round(time.monotonic() - t0, 2)
            return resp
        goal_handle = goal_future.result()
        if not goal_handle.accepted:
            resp.result = "FAILED"
            resp.reason = "导航目标被拒绝"
            resp.elapsed = round(time.monotonic() - t0, 2)
            return resp

        # ② 等待结果，带 60 s 预算
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=BUDGET_S)
        if not result_future.done():
            # 预算耗尽：先主动取消导航（顺序不可颠倒，P8）
            self.get_logger().warn(
                f"[navigate_to] {BUDGET_S:.0f}s 预算耗尽 → 先取消导航")
            cancel_future = goal_handle.cancel_goal_async()
            rclpy.spin_until_future_complete(self, cancel_future, timeout_sec=CANCEL_WAIT_S)
            # 确认目标真正终止后再返回（车已停止）
            term_future = goal_handle.get_result_async()
            rclpy.spin_until_future_complete(self, term_future, timeout_sec=CANCEL_WAIT_S)
            if not term_future.done():
                self.get_logger().warn("[navigate_to] 取消后 10s 目标仍未终止，仍按契约返回")
            resp.result = "TIMEOUT"
            resp.reason = f"{BUDGET_S:.0f} s 未到达"
            resp.elapsed = round(time.monotonic() - t0, 2)
            self.get_logger().info(
                f"[navigate_to] ({req.x:.2f},{req.y:.2f},{req.theta:.2f}) → "
                f"TIMEOUT[{resp.elapsed}s] {resp.reason}")
            return resp

        # ③ 翻译结果（P15）
        result = result_future.result()
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            resp.result = "SUCCEEDED"
            resp.reason = "到达目标"
        else:
            resp.result = "FAILED"
            code = result.result.error_code
            msg = result.result.error_msg
            resp.reason = NAV2_ERR_TEXT.get(code) or (msg if msg else f"导航失败(code={code})")
        resp.elapsed = round(time.monotonic() - t0, 2)
        self.get_logger().info(
            f"[navigate_to] ({req.x:.2f},{req.y:.2f},{req.theta:.2f}) → "
            f"{resp.result}[{resp.elapsed}s] {resp.reason}")
        return resp


def main():
    rclpy.init()
    node = NavigateToService()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        # Ctrl+C 时 rclpy 的 SIGINT 处理器已调用过 shutdown，二次调用会抛
        # RCLError("rcl_shutdown already called")——ok() 守卫后再调
        rclpy.shutdown()


if __name__ == "__main__":
    main()
