#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plan_auditor.py · 第8课 Plan Auditor：白名单前置＋四规则（task8.pptx P4/P8/P14）

数据来源（全部本组数据，P8 接口表）：
  规则① costmap：~/sim_ops/maps/map_gt.{pgm,yaml}（origin(0,0,0)、res 0.05、200×200 → 数值域 x,y∈[0,10]）
  规则② 语义地图：../task6_semanticmap/semantic_map_v1_G42.json ＋ 第6课《过期检测规则表》τ 三档（占位值，E3）
  规则③ 参数值域：isfinite(x,y)（NaN 拦截）；可选参数物理边界（speed 由第7课 schema 前置拦，此处防御）；
            label ∈ 已知集合并入②的 has_fresh 判定（不存在/已过期同一条文案，P8 模板）
  规则④ 资源可行：电量 ≥15%／预估用时 ≤ 预算（孪生占位电量 82%；实车＝底盘遥测）

审计顺序（P13 案例①：白名单最前——编造工具在四规则之前就被拦下）：
  白名单 → ③isfinite → ③speed防御 → ①in_bounds → ①is_occupied → ②has_fresh → ④电量 → ④用时

纪律：
  - 拒绝文案＝P4 模板逐条落进 f-string：超范围报坐标、过期附可用清单、低电报阈值——「无法执行」四个字不算（P5）。
  - 骨架默认 ttl=300 为占位值——已替换为本组 τ 表（TAU_MIN，第6课三档）。
  - 白名单复用第7课 schemas.SCHEMAS（冻结版）——schema_check 升级驻场：编造工具在四规则之前就被拦下（P4）。

用法：
  python3 plan_auditor.py --check-call navigate_to '{"x": 8.6, "y": 5.2, "label": "door"}'
  python3 plan_auditor.py --check-call navigate_to '{"x": 50, "y": 50}'
  八发测试：python3 test_plan_auditor.py

变更登记 2026-10-19：第8课 T1.1 创建（Claude 起草，P13 案例① 审核对象——审核结论见《AI辅助使用记录表_第8课.md》）。
"""
import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "task7_loadLLM"))
from schemas import SCHEMAS  # noqa: E402

WHITELIST = list(SCHEMAS)  # 白名单最前（第7课冻结版五件套）

MAP_PGM = Path.home() / "sim_ops" / "maps" / "map_gt.pgm"
MAP_YAML = Path.home() / "sim_ops" / "maps" / "map_gt.yaml"
SEMANTIC_MAP = HERE.parent / "task6_semanticmap" / "semantic_map_v1_G42.json"

BATTERY_MIN = 15        # %（P8/P12 阈值）
BATTERY_DEFAULT = 82    # 孪生占位电量（第7课 world_state 占位，实车＝底盘遥测）
SPEED_LIMIT = 0.25      # m/s（第4课 nav2_params_sim.yaml 限速，P12 阈值出处）
TIME_BUDGET = 300.0     # s，④预估用时预算（占位值，可变更登记）
OCCUPIED_TH = 50        # 占据判据＝栅格值 < 50（本平台 make_gt_map.py 约定：254=自由、0=占据/墙/障碍——
                        # 与教学判据「≥50」（ROS 三值 0自由/100占据/254未知）调色板相反，见《规则溯源表》①行与变更登记；
                        # 若教师下发 ROS 标准三值图，改判据为 50 ≤ v < 200 占据并登记）
W8_HOME = (8.08, 6.24)  # 当前位姿占位（第7课 world_state；④用时估算起点）
# 第6课《过期检测规则表》τ 三档（占位值，task8 E3：课内以本组观测改写或变更登记）
TAU_MIN = {"人": 10, "手持物": 30, "家具": 180}
TAU_WAYPOINT_MIN = 180  # 命名点位＝固定设施 → 家具档（本组决定，见《规则溯源表_第8课.md》②行）


class Costmap:
    """map_gt 代价地图只读视图（规则①）。P5 二进制 PGM 解析，无第三方依赖。"""

    def __init__(self, pgm=MAP_PGM, yaml_path=MAP_YAML, occupied_th=OCCUPIED_TH):
        import yaml
        self.meta = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
        self.resolution = float(self.meta["resolution"])
        self.origin = [float(v) for v in self.meta["origin"][:2]]
        self.occupied_th = occupied_th
        self._load_pgm(Path(pgm))

    def _load_pgm(self, path):
        raw = path.read_bytes()
        # P5 头：magic（第1行，跳过）→ 注释行(#) → 「宽 高」→ 最大灰度 → 二进制栅格
        lines, pos = [], raw.index(b"\n") + 1
        while len(lines) < 2 and pos < len(raw):
            nl = raw.index(b"\n", pos)
            line = raw[pos:nl].decode("ascii").strip()
            pos = nl + 1
            if not line or line.startswith("#"):
                continue
            lines.append(line)
        self.width, self.height = (int(v) for v in lines[0].split())
        self.maxval = int(lines[1])
        self.data = raw[pos: pos + self.width * self.height]
        if len(self.data) < self.width * self.height:
            raise ValueError(f"PGM 栅格数据不足: {len(self.data)} < {self.width * self.height}")

    def world_to_cell(self, x, y):
        # PGM 行 0 = 图像顶部 = 世界 y 最大（make_gt_map.py: cy_w=(hpx-ys-0.5)*res），读图须翻转
        return (int((x - self.origin[0]) / self.resolution),
                self.height - 1 - int((y - self.origin[1]) / self.resolution))

    def in_bounds(self, x, y):
        cx, cy = self.world_to_cell(x, y)
        return 0 <= cx < self.width and 0 <= cy < self.height

    def cell_value(self, x, y):
        if not self.in_bounds(x, y):
            return None
        cx, cy = self.world_to_cell(x, y)
        return self.data[cy * self.width + cx]

    def is_occupied(self, x, y):
        v = self.cell_value(x, y)
        return v is not None and v < self.occupied_th  # 本平台调色板：0=占据，254=自由（见 OCCUPIED_TH 注释）


class SemanticMap:
    """语义地图查询（规则②）：label 存在且 last_seen 未过期（age ≤ τ_class）。

    第6课契约：查询时计算 age_s = now − last_seen，state = stale 若 age_s > τ_class。
    """

    def __init__(self, path=SEMANTIC_MAP, data=None, now=None, tau_min=None):
        self.data = data if data is not None else json.loads(Path(path).read_text(encoding="utf-8"))
        self.tau_min = tau_min or TAU_MIN
        # now 可注入（测试/干跑对齐 exported_at；默认系统当前时间）
        self.now = now if now is not None else datetime.now().astimezone()

    def labels(self):
        s = set()
        for w in self.data.get("waypoints", []):
            s.add(w["label"])
            s.add(w["id"])
        for o in self.data.get("objects", []):
            s.add(o["label"])
        return sorted(s)

    def _parse_ts(self, s):
        return datetime.fromisoformat(s)

    def has_fresh(self, lbl):
        """返回 (ok, msg)。命名点位＝固定设施恒 fresh（家具档 τ）；物体按 last_seen 计算 age。"""
        for w in self.data.get("waypoints", []):
            if lbl in (w["label"], w["id"]):
                return True, f"命名点位 {w['id']}（固定设施，恒 fresh）"
        for o in self.data.get("objects", []):
            if lbl == o["label"]:
                age_s = (self.now - self._parse_ts(o["last_seen"])).total_seconds()
                tau_s = self.tau_min.get(o.get("class", "家具"), TAU_WAYPOINT_MIN) * 60
                if age_s <= tau_s:
                    return True, f"{lbl}: age_s={age_s:.0f}s ≤ τ={tau_s:.0f}s，fresh"
                return False, f"语义地图中'{lbl}'信息已过期（age_s={age_s:.0f}s > τ={tau_s:.0f}s）。当前可用: {', '.join(self.labels())}"
        return False, f"语义地图中不存在'{lbl}'。当前可用: {', '.join(self.labels())}"


class Battery:
    """电量（规则④）：孪生＝占位参数；实车＝底盘遥测。"""

    def __init__(self, percent=BATTERY_DEFAULT):
        self._pct = percent

    def percent(self):
        return self._pct


class PlanAuditor:
    """白名单最前，四规则逐条，拒绝携证据（P8 骨架）。audit(call) → (ok, reason)。"""

    def __init__(self, semantic_map=None, costmap=None, battery=None):
        self.sm = semantic_map or SemanticMap()
        self.costmap = costmap or Costmap()
        self.battery = battery or Battery()

    def audit(self, call):
        if not isinstance(call, dict):
            call = {"name": getattr(call, "name", None), "arguments": getattr(call, "arguments", {})}
        name = call.get("name")
        if name not in WHITELIST:  # 白名单最前（P13 案例①）
            return False, f"白名单｜工具 {name} 不存在（模型编造）"
        args = call.get("arguments") or {}

        if name == "navigate_to":
            x, y = args["x"], args["y"]
            # 规则③ 值域：非有限数值（NaN 拦在这里；P4 模板）
            if not math.isfinite(x):
                return False, f"规则③｜参数非法：x={x} 非有限数值"
            if not math.isfinite(y):
                return False, f"规则③｜参数非法：y={y} 非有限数值"
            # 规则③ 可选参数物理边界（五件套无 speed 参数；schema 前置拦截，此处防御）
            if "speed" in args:
                return False, f"规则③｜参数非法：speed={args['speed']} 不在物理边界内（五件套无 speed 参数）"
            # 规则① 虚拟围栏
            if not self.costmap.in_bounds(x, y):
                return False, f"规则①｜目标({x},{y})超出地图范围"
            if self.costmap.is_occupied(x, y):
                return False, f"规则①｜目标({x},{y})位于障碍物内"
            # 规则② 地标存在性
            lbl = args.get("label")
            if lbl:
                ok, msg = self.sm.has_fresh(lbl)
                if not ok:
                    return False, f"规则②｜{msg}" 
            # 规则④ 预估用时（路径长÷限速；起点占位 W8_home）
            dist = math.hypot(x - W8_HOME[0], y - W8_HOME[1])
            est = dist / SPEED_LIMIT
            if est > TIME_BUDGET:
                return False, f"规则④｜预估用时 {est:.0f}s 超过预算 {TIME_BUDGET:.0f}s"

        # 规则④ 电量（所有工具共用）
        pct = self.battery.percent()
        if pct < BATTERY_MIN:
            return False, f"规则④｜电量不足 {BATTERY_MIN}%，拒绝新任务（当前 {pct}%）"
        return True, "ok"


def main():
    ap = argparse.ArgumentParser(description="第8课 Plan Auditor 单发查询")
    ap.add_argument("--check-call", nargs=2, metavar=("NAME", "ARGS_JSON"), help="单发审计")
    args = ap.parse_args()
    if not args.check_call:
        print(__doc__)
        return
    name, args_json = args.check_call
    auditor = PlanAuditor()
    ok, reason = auditor.audit({"name": name, "arguments": json.loads(args_json)})
    print(("放行" if ok else "拒绝") + f" [{name}]: {reason}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
