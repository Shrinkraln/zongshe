#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_plan_auditor.py · 第8课 八发测试（task8.pptx P14；task8/task_plan.md T0.5/T1.2）

八发基线（每规则好/坏各 1）＋ 2 发冗余（①②的第二种坏变体）＝ 10 发；判据按「八发全中」。
判据（P14）：坏用例 reason 指向正确规则且含数值／清单；「无法执行」四个字不算。
纪律（P14）：八发不含「速度」用例——speed 额外参数与编造工具由第7课 schema_check／白名单前置拦截。
数据：全部本组在盘数据（map_gt 真实栅格、semantic_map_v1_G42.json、第6课 τ 三档）。
  · fresh 用例 now＝语义地图 exported_at（查询时刻对齐导出时刻，与文件内 age_s/state 自洽）；
  · stale 用例注入 last_seen＝now−2000s（cup 手持物 τ=30min=1800s → stale，即对照实验 T6 预演）；
  · 障碍内 (4.52,7.80)＝第4课真值障碍圆心（对照实验 T5 预演）。

用法：python3 test_plan_auditor.py [--log logs/audit_8shots.log]
变更登记 2026-10-19：第8课 T0.5/T1.2 创建（Claude 起草；用例坐标来源见《规则溯源表_第8课.md》）。
"""
import argparse
import copy
import json
import math
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from plan_auditor import Battery, Costmap, PlanAuditor, SemanticMap  # noqa: E402

SEMANTIC_MAP = HERE.parent / "task6_semanticmap" / "semantic_map_v1_G42.json"


def load_data():
    return json.loads(SEMANTIC_MAP.read_text(encoding="utf-8"))


def make_sm(data, now):
    return SemanticMap(data=data, now=now)


def nav(x, y, label=None, **extra):
    args = {"x": x, "y": y}
    if label is not None:
        args["label"] = label
    args.update(extra)
    return {"name": "navigate_to", "arguments": args}


def build_cases():
    data = load_data()
    exported_at = datetime.fromisoformat(data["meta"]["exported_at"])  # 与文件内 age_s/state 自洽
    stale_data = copy.deepcopy(data)
    for o in stale_data["objects"]:
        if o["label"] == "cup":
            o["last_seen"] = "2026-10-12T14:16:40+08:00"  # exported_at(14:50)−2000s → age=2000s > τ 1800s
    sm_fresh = make_sm(data, exported_at)
    sm_stale = make_sm(stale_data, exported_at)

    cases = [
        # 规则① 好：清单内自由格（W1_door，距最近障碍≈1.26m）
        ("①好 清单内自由格 W1_door", sm_fresh, Battery(60), nav(8.60, 5.20, label="door"), True, "ok", ""),
        # 规则① 坏a：地图外（官方 T2）
        ("①坏a 地图外 (50,50)＝官方T2", sm_fresh, Battery(60), nav(50, 50), False, "超出地图范围", "①"),
        # 规则① 坏b：障碍内（第4课真值障碍圆心，补充 T5）
        ("①坏b 障碍内 (4.52,7.80)＝T5", sm_fresh, Battery(60), nav(4.52, 7.80), False, "位于障碍物内", "①"),
        # 规则② 好：fresh 的 label（cup，age_s=900s ≤ τ=1800s）
        ("②好 fresh cup", sm_fresh, Battery(60), nav(2.70, 4.50, label="cup"), True, "ok", ""),
        # 规则② 坏a：清单外 label（kitchen）
        ("②坏a 清单外 label=kitchen", sm_fresh, Battery(60), nav(5.0, 5.0, label="kitchen"), False, "不存在'kitchen'", "②"),
        # 规则② 坏b：超龄 label（cup age 2000s > τ，补充 T6）
        ("②坏b 超龄 cup age2000s＝T6", sm_stale, Battery(60), nav(2.70, 4.50, label="cup"), False, "已过期", "②"),
        # 规则③ 好：有限且在数值域内、label ∈ 已知集合（W1_door id 形式）
        ("③好 值域有限 label=W1_door", sm_fresh, Battery(60), nav(8.60, 5.20, label="W1_door"), True, "ok", ""),
        # 规则③ 坏：x=NaN 非有限（P4 模板文案）
        ("③坏 x=NaN 非有限数值", sm_fresh, Battery(60), nav(float("nan"), 5.2), False, "非有限数值", "③"),
        # 规则④ 好：电量 60%
        ("④好 电量60%", sm_fresh, Battery(60), nav(8.60, 5.20), True, "ok", ""),
        # 规则④ 坏：电量 10% < 15%
        ("④坏 电量10%", sm_fresh, Battery(10), nav(8.60, 5.20), False, "电量不足", "④"),
    ]
    return cases, sm_fresh, sm_stale


def run(cases, log_path=None):
    auditor = PlanAuditor()  # 真实 Costmap（map_gt）；sm/battery 逐发替换
    lines = []
    n_fail = 0
    for label, sm, battery, call, expect_ok, expect_msg, rule_tag in cases:
        auditor.sm = sm
        auditor.battery = battery
        ok, reason = auditor.audit(call)
        args_str = json.dumps(call["arguments"], ensure_ascii=False)
        pass_ = (ok == expect_ok) and (expect_msg in reason)
        if not pass_:
            n_fail += 1
        line = (f"[{'PASS' if pass_ else 'FAIL'}] {label} | {call['name']}({args_str}) "
                f"→ ok={ok} reason={reason!r}（期望 ok={expect_ok}，含 {expect_msg!r}，规则 {rule_tag}）")
        lines.append(line)
        print(line)
    summary = f"八发测试: {len(cases) - n_fail}/{len(cases)} passed（八发基线+2冗余）"
    print(summary)
    lines.append(summary)
    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("# 八发测试 · 第8课 task8.pptx P14（重跑追加，最新一次在末尾）\n")
            f.write("\n".join(lines) + "\n\n")
        print(f"已写入日志: {log_path}")
    return n_fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=str(HERE / "logs" / "audit_8shots.log"))
    args = ap.parse_args()
    cases, _, _ = build_cases()
    sys.exit(1 if run(cases, args.log) else 0)


if __name__ == "__main__":
    main()
