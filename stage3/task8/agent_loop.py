#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""agent_loop.py · 第8课 规划-审计-执行状态机（task8.pptx P3/P9/P15）

五态：IDLE → PLANNING → AUDITING → EXECUTING → REPORTING → IDLE
三条出口（全部通向有据报告，P3）：拒绝（审计不过，携证据）／完成（全部步骤执行）／超限（重规划 >2）
纪律：
  - LLM 绝不直连电机：认知层输出提案，物理执行权在审计层之后（P3）。
  - 一条不过整案拒绝，不许半案执行（P9）。
  - 白名单前置（P4）：AUDITING 先过第7课 schema_check（编造工具/参数形态在前），再过四规则 audit（可行性）——
    进入 EXECUTING 前提＝schema 通过 且 audit 全部通过（《接口契约表》audit 行）。
  - 重规划上限 ≤2（P18 三代价）；--unbounded-replan＝突袭模式：拿掉上限，拒绝/失败均回注再规划，
    观察「PLANNING → 拒绝 → 回注 → PLANNING → …」循环（课堂以 Ctrl+C 终止实记，本机以 --max-loops 兜底）。
  - --no-audit（关审计配置）仅干跑，永不接实车（P17）。
  - 契约名（《接口契约表》）：订阅 /agent/instruction；发布 /agent/plan_events（JSON，type ∈ {plan, audit, exec, report}）。

LLM 调用：复用第7课 llm_planner 口径（本机三坑已修复：密钥文件 ~/.llm_key_t7.txt 缺省、剔除 socks 代理、
Accept-Encoding: identity——见第7课预注册单变更登记 #3/#4；值永不打印）。

用法：
  python3 agent_loop.py --dry-run --temperature 0.2 "去门口"                    # 真 LLM（干跑）
  python3 agent_loop.py --dry-run --plan-file plan.json                          # 预置 tool_calls（无 LLM）
  python3 agent_loop.py --dry-run --no-audit --temperature 0.2 "..."             # 关审计（仅干跑！）
  python3 agent_loop.py --dry-run --temperature 0.2 --unbounded-replan "..."     # 突袭（P18，课堂 Ctrl+C）
  python3 agent_loop.py --self-test                                              # 状态机冒烟七例（无 LLM）

变更登记 2026-10-19：第8课 T1.3 创建（Claude 起草；P13 案例②：未采用「while not ok 无限重试」，采用计数器 ≤2）。
变更登记 2026-10-19 第2次：AUDITING 接入 schema_check 驻场（P4 白名单前置）；新增 --unbounded-replan/--max-loops
（突袭模式，P18）；LLM 调用对齐第7课三坑修复口径与 call_llm(client, model, instruction, temperature) 新签名。
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "task7_loadLLM"))
sys.path.insert(0, str(HERE))
from plan_auditor import PlanAuditor  # noqa: E402
from schema_check import schema_check  # noqa: E402  （第7课冻结版，白名单关卡①＋jsonschema 关卡②）

LOG_PATH = HERE / "logs" / "audit_log_G42.jsonl"
MAX_REPLAN = 2  # 重规划上限（P3/P18）

LIMITS = [
    "未验证假设：孪生真执行链缺物理接触与打滑（第4课能力边界声明口径）",
    "过期风险：τ 三档为第6课占位值（E3，待本组观测改写）",
    "资源：电量＝孪生占位 82%（实车＝底盘遥测）",
]


def emit(event_type, payload):
    """/agent/plan_events 干跑实现：打印契约事件并返回记录 dict。"""
    rec = {"ts": datetime.now().astimezone().isoformat(timespec="seconds"),
           "type": event_type, **payload}
    print(f"[plan_events] {json.dumps(rec, ensure_ascii=False)}")
    return rec


def report_three_parts(result, evidence, extra=None):
    """三段式汇报（P5）：结果／证据／局限。"""
    parts = {"结果": result, "证据": evidence, "局限": LIMITS + (extra or [])}
    print("\n=== REPORTING 三段式汇报 ===")
    for k, v in parts.items():
        print(f"【{k}】{v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}")
    return parts


def run_loop(planner, executor, auditor, dry_run=True, no_audit=False,
             replan_cap=MAX_REPLAN, unbounded_replan=False, max_loops=None):
    """状态机（P9 模板填空）：AUDITING 一条不过整案拒绝；EXECUTING 失败→重规划 ≤2（或突袭无界）。
    planner(feedback=None)：重规划/突袭回注时把上一次拒绝/失败证据喂回（P18「结果回注 LLM 上下文」）。"""
    state, replan_count, plan, evidence, outcome = "IDLE", 0, None, [], "完成"
    loop_count = 0  # PLANNING 轮数＝突袭记录「循环次数/调用计数」
    pending_feedback = None
    while True:
        if state == "IDLE":
            state = "PLANNING"
        elif state == "PLANNING":
            if max_loops is not None and loop_count >= max_loops:  # 突袭人工打断（P18 演示口径）
                outcome = "超限"
                report_three_parts(
                    "超限", {"循环次数": loop_count, "调用计数": loop_count,
                             "终止方式": f"人工打断（--max-loops={max_loops}；课堂以 Ctrl+C 实记）"},
                    [f"重规划上限 {MAX_REPLAN} 次的辩护：给恢复一次机会、给失控一个上限、保护额度（P18 三代价）"])
                state = "REPORTING"
                continue
            loop_count += 1
            plan = planner(pending_feedback)
            pending_feedback = None
            emit("plan", {"tool_calls": plan, "loop": loop_count})
            state = "EXECUTING" if no_audit else "AUDITING"  # 关审计：仅干跑（P17）
        elif state == "AUDITING":
            # 白名单前置（P4）：schema_check 驻场（形态）→ audit 四规则（可行性）
            results = []
            for c in plan:
                ok_s, msg_s = schema_check(c)
                if not ok_s:
                    results.append((False, f"[schema｜白名单/参数] {msg_s}"))
                    continue
                ok_a, msg_a = auditor.audit(c)
                results.append((ok_a, msg_a))
            for c, (ok, reason) in zip(plan, results):
                emit("audit", {"call": c, "ok": ok, "reason": reason})
            if all(ok for ok, _ in results):  # 全部通过才进执行（接口契约表 audit 行）
                state = "EXECUTING"
            else:
                outcome = "拒绝"
                evidence = [r for ok, r in results if not ok]
                if unbounded_replan:  # 突袭（P18）：拒绝→回注→再规划，API 计数持续增加
                    replan_count += 1
                    pending_feedback = "上次计划被审计拒绝：" + "；".join(evidence)
                    state = "PLANNING"
                else:  # 整案拒绝，携证据（P9）
                    report_three_parts("拒绝", {"规则编号与数值": evidence})
                    state = "REPORTING"
        elif state == "EXECUTING":
            for call in plan:
                res = executor(call)  # 干跑：打印；拆封后：navigate_to 服务
                emit("exec", {"call": call, "ok": res.get("ok")})
                if not res.get("ok"):
                    replan_count += 1
                    if not unbounded_replan and replan_count > replan_cap:
                        outcome = "超限"
                        report_three_parts(
                            "超限", {"重规划次数": replan_count - 1, "最后失败": call},
                            [f"重规划上限 {MAX_REPLAN} 次的辩护：给恢复一次机会、给失控一个上限、保护额度（P18 三代价）"])
                        state = "REPORTING"
                        break
                    pending_feedback = f"上次执行失败: {call}"  # 回注（P3/P18）
                    state = "PLANNING"  # 有界重规划（≤2）或突袭无界
                    break
            else:  # 全部步骤执行成功
                outcome = "完成"  # 突袭回注后改口成功：出口如实归「完成」（2026-10-19 突袭真跑暴露：此前残留「拒绝」）
                report_three_parts("完成", {"执行步骤数": len(plan)})
                state = "REPORTING"
        elif state == "REPORTING":
            emit("report", {"result": outcome, "loop_count": loop_count, "replan_count": replan_count})
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with LOG_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(
                    {"ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                     "result": outcome, "evidence": evidence,
                     "replan_count": replan_count, "loop_count": loop_count},
                    ensure_ascii=False) + "\n")
            return {"result": outcome, "replan_count": replan_count,
                    "loop_count": loop_count, "evidence": evidence}
        else:
            raise ValueError(f"未知状态: {state}")


# ---------- 干跑执行器 ----------

def dry_executor(call):
    print(f"[EXECUTING·干跑] {call['name']}({json.dumps(call['arguments'], ensure_ascii=False)})  — 只打印，不调服务（P9）")
    return {"ok": True}


# ---------- 真 LLM 规划（第7课 llm_planner，本机三坑已修复口径） ----------

def llm_planner_fn(instruction, temperature):
    import llm_planner
    from openai import OpenAI
    llm_planner.sanitize_proxies()
    api_key, base_url, model = llm_planner.resolve_env()
    client = OpenAI(base_url=base_url, api_key=api_key,
                    default_headers={"Accept-Encoding": "identity"})  # httpx2 brotli 缺陷绕开
    try:
        res = llm_planner.call_llm(client, model, instruction, temperature)
    except Exception as e:
        print(f"[PLANNING 失败] {type(e).__name__}: {e}")
        sys.exit(2)
    return res["tool_calls"]


# ---------- 冒烟测试（--self-test，无 LLM） ----------

class FakePlanner:
    def __init__(self, plans, repeat=False):
        self.plans = list(plans)
        self.last = None
        self.repeat = repeat

    def __call__(self, feedback=None):
        if self.plans:
            self.last = self.plans.pop(0)
            return self.last
        return self.last if self.repeat else []


class FakeExecutor:
    """按配置对第 n 次执行注入失败。"""

    def __init__(self, fail_at=(), calls=None):
        self.fail_at = set(fail_at)
        self.calls = calls if calls is not None else []

    def __call__(self, call):
        self.calls.append(call)
        n = len(self.calls)
        ok = n not in self.fail_at
        print(f"[EXECUTING·冒烟] 第{n}次 {call['name']}({json.dumps(call['arguments'], ensure_ascii=False)}) ok={ok}")
        return {"ok": ok}


def smoke_tests():
    good1 = {"name": "navigate_to", "arguments": {"x": 8.60, "y": 5.20, "label": "door"}}
    good2 = {"name": "navigate_to", "arguments": {"x": 0.90, "y": 2.00, "label": "charger"}}
    bad = {"name": "navigate_to", "arguments": {"x": 50, "y": 50}}
    speed = {"name": "navigate_to", "arguments": {"x": 8.60, "y": 5.20, "speed": 5.0}}
    print("\n--- 冒烟(a) 全可行 → EXECUTING → 完成（重规划 0） ---")
    r1 = run_loop(FakePlanner([[good1, good2]]), FakeExecutor(), PlanAuditor())
    assert r1["result"] == "完成" and r1["replan_count"] == 0
    print("\n--- 冒烟(b) 一条不过 → 整案拒绝（第二条不执行） ---")
    ex = FakeExecutor()
    r2 = run_loop(FakePlanner([[bad, good1]]), ex, PlanAuditor())
    assert r2["result"] == "拒绝", f"整案拒绝出口: {r2['result']}"
    assert len(ex.calls) == 0, "整案拒绝：不许半案执行（第二条不得执行）"
    print("\n--- 冒烟(c) 执行失败 1 次 → 重规划 → 完成 ---")
    ex = FakeExecutor(fail_at={1})
    r3 = run_loop(FakePlanner([[good1], [good1]]), ex, PlanAuditor())
    assert r3["replan_count"] == 1
    print("\n--- 冒烟(d) 连续失败 → 超限出口（重规划恰好 2 次后报告） ---")
    ex = FakeExecutor(fail_at={1, 2, 3})
    r4 = run_loop(FakePlanner([[good1], [good1], [good1]]), ex, PlanAuditor())
    assert r4["result"] == "超限", f"超限出口: {r4['result']}"
    assert len(ex.calls) == 3, "最多 1 次初试 + 2 次重规划"
    print("\n--- 冒烟(e) --no-audit 关审计：坏调用直达 EXECUTING（仅干跑） ---")
    ex = FakeExecutor()
    r5 = run_loop(FakePlanner([[bad]]), ex, PlanAuditor(), no_audit=True)
    assert len(ex.calls) == 1, "关审计配置：审计被跳过（对照实验关审计列口径）"
    print("\n--- 冒烟(f) speed 参数 → schema 前置拦截（T4 预判：白名单/schema） ---")
    r6 = run_loop(FakePlanner([[speed]]), FakeExecutor(), PlanAuditor())
    assert r6["result"] == "拒绝" and any("schema" in e for e in r6["evidence"]), r6["evidence"]
    print("\n--- 冒烟(g) 突袭：--unbounded-replan＋max_loops=5 → 循环 5 轮后人工打断口径超限 ---")
    r7 = run_loop(FakePlanner([[bad]], repeat=True), FakeExecutor(), PlanAuditor(),
                  unbounded_replan=True, max_loops=5)
    assert r7["result"] == "超限" and r7["loop_count"] == 5, (r7["result"], r7["loop_count"])
    print("\n冒烟七例全部通过 ✅")


def main():
    ap = argparse.ArgumentParser(description="第8课 规划-审计-执行状态机")
    ap.add_argument("--dry-run", action="store_true", help="EXECUTING 只打印（必带，P9 干跑纪律）")
    ap.add_argument("--no-audit", action="store_true", help="关审计（仅干跑，永不接实车，P17）")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--plan-file", help="预置 tool_calls JSON 文件（跳过 LLM）")
    ap.add_argument("--unbounded-replan", action="store_true", help="突袭模式：拿掉 ≤2 上限（P18，课堂 Ctrl+C）")
    ap.add_argument("--replan-cap", type=int, default=MAX_REPLAN)
    ap.add_argument("--max-loops", type=int, default=None, help="突袭兜底轮数（默认 8）")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("instruction", nargs="*")
    args = ap.parse_args()

    if args.self_test:
        smoke_tests()
        return
    if not args.dry_run:
        print("[纪律] 必须带 --dry-run（P9）：本课干跑不调服务；拆封后由组员切换 execute 实现。")
        sys.exit(1)

    max_loops = args.max_loops
    if args.unbounded_replan and max_loops is None:
        max_loops = 8
    auditor = PlanAuditor()
    if args.plan_file:
        plan = json.loads(Path(args.plan_file).read_text(encoding="utf-8"))
        planner = FakePlanner([plan], repeat=args.unbounded_replan)
    else:
        instruction = " ".join(args.instruction)
        if not instruction:
            print("[用法] 需指令文本或 --plan-file")
            sys.exit(1)

        def planner(feedback=None):  # 回注（P18）：上次拒绝/失败证据拼进 user 消息
            ins = instruction if not feedback else f"{instruction}\n[上一次执行反馈] {feedback}"
            return llm_planner_fn(ins, args.temperature)
    run_loop(planner, dry_executor, auditor, dry_run=True, no_audit=args.no_audit,
             replan_cap=args.replan_cap, unbounded_replan=args.unbounded_replan, max_loops=max_loops)


if __name__ == "__main__":
    main()
