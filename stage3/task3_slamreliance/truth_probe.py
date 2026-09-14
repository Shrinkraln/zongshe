#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""truth_probe.py —— 第3课真值探针（PPT P16 引用；平台仓库未提供，本组自写）。

作用：查询静态世界网关 GET /health 的 robot_truth（真值位姿），
     作为《定位误差统计表》孪生版真值列的唯一来源。
契约：nav_gateway.py /health 返回
     {"robot_truth": {"x": .., "y": .., "theta_deg": ..}, "tick_n": .., "uptime_s": ..}
纪律：两条证据链独立——先记 AMCL 估计，再运行本脚本读真值，互不参照。

用法：
  python truth_probe.py --host <笔记本IP>            # 默认端口 8000
  python truth_probe.py --host 127.0.0.1 --port 8000
仅用 stdlib（urllib），树莓派无需额外 pip 依赖。
"""

import argparse
import json
import urllib.request


def probe(host: str, port: int) -> dict:
    url = f"http://{host}:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise SystemExit(f"[truth_probe] 查询失败 {url}: {e}\n"
                         f"  检查：网关是否在跑 nav_gateway.py？IP/端口是否正确？")


def main() -> None:
    ap = argparse.ArgumentParser(description="查询静态世界网关真值位姿（GET /health robot_truth）")
    ap.add_argument("--host", required=True, help="笔记本（网关）IP")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    data = probe(args.host, args.port)
    truth = data.get("robot_truth")
    if truth is None:
        raise SystemExit(f"[truth_probe] 响应无 robot_truth 字段：{json.dumps(data, ensure_ascii=False)}")

    # 打印便于直接抄录进统计表的真值行
    print(f"模式={data.get('mode')} seed={data.get('seed')} slip={data.get('slip')} "
          f"tick_n={data.get('tick_n')}")
    print(f"真值 (x, y, θ°) = ({truth['x']:.3f}, {truth['y']:.3f}, {truth['theta_deg']:.1f})")
    print("抄录进统计表【真值(x,y,θ)】列；与 AMCL 估计分别记录、互不参照。")


if __name__ == "__main__":
    main()
