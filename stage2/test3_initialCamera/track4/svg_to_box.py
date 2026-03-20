#!/usr/bin/env python3
"""
svg_to_box_sdf_v2.py
将 SVG 赛道路径生成纯 box 的 SDF，结构与官方 maze.sdf 完全一致：
  - 一个 model 包含多个 link
  - 每个 link = 一个 box collision + 一个 box visual
  - 无 mesh, 无 Sensors 插件

用法:
  python3 svg_to_box_sdf_v2.py track.svg
"""

import xml.etree.ElementTree as ET
import math, sys, os, re

try:
    import numpy as np
except ImportError:
    sys.exit("[ERROR] 需要 numpy")

# ═══════════════════════════════════════════════════════════
#  参数
# ═══════════════════════════════════════════════════════════

TURTLEBOT4_WIDTH   = 0.351
TRACK_WIDTH_RATIO  = 4.0
TARGET_TRACK_WIDTH = TURTLEBOT4_WIDTH * TRACK_WIDTH_RATIO

MANUAL_SCALE  = 58.20
OFFSET_X      = -3.578
OFFSET_Y      =  4.800

WALL_HEIGHT   = 0.40
WALL_THICK    = 0.05
BEZIER_STEPS  = 12
BOX_OVERLAP   = 0.02
DEBUG         = True

# ═══════════════════════════════════════════════════════════
# SVG 解析
# ═══════════════════════════════════════════════════════════

def strip_ns(tag):
    return tag.split('}', 1)[-1] if '}' in tag else tag

def tokenize(d):
    return re.findall(
        r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', d)

def cubic_b(p0, p1, p2, p3, n):
    pts = []
    for k in range(n + 1):
        t = k / n; mt = 1 - t
        x = mt**3*p0[0]+3*mt**2*t*p1[0]+3*mt*t**2*p2[0]+t**3*p3[0]
        y = mt**3*p0[1]+3*mt**2*t*p1[1]+3*mt*t**2*p2[1]+t**3*p3[1]
        pts.append((x, y))
    return pts

def quad_b(p0, p1, p2, n):
    pts = []
    for k in range(n + 1):
        t = k / n; mt = 1 - t
        x = mt**2*p0[0]+2*mt*t*p1[0]+t**2*p2[0]
        y = mt**2*p0[1]+2*mt*t*p1[1]+t**2*p2[1]
        pts.append((x, y))
    return pts

def parse_path(d_str):
    tokens = tokenize(d_str)
    idx = 0
    def is_cmd(t): return t and re.match(r'[MmLlHhVvCcSsQqTtAaZz]$', t)
    def rf():
        nonlocal idx
        if idx >= len(tokens) or is_cmd(tokens[idx]): return None
        v = float(tokens[idx]); idx += 1; return v

    subpaths, cur = [], []
    cx = cy = sx = sy = 0.0
    last_cp = None; cmd = None

    while idx < len(tokens):
        t = tokens[idx]
        if is_cmd(t):
            cmd = t; idx += 1
            if cmd in 'Zz':
                if cur: cur.append((sx, sy))
                subpaths.append(cur); cur=[]; cx,cy=sx,sy; cmd=None; continue
            last_cp = None; continue
        if cmd is None: idx += 1; continue

        if   cmd == 'M': x,y=rf(),rf(); subpaths.append(cur) if cur else None; cur=[(x,y)]; cx,cy=x,y; sx,sy=x,y; cmd='L'
        elif cmd == 'm': dx,dy=rf(),rf(); subpaths.append(cur) if cur else None; cx+=dx;cy+=dy; cur=[(cx,cy)]; sx,sy=cx,cy; cmd='l'
        elif cmd == 'L': x,y=rf(),rf(); cx,cy=x,y; cur.append((cx,cy))
        elif cmd == 'l': dx,dy=rf(),rf(); cx+=dx;cy+=dy; cur.append((cx,cy))
        elif cmd == 'H': cx=rf(); cur.append((cx,cy))
        elif cmd == 'h': cx+=rf(); cur.append((cx,cy))
        elif cmd == 'V': cy=rf(); cur.append((cx,cy))
        elif cmd == 'v': cy+=rf(); cur.append((cx,cy))
        elif cmd == 'C':
            x1,y1=rf(),rf();x2,y2=rf(),rf();x,y=rf(),rf()
            pts=cubic_b((cx,cy),(x1,y1),(x2,y2),(x,y),BEZIER_STEPS)
            cur.extend(pts[1:]);last_cp=(x2,y2);cx,cy=x,y
        elif cmd == 'c':
            x1,y1=cx+rf(),cy+rf();x2,y2=cx+rf(),cy+rf();dx,dy=rf(),rf()
            nx,ny=cx+dx,cy+dy
            pts=cubic_b((cx,cy),(x1,y1),(x2,y2),(nx,ny),BEZIER_STEPS)
            cur.extend(pts[1:]);last_cp=(x2,y2);cx,cy=nx,ny
        elif cmd == 'S':
            rx=2*cx-last_cp[0] if last_cp else cx;ry=2*cy-last_cp[1] if last_cp else cy
            x2,y2=rf(),rf();x,y=rf(),rf()
            pts=cubic_b((cx,cy),(rx,ry),(x2,y2),(x,y),BEZIER_STEPS)
            cur.extend(pts[1:]);last_cp=(x2,y2);cx,cy=x,y
        elif cmd == 's':
            rx=2*cx-last_cp[0] if last_cp else cx;ry=2*cy-last_cp[1] if last_cp else cy
            x2,y2=cx+rf(),cy+rf();dx,dy=rf(),rf();nx,ny=cx+dx,cy+dy
            pts=cubic_b((cx,cy),(rx,ry),(x2,y2),(nx,ny),BEZIER_STEPS)
            cur.extend(pts[1:]);last_cp=(x2,y2);cx,cy=nx,ny
        elif cmd == 'Q':
            x1,y1=rf(),rf();x,y=rf(),rf()
            pts=quad_b((cx,cy),(x1,y1),(x,y),BEZIER_STEPS)
            cur.extend(pts[1:]);last_cp=(x1,y1);cx,cy=x,y
        elif cmd == 'q':
            x1,y1=cx+rf(),cy+rf();dx,dy=rf(),rf();nx,ny=cx+dx,cy+dy
            pts=quad_b((cx,cy),(x1,y1),(nx,ny),BEZIER_STEPS)
            cur.extend(pts[1:]);last_cp=(x1,y1);cx,cy=nx,ny
        elif cmd == 'T':
            rx=2*cx-last_cp[0] if last_cp else cx;ry=2*cy-last_cp[1] if last_cp else cy
            x,y=rf(),rf();pts=quad_b((cx,cy),(rx,ry),(x,y),BEZIER_STEPS)
            cur.extend(pts[1:]);last_cp=(rx,ry);cx,cy=x,y
        elif cmd == 't':
            rx=2*cx-last_cp[0] if last_cp else cx;ry=2*cy-last_cp[1] if last_cp else cy
            dx,dy=rf(),rf();nx,ny=cx+dx,cy+dy;pts=quad_b((cx,cy),(rx,ry),(nx,ny),BEZIER_STEPS)
            cur.extend(pts[1:]);last_cp=(rx,ry);cx,cy=nx,ny
        elif cmd == 'A': [rf() for _ in range(5)];x,y=rf(),rf();cx,cy=x,y;cur.append((cx,cy))
        elif cmd == 'a': [rf() for _ in range(5)];dx,dy=rf(),rf();cx+=dx;cy+=dy;cur.append((cx,cy))
        elif cmd in 'Zz':
            if cur: cur.append(cur[0])
            subpaths.append(cur);cur=[];cx,cy=sx,sy;idx+=1
        else: idx+=1

    if cur and len(cur)>1: subpaths.append(cur)
    return [sp for sp in subpaths if len(sp)>=2]

def estimate_track_gap(pts1, pts2):
    sample = pts1[::max(1, len(pts1)//30)]
    arr2 = np.array(pts2)
    dists = [float(np.min(np.linalg.norm(arr2 - np.array(p), axis=1))) for p in sample]
    return float(np.median(dists))

# ═══════════════════════════════════════════════════════════
# 路径转世界坐标
# ═══════════════════════════════════════════════════════════

def path_to_world_coords(pts_mm, scale):
    """将SVG mm坐标转为Gazebo世界坐标，返回去重后的numpy数组"""
    raw = np.array([(p[0]*scale + OFFSET_X, -p[1]*scale + OFFSET_Y) for p in pts_mm])
    pts_list = [raw[0]]
    for i in range(1, len(raw)):
        if np.linalg.norm(raw[i] - pts_list[-1]) > 1e-9:
            pts_list.append(raw[i])
    pts = np.array(pts_list)
    # 闭合
    if np.linalg.norm(pts[-1] - pts[0]) > 1e-9:
        pts = np.vstack([pts, pts[0:1]])
    return pts

# ═══════════════════════════════════════════════════════════
# 生成 SDF link 列表（与 maze.sdf 结构一致）
# ═══════════════════════════════════════════════════════════

def generate_wall_links(pts, wall_name, wall_height, wall_thick, overlap, color_amb, color_diff):
    """为一条路径生成多个 link，每个 link 一个 box collision + box visual"""
    links = []
    n = len(pts)
    for i in range(n - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        cz = wall_height / 2.0
        dx = x1 - x0
        dy = y1 - y0
        seg_len = math.sqrt(dx*dx + dy*dy)
        if seg_len < 1e-6:
            continue
        yaw = math.atan2(dy, dx)
        box_len = seg_len + overlap

        link_name = f'{wall_name}_{i}'
        links.append(f"""            <link name='{link_name}'>
                <pose>{cx:.6f} {cy:.6f} {cz:.4f} 0 0 {yaw:.6f}</pose>
                <collision name='{link_name}_collision'>
                    <geometry>
                        <box>
                            <size>{box_len:.6f} {wall_thick} {wall_height}</size>
                        </box>
                    </geometry>
                </collision>
                <visual name='{link_name}_visual'>
                    <geometry>
                        <box>
                            <size>{box_len:.6f} {wall_thick} {wall_height}</size>
                        </box>
                    </geometry>
                    <material>
                        <ambient>{color_amb}</ambient>
                        <diffuse>{color_diff}</diffuse>
                        <specular>0.1 0.1 0.1 1</specular>
                    </material>
                </visual>
            </link>""")

    if DEBUG:
        print(f"[DEBUG] {wall_name}: {len(links)} 个 link", file=sys.stderr)
    return links

# ═══════════════════════════════════════════════════════════
# SDF 输出
# ═══════════════════════════════════════════════════════════

def write_sdf(out_dir, outer_links, inner_links, world_name="custom_track_lidar"):
    """生成与 maze.sdf 结构完全一致的 SDF"""

    outer_links_str = "\n".join(outer_links)
    inner_links_str = "\n".join(inner_links)

    sdf = f"""<?xml version="1.0"?>
<sdf version='1.8'>
    <world name='{world_name}'>
        <physics name='1ms' type='ignored'>
            <max_step_size>0.003</max_step_size>
            <real_time_factor>1</real_time_factor>
            <real_time_update_rate>1000</real_time_update_rate>
        </physics>
        <plugin name='ignition::gazebo::systems::Physics' filename='ignition-gazebo-physics-system' />
        <plugin name='ignition::gazebo::systems::UserCommands' filename='ignition-gazebo-user-commands-system' />
        <plugin name='ignition::gazebo::systems::SceneBroadcaster' filename='ignition-gazebo-scene-broadcaster-system' />
        <plugin name='ignition::gazebo::systems::Contact' filename='ignition-gazebo-contact-system' />
        <light name='sun' type='directional'>
            <cast_shadows>1</cast_shadows>
            <pose>0 0 10 0 -0 0</pose>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.2 0.2 0.2 1</specular>
            <attenuation>
                <range>1000</range>
                <constant>0.90000000000000002</constant>
                <linear>0.01</linear>
                <quadratic>0.001</quadratic>
            </attenuation>
            <direction>-0.5 0.1 -0.9</direction>
            <spot><inner_angle>0</inner_angle><outer_angle>0</outer_angle><falloff>0</falloff></spot>
        </light>
        <gravity>0 0 -9.8</gravity>
        <magnetic_field>6e-06 2.3e-05 -4.2e-05</magnetic_field>
        <atmosphere type='adiabatic' />
        <scene>
            <ambient>0.4 0.4 0.4 1</ambient>
            <background>0.7 0.7 0.7 1</background>
            <shadows>1</shadows>
        </scene>
        <model name='ground_plane'>
            <static>1</static>
            <link name='link'>
                <collision name='collision'>
                    <geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>
                    <surface><friction><ode /></friction><bounce /><contact /></surface>
                </collision>
                <visual name='visual'>
                    <geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>
                    <material>
                        <ambient>0.8 0.8 0.8 1</ambient>
                        <diffuse>0.8 0.8 0.8 1</diffuse>
                        <specular>0.8 0.8 0.8 1</specular>
                    </material>
                    <plugin name='__default__' filename='__default__' />
                </visual>
            </link>
            <plugin name='__default__' filename='__default__' />
            <pose>0 0 0 0 -0 0</pose>
        </model>

        <model name='outer_wall'>
            <pose>0 0 0 0 0 0</pose>
            <static>true</static>
{outer_links_str}
        </model>

        <model name='inner_wall'>
            <pose>0 0 0 0 0 0</pose>
            <static>true</static>
{inner_links_str}
        </model>

    </world>
</sdf>
"""
    sdf_path = os.path.join(out_dir, "track.sdf")
    with open(sdf_path, 'w') as f:
        f.write(sdf)
    print(f"[OK] SDF → {sdf_path}", file=sys.stderr)
    return sdf_path

# ═══════════════════════════════════════════════════════════
#  主流程
# ═══════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("用法: python3 svg_to_box_sdf_v2.py track.svg", file=sys.stderr)
        sys.exit(1)

    svg_path = sys.argv[1]
    out_dir  = os.path.dirname(os.path.abspath(svg_path))
    os.makedirs(out_dir, exist_ok=True)

    # 1. 解析 SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()
    path_elems = []
    for elem in root.iter():
        if strip_ns(elem.tag) == 'path':
            d = elem.get('d', '')
            if d: path_elems.append((elem.get('id','?'), d))

    if len(path_elems) < 2:
        print(f"[ERROR] 需要至少 2 条 path，找到 {len(path_elems)} 条", file=sys.stderr)
        sys.exit(1)

    # 2. 解析点列表
    all_pts = []
    for pid, d in path_elems:
        subpaths = parse_path(d)
        sp = max(subpaths, key=len)
        all_pts.append((pid, sp))
        print(f"[DEBUG] path {pid}: {len(sp)} 个点", file=sys.stderr)

    # 3. 缩放
    scale = MANUAL_SCALE if MANUAL_SCALE else TARGET_TRACK_WIDTH / (estimate_track_gap(all_pts[0][1], all_pts[1][1]) * 0.001)
    actual_scale = scale * 0.001
    print(f"[DEBUG] scale = {scale}", file=sys.stderr)

    # 4. 转世界坐标
    outer_pts = path_to_world_coords(all_pts[0][1], actual_scale)
    inner_pts = path_to_world_coords(all_pts[1][1], actual_scale)

    # 5. 生成 link 列表
    outer_links = generate_wall_links(
        outer_pts, "ow", WALL_HEIGHT, WALL_THICK, BOX_OVERLAP,
        "0.85 0.15 0.15 1", "0.85 0.15 0.15 1")
    inner_links = generate_wall_links(
        inner_pts, "iw", WALL_HEIGHT, WALL_THICK, BOX_OVERLAP,
        "0.15 0.15 0.85 1", "0.15 0.15 0.85 1")

    # 6. 写 SDF
    sdf_path = write_sdf(out_dir, outer_links, inner_links)

    print("", file=sys.stderr)
    print("══════════════════════════════════════", file=sys.stderr)
    print(f" 完成！纯 box 结构，与 maze.sdf 一致", file=sys.stderr)
    print(f" 外墙: {len(outer_links)} 段", file=sys.stderr)
    print(f" 内墙: {len(inner_links)} 段", file=sys.stderr)
    print(f" 墙高: {WALL_HEIGHT}m  墙厚: {WALL_THICK}m", file=sys.stderr)
    print(f" 重叠: {BOX_OVERLAP}m", file=sys.stderr)
    print("══════════════════════════════════════", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(f"部署:", file=sys.stderr)
    print(f"  sudo cp {sdf_path} /opt/ros/humble/share/turtlebot4_ignition_bringup/worlds/custom_track_lidar.sdf", file=sys.stderr)

if __name__ == '__main__':
    main()