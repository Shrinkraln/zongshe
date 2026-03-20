#!/usr/bin/env python3
"""
svg_to_stl_sdf.py
将 Inkscape SVG 赛道路径挤出为 Collada (.dae) mesh，生成 SDF，并自动部署到 Ignition worlds 目录。

用法:
  python3 svg_to_stl_sdf.py track.svg
  → 生成 meshes/track_outer.dae、meshes/track_inner.dae
  → 自动部署 SDF 到 /opt/ros/humble/share/turtlebot4_ignition_bringup/worlds/custom_track_lidar.sdf
    （需要 sudo 权限，权限不足时自动暂存到 /tmp 并提示）

依赖: numpy (sudo apt install python3-numpy)
"""

import xml.etree.ElementTree as ET
import sys, os, re

try:
    import numpy as np
except ImportError:
    sys.exit("[ERROR] 需要 numpy: sudo apt install python3-numpy")

# ═══════════════════════════════════════════════════════════
#  参数配置
# ═══════════════════════════════════════════════════════════

TURTLEBOT4_WIDTH   = 0.351
TRACK_WIDTH_RATIO  = 4.0
TARGET_TRACK_WIDTH = TURTLEBOT4_WIDTH * TRACK_WIDTH_RATIO  # 1.404m

MANUAL_SCALE = 58.20   # mm→m 缩放比例（设为 None 则自动计算）
OFFSET_X     = -3.578  # 赛道居中 X 偏移 (m)
OFFSET_Y     =  4.800  # 赛道居中 Y 偏移 (m)

WALL_HEIGHT  = 0.35    # 墙高 (m)，高于 TurtleBot4(0.192m)
WALL_THICK   = 0.05    # 墙厚 (m)
BEZIER_STEPS = 12      # 贝塞尔曲线细分段数
DEBUG        = True

WORLD_NAME  = 'custom_track_lidar'
DEPLOY_PATH = f'/opt/ros/humble/share/turtlebot4_ignition_bringup/worlds/{WORLD_NAME}.sdf'

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
    """解析 SVG path d 属性，返回子路径点列表（mm 坐标）。"""
    tokens = tokenize(d_str)
    idx = 0

    def is_cmd(t):
        return t and re.match(r'[MmLlHhVvCcSsQqTtAaZz]$', t)

    def rf():
        nonlocal idx
        if idx >= len(tokens) or is_cmd(tokens[idx]):
            return None
        v = float(tokens[idx]); idx += 1; return v

    subpaths, cur = [], []
    cx = cy = sx = sy = 0.0
    last_cp = None
    cmd = None

    while idx < len(tokens):
        t = tokens[idx]
        if is_cmd(t):
            cmd = t; idx += 1
            if cmd in 'Zz':
                # Z 无参数，立即闭合到 M 命令记录的精确起点
                if cur:
                    cur.append((sx, sy))
                subpaths.append(cur); cur = []; cx, cy = sx, sy
                cmd = None; continue
            last_cp = None
            continue
        if cmd is None:
            idx += 1; continue

        if   cmd == 'M': x,y=rf(),rf(); subpaths.append(cur) if cur else None; cur=[(x,y)]; cx,cy=x,y; sx,sy=x,y; cmd='L'
        elif cmd == 'm': dx,dy=rf(),rf(); subpaths.append(cur) if cur else None; cx+=dx; cy+=dy; cur=[(cx,cy)]; sx,sy=cx,cy; cmd='l'
        elif cmd == 'L': x,y=rf(),rf(); cx,cy=x,y; cur.append((cx,cy))
        elif cmd == 'l': dx,dy=rf(),rf(); cx+=dx; cy+=dy; cur.append((cx,cy))
        elif cmd == 'H': cx=rf(); cur.append((cx,cy))
        elif cmd == 'h': cx+=rf(); cur.append((cx,cy))
        elif cmd == 'V': cy=rf(); cur.append((cx,cy))
        elif cmd == 'v': cy+=rf(); cur.append((cx,cy))
        elif cmd == 'C':
            x1,y1=rf(),rf(); x2,y2=rf(),rf(); x,y=rf(),rf()
            pts=cubic_b((cx,cy),(x1,y1),(x2,y2),(x,y),BEZIER_STEPS)
            cur.extend(pts[1:]); last_cp=(x2,y2); cx,cy=x,y
        elif cmd == 'c':
            x1,y1=cx+rf(),cy+rf(); x2,y2=cx+rf(),cy+rf(); dx,dy=rf(),rf()
            nx,ny=cx+dx,cy+dy
            pts=cubic_b((cx,cy),(x1,y1),(x2,y2),(nx,ny),BEZIER_STEPS)
            cur.extend(pts[1:]); last_cp=(x2,y2); cx,cy=nx,ny
        elif cmd == 'S':
            rx=2*cx-last_cp[0] if last_cp else cx; ry=2*cy-last_cp[1] if last_cp else cy
            x2,y2=rf(),rf(); x,y=rf(),rf()
            pts=cubic_b((cx,cy),(rx,ry),(x2,y2),(x,y),BEZIER_STEPS)
            cur.extend(pts[1:]); last_cp=(x2,y2); cx,cy=x,y
        elif cmd == 's':
            rx=2*cx-last_cp[0] if last_cp else cx; ry=2*cy-last_cp[1] if last_cp else cy
            x2,y2=cx+rf(),cy+rf(); dx,dy=rf(),rf(); nx,ny=cx+dx,cy+dy
            pts=cubic_b((cx,cy),(rx,ry),(x2,y2),(nx,ny),BEZIER_STEPS)
            cur.extend(pts[1:]); last_cp=(x2,y2); cx,cy=nx,ny
        elif cmd == 'Q':
            x1,y1=rf(),rf(); x,y=rf(),rf()
            pts=quad_b((cx,cy),(x1,y1),(x,y),BEZIER_STEPS)
            cur.extend(pts[1:]); last_cp=(x1,y1); cx,cy=x,y
        elif cmd == 'q':
            x1,y1=cx+rf(),cy+rf(); dx,dy=rf(),rf(); nx,ny=cx+dx,cy+dy
            pts=quad_b((cx,cy),(x1,y1),(nx,ny),BEZIER_STEPS)
            cur.extend(pts[1:]); last_cp=(x1,y1); cx,cy=nx,ny
        elif cmd == 'T':
            rx=2*cx-last_cp[0] if last_cp else cx; ry=2*cy-last_cp[1] if last_cp else cy
            x,y=rf(),rf()
            pts=quad_b((cx,cy),(rx,ry),(x,y),BEZIER_STEPS)
            cur.extend(pts[1:]); last_cp=(rx,ry); cx,cy=x,y
        elif cmd == 't':
            rx=2*cx-last_cp[0] if last_cp else cx; ry=2*cy-last_cp[1] if last_cp else cy
            dx,dy=rf(),rf(); nx,ny=cx+dx,cy+dy
            pts=quad_b((cx,cy),(rx,ry),(nx,ny),BEZIER_STEPS)
            cur.extend(pts[1:]); last_cp=(rx,ry); cx,cy=nx,ny
        elif cmd == 'A': [rf() for _ in range(5)]; x,y=rf(),rf(); cx,cy=x,y; cur.append((cx,cy))
        elif cmd == 'a': [rf() for _ in range(5)]; dx,dy=rf(),rf(); cx+=dx; cy+=dy; cur.append((cx,cy))
        else: idx += 1

    if cur and len(cur) > 1:
        subpaths.append(cur)
    return [sp for sp in subpaths if len(sp) >= 2]

def estimate_track_gap(pts1, pts2):
    """估算两条路径的中位最近距离（mm）"""
    sample = pts1[::max(1, len(pts1)//30)]
    arr2 = np.array(pts2)
    dists = [np.min(np.linalg.norm(arr2 - np.array(p), axis=1)) for p in sample]
    return float(np.median(dists))

def extrude_path_to_dae(pts_mm, scale, wall_height, wall_thick, out_path):
    """
    将闭合 2D 路径挤出为 Collada (.dae) 墙壁。
    - 路径末尾必须等于起点（由 parse_path Z 命令保证）
    - 顶点法线用前后两条边的平均（miter join）
    - 带 miter limit（超过 3 倍墙厚时改用当前边法线，防止尖角突出）
    - 挤出四个面：外侧、内侧、顶面、底面
    """
    raw = np.array([(p[0]*scale + OFFSET_X, -p[1]*scale + OFFSET_Y) for p in pts_mm])

    # 去重（保留闭合点）
    pts_list = [raw[0]]
    for i in range(1, len(raw)):
        if np.linalg.norm(raw[i] - pts_list[-1]) > 1e-9:
            pts_list.append(raw[i])
    pts = np.array(pts_list)
    n = len(pts)

    # 确保最后一点等于第一点
    if np.linalg.norm(pts[-1] - pts[0]) > 1e-9:
        pts = np.vstack([pts, pts[0:1]])
        n = len(pts)

    m_pts = n - 1  # 环上不重复点数
    half  = wall_thick / 2.0

    def seg_normal(a, b):
        d = b - a; L = np.linalg.norm(d)
        if L < 1e-9: return np.array([0.0, 1.0])
        d /= L; return np.array([-d[1], d[0]])

    edge_normals = [seg_normal(pts[i], pts[(i+1)%m_pts]) for i in range(m_pts)]

    vert_normals = []
    for i in range(m_pts):
        avg = edge_normals[(i-1)%m_pts] + edge_normals[i]
        L   = np.linalg.norm(avg)
        if L > 1e-9:
            sin_half  = L / 2.0
            miter_len = half / max(sin_half, 1e-6)
            if miter_len > half * 3:
                vert_normals.append(edge_normals[i])  # miter limit
            else:
                vert_normals.append(avg / L)
        else:
            vert_normals.append(edge_normals[i])

    verts, norms, indices = [], [], []

    def add_quad(v0, v1, v2, v3, nx, ny, nz):
        base = len(verts)
        for v in (v0, v1, v2, v3):
            verts.append(v); norms.append((nx, ny, nz))
        indices.append((base, base+1, base+2))
        indices.append((base, base+2, base+3))

    for i in range(m_pts):
        j  = (i+1) % m_pts
        xi, yi = pts[i];  xj, yj = pts[j]
        ni = vert_normals[i]; nj = vert_normals[j]; en = edge_normals[i]
        ob_i = (xi+ni[0]*half, yi+ni[1]*half, 0.0)
        ob_j = (xj+nj[0]*half, yj+nj[1]*half, 0.0)
        ot_i = (xi+ni[0]*half, yi+ni[1]*half, wall_height)
        ot_j = (xj+nj[0]*half, yj+nj[1]*half, wall_height)
        ib_i = (xi-ni[0]*half, yi-ni[1]*half, 0.0)
        ib_j = (xj-nj[0]*half, yj-nj[1]*half, 0.0)
        it_i = (xi-ni[0]*half, yi-ni[1]*half, wall_height)
        it_j = (xj-nj[0]*half, yj-nj[1]*half, wall_height)
        add_quad(ob_i, ob_j, ot_j, ot_i,  en[0],  en[1], 0.0)
        add_quad(ib_j, ib_i, it_i, it_j, -en[0], -en[1], 0.0)
        add_quad(it_i, ot_i, ot_j, it_j,  0.0,    0.0,   1.0)
        add_quad(ob_i, ib_i, ib_j, ob_j,  0.0,    0.0,  -1.0)

    vc = len(verts)
    vs = " ".join(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}" for v in verts)
    ns = " ".join(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}" for v in norms)
    ix = " ".join(f"{a} {b} {c}" for a, b, c in indices)
    tc = len(indices)

    if DEBUG:
        print(f"[DEBUG] DAE {out_path}: {vc} 顶点, {tc} 三角面, {m_pts} 段", file=sys.stderr)

    dae = f'''<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
  <asset><unit name="meter" meter="1"/><up_axis>Z_UP</up_axis></asset>
  <library_geometries>
    <geometry id="mesh0" name="Mesh">
      <mesh>
        <source id="pos">
          <float_array id="pos-arr" count="{vc*3}">{vs}</float_array>
          <technique_common><accessor source="#pos-arr" count="{vc}" stride="3">
            <param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/>
          </accessor></technique_common>
        </source>
        <source id="nor">
          <float_array id="nor-arr" count="{vc*3}">{ns}</float_array>
          <technique_common><accessor source="#nor-arr" count="{vc}" stride="3">
            <param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/>
          </accessor></technique_common>
        </source>
        <vertices id="verts">
          <input semantic="POSITION" source="#pos"/>
          <input semantic="NORMAL"   source="#nor"/>
        </vertices>
        <triangles count="{tc}">
          <input semantic="VERTEX" source="#verts" offset="0"/>
          <p>{ix}</p>
        </triangles>
      </mesh>
    </geometry>
  </library_geometries>
  <library_visual_scenes>
    <visual_scene id="Scene" name="Scene">
      <node id="Mesh" name="Mesh" type="NODE">
        <instance_geometry url="#mesh0"/>
      </node>
    </visual_scene>
  </library_visual_scenes>
  <scene><instance_visual_scene url="#Scene"/></scene>
</COLLADA>
'''
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(dae)

def deploy_sdf(mesh_dir, world_name, deploy_path):
    """生成并部署 SDF world 文件到 Ignition worlds 目录"""
    sdf = f'''<?xml version="1.0"?>
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
                <constant>0.9</constant>
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
        <model name="wall_0">
            <static>true</static>
            <pose>0 0 0 0 0 0</pose>
            <link name="link">
                <collision name="col">
                    <geometry><mesh><uri>file://{mesh_dir}/track_outer.dae</uri><scale>1 1 1</scale></mesh></geometry>
                </collision>
                <visual name="vis">
                    <geometry><mesh><uri>file://{mesh_dir}/track_outer.dae</uri><scale>1 1 1</scale></mesh></geometry>
                    <material><ambient>0.85 0.15 0.15 1</ambient><diffuse>0.85 0.15 0.15 1</diffuse></material>
                </visual>
            </link>
        </model>
        <model name="wall_1">
            <static>true</static>
            <pose>0 0 0 0 0 0</pose>
            <link name="link">
                <collision name="col">
                    <geometry><mesh><uri>file://{mesh_dir}/track_inner.dae</uri><scale>1 1 1</scale></mesh></geometry>
                </collision>
                <visual name="vis">
                    <geometry><mesh><uri>file://{mesh_dir}/track_inner.dae</uri><scale>1 1 1</scale></mesh></geometry>
                    <material><ambient>0.15 0.15 0.85 1</ambient><diffuse>0.15 0.15 0.85 1</diffuse></material>
                </visual>
            </link>
        </model>
    </world>
</sdf>'''

    # 先验证 XML 格式
    try:
        ET.fromstring(sdf)
    except ET.ParseError as e:
        print(f"[ERROR] SDF XML 格式错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 写入部署路径
    try:
        with open(deploy_path, 'w') as f:
            f.write(sdf)
        print(f"[OK] SDF 已部署 → {deploy_path}", file=sys.stderr)
    except PermissionError:
        tmp = '/tmp/custom_track_lidar.sdf'
        with open(tmp, 'w') as f:
            f.write(sdf)
        print(f"[WARN] 没有写入权限，SDF 暂存到 {tmp}", file=sys.stderr)
        print(f"[WARN] 请运行: sudo cp {tmp} {deploy_path}", file=sys.stderr)
        return

    # 验证部署结果
    with open(deploy_path) as f:
        c = f.read()
    assert c.count('wall_0') == 1
    assert c.count('ground_plane') == 1
    assert world_name in c
    assert 'Sensors' not in c
    print(f"[OK] 验证通过: world={world_name}, Sensors=无", file=sys.stderr)

# ═══════════════════════════════════════════════════════════
#  主流程
# ═══════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("用法: python3 svg_to_stl_sdf.py track.svg", file=sys.stderr)
        sys.exit(1)

    svg_path = sys.argv[1]
    out_dir  = os.path.dirname(os.path.abspath(svg_path))
    mesh_dir = os.path.join(out_dir, "meshes")
    os.makedirs(mesh_dir, exist_ok=True)

    # 1. 解析 SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()

    path_elems = []
    for elem in root.iter():
        if strip_ns(elem.tag) == 'path':
            d = elem.get('d', '')
            if d:
                path_elems.append((elem.get('id', '?'), d))

    if len(path_elems) < 2:
        print(f"[ERROR] 需要至少 2 条 path（内墙+外墙），找到 {len(path_elems)} 条", file=sys.stderr)
        sys.exit(1)

    print(f"[DEBUG] 找到 {len(path_elems)} 条 path", file=sys.stderr)

    # 2. 解析点列表
    all_pts = []
    for pid, d in path_elems:
        subpaths = parse_path(d)
        sp = max(subpaths, key=len)
        all_pts.append((pid, sp))
        gap = np.linalg.norm(np.array(sp[0]) - np.array(sp[-1]))
        print(f"[DEBUG] path {pid}: {len(sp)} 个点, 首尾距离={gap:.6f}mm", file=sys.stderr)

    # 3. 计算缩放比例
    if MANUAL_SCALE is not None:
        scale = MANUAL_SCALE
        print(f"[DEBUG] 使用手动 scale = {scale}", file=sys.stderr)
    else:
        gap_mm = estimate_track_gap(all_pts[0][1], all_pts[1][1])
        scale  = TARGET_TRACK_WIDTH / (gap_mm * 0.001)
        print(f"[DEBUG] 内外墙估算间距 = {gap_mm:.2f} mm", file=sys.stderr)
        print(f"[DEBUG] 自动 scale    = {scale:.4f}", file=sys.stderr)

    actual_scale = scale * 0.001  # mm → m

    # 4. 挤出 DAE
    labels = ["outer", "inner"]
    for i, (pid, pts) in enumerate(all_pts[:2]):
        dae_path = os.path.join(mesh_dir, f"track_{labels[i]}.dae")
        extrude_path_to_dae(pts, actual_scale, WALL_HEIGHT, WALL_THICK, dae_path)
        print(f"[OK] DAE  → {dae_path}", file=sys.stderr)

    # 5. 生成并部署 SDF（合并了 deploy.py 的功能）
    deploy_sdf(mesh_dir, WORLD_NAME, DEPLOY_PATH)

    print("", file=sys.stderr)
    print("══════════════════════════════════════", file=sys.stderr)
    print(f" 完成！赛道宽 {TARGET_TRACK_WIDTH:.2f}m = TurtleBot4({TURTLEBOT4_WIDTH}m) x {TRACK_WIDTH_RATIO}", file=sys.stderr)
    print(f" 启动命令:", file=sys.stderr)
    print(f"   __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia \\", file=sys.stderr)
    print(f"   ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py \\", file=sys.stderr)
    print(f"   world:={WORLD_NAME} model:=standard x:=0.5 y:=0.0 rviz:=true", file=sys.stderr)
    print("══════════════════════════════════════", file=sys.stderr)

if __name__ == '__main__':
    main()