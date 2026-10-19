#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_stats.py · 第7课 T2.5 随机性审计统计（P19–P20）
从 logs/plan_log_G42.jsonl 按（指令原文, 温度）过滤出各 10 次审计样本，计算：
- 一致率＝最常见步骤序列出现次数／10（只比工具名序列，参数差异记变体）
- 变体数＝不同工具名序列个数（含参数变体明细）
- 三问分类（0.8 档前 3 次，按预注册口径）：
  A 序列与参数全同 / B 序列同、参数或文字异 / C 序列不同
- 用量合计（prompt/completion tokens，P5 纪律③每日看用量）
用法：python3 audit_stats.py "指令原文" [温度] [--three]
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG_PATH = HERE / "logs" / "plan_log_G42.jsonl"


def canon(args):
    return json.dumps(args, sort_keys=True, ensure_ascii=False)


def load_runs(instruction, temperature=None):
    runs = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec.get("instruction") != instruction:
            continue
        if temperature is not None and rec.get("temperature") != temperature:
            continue
        if "error" in rec or not rec.get("tool_calls"):
            continue   # 报错/拒绝样本不进一致率统计（另有处理）
        runs.append(rec)
    return sorted(runs, key=lambda r: r["ts"])


def cell_report(instruction, temperature, n_expect=10):
    runs = load_runs(instruction, temperature)
    if len(runs) != n_expect:
        print(f"[warn] {temperature} 档样本 {len(runs)} 次（期望 {n_expect}）")
    if not runs:
        return None, runs
    seqs = [tuple(tc["name"] for tc in r["tool_calls"]) for r in runs]
    counts = Counter(seqs)
    most, most_n = counts.most_common(1)[0]
    variants = sorted(set(seqs), key=lambda s: (-counts[s], s))
    print(f"\n== 指令 {instruction!r}  temp={temperature}  n={len(runs)}")
    print(f"   一致率 = {most_n}/{len(runs)}（最常见序列 {list(most)}）")
    print(f"   变体数 = {len(variants)}")
    for s in variants:
        args_uniq = sorted({canon(tc["arguments"]) for r in runs
                            for tc in r["tool_calls"]
                            if tuple(t["name"] for t in r["tool_calls"]) == s})
        tag = " ← 最常见" if s == most else ""
        print(f"   {counts[s]:>2}× {list(s)}{tag}")
        if len(args_uniq) > 1:
            print(f"      参数变体 {len(args_uniq)} 种：")
            for a in args_uniq:
                print(f"        {a}")
    return (most_n, len(runs), len(variants), counts), runs


def classify_three(runs):
    """0.8 档前 3 次（预注册口径）：A 序列与参数全同（文字亦一致）/ B 序列同、参数或文字异 / C 序列不同。"""
    first3 = runs[:3]
    sigs = []
    for r in first3:
        seq = tuple(tc["name"] for tc in r["tool_calls"])
        args = tuple(canon(tc["arguments"]) for tc in r["tool_calls"])
        text = (r.get("content") or "").strip()
        sigs.append((seq, args, text))
    seqs = {s[0] for s in sigs}
    if len(seqs) == 1 and len({s[1] for s in sigs}) == 1 and len({s[2] for s in sigs}) == 1:
        verdict = "A"
    elif len(seqs) == 1:
        verdict = "B"
    else:
        verdict = "C"
    print(f"\n三问（0.8 档前 3 次）：序列 {len(seqs)} 种 → 分类 {verdict}")
    for i, (seq, args, text) in enumerate(sigs, 1):
        print(f"   第{i}问 序列={list(seq)} args={list(args)} 文字={text!r}")
    return verdict


def main():
    instruction = sys.argv[1]
    temps = [float(t) for t in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2] not in ("--three",) else [0.2, 0.8]
    rows = {}
    for t in temps:
        res, runs = cell_report(instruction, t)
        if res:
            rows[t] = res
    if "--three" in sys.argv:
        runs08 = load_runs(instruction, 0.8)
        if runs08:
            classify_three(runs08)
    # 用量合计
    tot = Counter()
    for r in load_runs(instruction):
        u = r.get("usage") or {}
        tot["prompt"] += u.get("prompt_tokens", 0)
        tot["completion"] += u.get("completion_tokens", 0)
    print(f"\n用量合计：prompt {tot['prompt']} / completion {tot['completion']} tokens")


if __name__ == "__main__":
    main()
