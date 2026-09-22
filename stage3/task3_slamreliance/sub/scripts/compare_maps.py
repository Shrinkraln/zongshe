#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compare_maps.py —— 第3课 建图与真值图叠合对照（互评预演/验收用）。

用法：python3 compare_maps.py <真值图.yaml> <建图.yaml> [--out 叠合图.png]
例：  python3 compare_maps.py ~/sim_ops/map_gt.yaml ~/sim_ops/sim_G42.yaml

原理：两张图的形状/origin/resolution 不同（SLAM 图包围盒更大、原点漂移），
      先按各自 yaml 元数据把建图重采样到真值图网格（世界坐标对齐），再逐格比对。
口径：
  已探索 = 建图格 ≠ 205（unknown）；
  墙命中 = 真值墙格 0.10m 半径内有建图墙（24 线稀疏雷达允许 1~2 格偏差）→ 缺口 = 1−命中率；
  假墙   = 真值自由区（距真值墙 >0.10m）内建图画出墙（重影/鬼影/残影的量化）；
  另输出各区域统计与叠合 PNG（黑＝真值图，橙＝建图）。
依赖：PIL + PyYAML + numpy（ROS2 humble 环境自带）。
"""

import argparse
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

UNKNOWN = 205
OCC_THRESH = 128      # 0~127=墙，>127=自由/未知
NEAR_TOL = 0.10       # 墙命中容忍半径 (m)


def load_map(yaml_path: str):
    """返回 (grid HxW uint8, meta) —— 按 yaml 的 image 字段读 pgm。"""
    yp = Path(yaml_path).expanduser()
    meta = yaml.safe_load(yp.read_text(encoding="utf-8"))
    img = Image.open((yp.parent / meta["image"]).expanduser()).convert("L")
    grid = np.frombuffer(img.tobytes(), dtype=np.uint8).reshape(img.size[1], img.size[0])
    return grid, meta


def dist_to(coords_y, coords_x, shape):
    """每个格中心到给定点集最近点的距离（格距单位，未乘分辨率）。"""
    d2 = np.full(shape, np.inf)
    gy = np.arange(shape[0])[:, None]
    gx = np.arange(shape[1])[None, :]
    for cy, cx in zip(coords_y, coords_x):
        d2 = np.minimum(d2, (gy - cy) ** 2 + (gx - cx) ** 2)
    return np.sqrt(d2)


def main():
    ap = argparse.ArgumentParser(description="建图与真值图叠合对照（互评三缺陷量化）")
    ap.add_argument("gt_yaml", help="真值图 yaml（make_gt_map 产出）")
    ap.add_argument("slam_yaml", help="建图 yaml（map_saver 产出）")
    ap.add_argument("--out", default=None, help="叠合 PNG 输出路径（默认 <建图名>_overlay.png）")
    args = ap.parse_args()

    gt, gtm = load_map(args.gt_yaml)
    sm, smm = load_map(args.slam_yaml)
    print(f"真值图: {gt.shape[1]}x{gt.shape[0]}px res={gtm['resolution']} origin={gtm['origin'][:2]}")
    print(f"建图:   {sm.shape[1]}x{sm.shape[0]}px res={smm['resolution']} origin={smm['origin'][:2]}")

    # ---- 世界坐标对齐：把建图重采样到真值图网格（最近邻） ----
    gres, sres = gtm["resolution"], smm["resolution"]
    gox, goy = gtm["origin"][0], gtm["origin"][1]
    sox, soy = smm["origin"][0], smm["origin"][1]
    gH, gW = gt.shape
    sH, sW = sm.shape
    gwy = goy + (gH - np.arange(gH) - 0.5) * gres      # 真值各行格中心世界 y
    gwx = gox + (np.arange(gW) + 0.5) * gres           # 真值各列格中心世界 x
    swy0 = soy + (sH - 0.5) * sres                     # 建图顶行格中心世界 y
    swx0 = sox + 0.5 * sres                            # 建图首列格中心世界 x
    si = np.clip(((swy0 - gwy[:, None]) / sres).round().astype(int), 0, sH - 1)
    sj = np.clip(((gwx[None, :] - swx0) / sres).round().astype(int), 0, sW - 1)
    aligned = sm[si, sj]                               # 建图在真值网格上的取值

    gt_wall = gt < OCC_THRESH
    sm_wall = aligned < OCC_THRESH
    explored = aligned != UNKNOWN

    # ---- 统计 ----
    n_wall = int(gt_wall.sum())
    n_explored = int(explored.sum())
    n_arena = int(gt.size)
    n_wall_explored = int((gt_wall & explored).sum())

    # 墙命中：真值墙格 0.10m 内有建图墙（对每格找最近建图墙）
    sy, sx = np.nonzero(sm_wall)
    d_to_sm_wall = dist_to(sy, sx, gt.shape) * gres if len(sy) else np.full(gt.shape, np.inf)
    wall_hit = gt_wall & explored & (d_to_sm_wall <= NEAR_TOL)
    n_wall_hit = int(wall_hit.sum())

    # 假墙：真值自由区（距真值墙 >0.10m）内建图画出墙
    gy, gx = np.nonzero(gt_wall)
    d_to_gt_wall = dist_to(gy, gx, gt.shape) * gres if len(gy) else np.full(gt.shape, np.inf)
    ghost = (~gt_wall) & (d_to_gt_wall > NEAR_TOL) & explored & sm_wall
    n_ghost = int(ghost.sum())

    print(f"\n===== 对照统计（真值网格口径，容忍 {NEAR_TOL*100:.0f}cm） =====")
    print(f"场地覆盖: 已探索 {n_explored}/{n_arena} ({n_explored/n_arena*100:.1f}%)")
    print(f"真值墙格: {n_wall}   其中建图已探索: {n_wall_explored} ({n_wall_explored/max(n_wall,1)*100:.1f}%)")
    print(f"墙命中: {n_wall_hit}/{n_wall}  →  缺口率 {(1 - n_wall_hit/max(n_wall,1))*100:.1f}%"
          f"（含未探索墙段；24线稀疏雷达存在天然缺口属平台特性）")
    print(f"假墙格(自由区重影/鬼影): {n_ghost}  (占已探索 {n_ghost/max(n_explored,1)*100:.2f}%)")
    print("判读: 假墙成线状且平行贴近真值墙=重影；游离成团=鬼影/残影；墙命中率低=断裂。")

    # ---- 叠合图：黑＝真值图墙，橙＝建图墙 ----
    canvas = np.full(gt.shape + (3,), 255, dtype=np.uint8)
    canvas[sm_wall] = (255, 140, 0)   # 橙=建图
    canvas[gt_wall] = (0, 0, 0)       # 黑=真值（盖在橙上）
    out = Path(args.out) if args.out else Path(str(Path(args.slam_yaml).with_suffix("")) + "_overlay.png")
    Image.fromarray(canvas).save(out)
    print(f"\n叠合图已存: {out}（黑＝真值图，橙＝建图；橙贴黑＝重影，黑孤悬＝缺口，橙游离＝鬼影）")


if __name__ == "__main__":
    main()
