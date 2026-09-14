# ~/sim_ops 预验证数据清单（2026-09-14）

第3课·实车SLAM建图与定位可信度实验——孪生链路预验证的全部数据归档。
纪律五"数据当堂备份"：本目录已同步进组仓库 stage3/task3_slamreliance/预验证数据/（git c13830f 之后提交）。

## 目录结构

```
~/sim_ops/
├── config/mapper_real.yaml      # 建图参数（最终版：插帧0.1、smear 0.1、回环方差4.0、loop_search 6.0）
├── maps/
│   ├── map_gt.pgm / .yaml       # 真值图（make_gt_map.py --seed 42，200×200，origin [0,0]）
│   ├── sim_G42_slip0.pgm/.yaml  # slip=0 建图（307×289，origin [-3.75,-2.62]）——AMCL 重定位用图
│   └── sim_G42_slip005.pgm/.yaml# slip=0.05 建图（280×384，origin [0.678,-5.9]）——漂移对照图
├── overlays/
│   ├── sim_G42_slip0_overlay.png     # 叠合图（黑=真值，橙=建图）
│   └── sim_G42_slip005_overlay.png
└── README.md
```

## 对照统计（compare_maps.py，容忍 10cm）

| 图 | 场地覆盖 | 墙探索 | 墙命中率 | 假墙率(已探索) |
|---|---|---|---|---|
| sim_G42_slip0 | 49.3% | 45.2% | 23.4%（含未探索墙段） | 7.85% |
| sim_G42_slip005 | 44.0% | 49.1% | 20.4%（含未探索墙段） | 7.44% |

判读：两图假墙率同量级 → 与"漂移主因＝24线稀疏雷达，slip 为放大因子"的 A/B 归因一致（详见任务目录 findings.md）。

## 关键实验记录（详细见任务目录 findings.md）

1. **建图 A/B**：slip=0.05 与 slip=0 均漂移 → 主因＝稀疏观测（15°/5m，场地中央无回波）
2. **重定位条件A**（地图=sim_G42_slip0）：正确初始位姿 (2.278,0.102,−136.3°) 收敛到 (4.241,0.543,−108.2°)，**误差 2.01m**，椭圆长轴 0.69m（长走廊签名）→ 不可信区域候选 U1
3. **参数教训**：smear 硬上限 0.1（karto 校验 [0.005,0.1]，0.25 实测启动即崩）；max_laser_range=5.0

## 未归档项

- **frames.pdf**：预验证未跑 view_frames（tf 链完整性已由重定位功能间接证明）；课上正式执行时归档（验收第三项）
- **轨迹 CSV**：未用 traj_logger.py；如需"绕场两圈"量化证据可补跑
