#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
schema_check.py · 第7课 工具调用校验器（P16–P17 骨架）
两道关卡：① 白名单（工具名）→ ② jsonschema 参数校验。白名单在前、jsonschema 在后。
纪律（P9/P13 案例②）：无任何「修复」分支——缺 y 不补默认值、坏类型不改写；
修复权属于重新规划，不属于校验器。看到「自动补默认值」分支＝删。
用法：
  python3 schema_check.py --self-test                     # T2.2 三种坏调用 + 好调用
  python3 schema_check.py --check-log logs/plan_log_G42.jsonl   # 批量校验干跑日志全部 tool_calls
"""
import json
import sys

import jsonschema

from schemas import SCHEMAS


def schema_check(call):
    """call: {'name': str, 'arguments': dict} → (ok: bool, msg: str)"""
    if call["name"] not in SCHEMAS:
        return False, f"编造工具: {call['name']}"
    try:
        jsonschema.validate(call["arguments"], SCHEMAS[call["name"]]["parameters"])
    except jsonschema.ValidationError as e:
        return False, f"参数非法: {e.message}"
    return True, "OK"


# T2.2 三种坏调用（P17 表）＋好调用对照
SELF_TESTS = [
    ({"name": "pick_up", "arguments": {"x": 1.0, "y": 2.0}},
     False, "编造工具: pick_up"),
    ({"name": "navigate_to", "arguments": {"x": 1.0}},
     False, "'y' is a required property"),
    ({"name": "navigate_to", "arguments": {"x": "门口附近", "y": 2.0}},
     False, "is not of type 'number'"),
    ({"name": "navigate_to", "arguments": {"x": 8.6, "y": 5.2, "label": "W1_door"}},
     True, "OK"),
    ({"name": "get_semantic_map", "arguments": {}},
     True, "OK"),
    ({"name": "stop", "arguments": {}},
     True, "OK"),
]


def self_test():
    n_fail = 0
    for call, expect_ok, expect_msg in SELF_TESTS:
        ok, msg = schema_check(call)
        pass_ = (ok == expect_ok) and (expect_msg in msg)
        mark = "PASS" if pass_ else "FAIL"
        if not pass_:
            n_fail += 1
        print(f"[{mark}] {call['name']} {json.dumps(call['arguments'], ensure_ascii=False)} "
              f"→ ok={ok} msg={msg!r}（期望 {expect_msg!r}）")
    print(f"self-test: {len(SELF_TESTS) - n_fail}/{len(SELF_TESTS)} passed")
    return n_fail


def check_log(path):
    """批量校验 plan_log 中全部 tool_calls（T3.4 契约：进入执行队列的前提＝schema_check 通过）。"""
    n_calls = n_bad = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            for tc in rec.get("tool_calls", []):
                n_calls += 1
                ok, msg = schema_check(tc)
                if not ok:
                    n_bad += 1
                    print(f"[REJECT] {rec.get('ts')} temp={rec.get('temperature')} "
                          f"指令={rec.get('instruction')!r} → {msg} {json.dumps(tc['arguments'], ensure_ascii=False)}")
    print(f"check-log: 共 {n_calls} 个 tool_calls，通过 {n_calls - n_bad}，拒绝 {n_bad}")
    return n_bad


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(1 if self_test() else 0)
    if "--check-log" in sys.argv:
        sys.exit(1 if check_log(sys.argv[sys.argv.index("--check-log") + 1]) else 0)
    print(__doc__)
