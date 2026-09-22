# 任务清单与执行指令 · 第4课 Nav2 自主导航部署与失效注入实验

> 依据：class.ppt（P3–P24）｜组号 G42｜seed 42｜--slip 0｜日期 2026-09-21
> **用法**：执行由组员本人操作，逐条打勾。每条任务标注【位置】【终端】【环境】【命令】【判据】【记录】。
> **修改回写规则**（本课纪律）：操作途中任何参数/坐标/命令修改，必须 ① 改本清单对应命令 ② 在该任务「变更登记」追加一行 ③ 在 progress.md 记一条。**先改清单，再继续操作。**
> 验收对照（P22）：① 导航稳定演示 40% ② 记录表+边界声明 40% ③ navigate_to 接口 20%。

## 全局环境与终端布局

**机器与拓扑**：同机拓扑——平台（embodied-sim-lite）与 ROS2 跑在同一台 PC（Ubuntu 24.04，ROS **Humble**）。
**关键路径**：

| 路径 | 用途 |
|---|---|
| `~/workspace/zs3_fyue/embodied-sim-lite-master` | 平台仓库（**只读**，脚本不改；本任务补丁副本在 scripts/） |
| `/home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable` | 本任务目录（清单/记录表/工具/ROS 工作区） |
| `~/sim_ops` | 运行数据目录（沿用第3课）：maps/ config/ logs/ overlays/ |

**终端布局（6 个，全部开在本机）**：

| 终端 | 角色 | 环境 | 常驻 |
|---|---|---|---|
| T1 | 平台端：make_gt_map → nav_gateway | 无 ROS，python3 | 是 |
| T2 | ROS2 桥接 ros_bridge.py | `source /opt/ros/humble/setup.bash` | 是 |
| T3 | ROS2 导航栈（真值栈/AMCL 栈） | 同上 | 是 |
| T4 | rviz2 | 同上 | 是 |
| T5 | 检查/记录/服务/traj_logger | 同上 | 按需 |
| T6 | 注入工具 scan_inject / scan_mask | 同上 | 按需 |

---

## 阶段 0 · 环境预检与材料准备（课前，约 20 分钟）

### T0.1 预检与清残留
- **位置**：任意；**终端**：T5；**环境**：本机
- **命令**：
  ```bash
  pkill -f ros_bridge; pkill -f nav_gateway; pkill -f scan_inject; pkill -f scan_mask
  ss -tlnp | grep 8000                          # 期望：空（安全六条②）
  source /opt/ros/humble/setup.bash
  ls /opt/ros/humble/share/nav2_bringup/launch/   # bringup/navigation/localization 三 launch 在（nav2_bringup 是纯 launch 包，无 executables）
  python3 -c "import fastapi, uvicorn, websockets, numpy, yaml"     # 平台依赖
  python3 -c "import torch, stable_baselines3"  # run_action1 依赖；缺则登记、基线跑分改课外
  ```
- **判据**：8000 空；依赖无报错。**记录**：依赖检查结果 → findings.md。
- **变更登记**：2026-09-21 已执行——平台依赖 ✓；torch/sb3 ✓（T0.4 可课上做）；nav2_bringup 无 executables（纯 launch 包），检查命令已改为 `ls /opt/ros/humble/share/nav2_bringup/launch/`。⚠️ 本记录中未看到 pkill/ss 两行执行，如未跑请补跑。

### T0.2 核对本任务目录已备材料
- **位置**：`/home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable`；**终端**：任意
- **命令**：
  ```bash
  ls tools/ scripts/ nav2_ws/src/ 预注册单_第4课.md 失效模式记录表.md 能力边界声明.md AI辅助使用记录表_第4课.md
  ```
- **判据**：工具/补丁脚本/ROS 包/四张表齐全（由 Claude 预生成，AI 辅助表已预登记 4 条）。
- **记录**：逐条审核 AI 预生成材料（P13），审核结论 → AI辅助使用记录表。
- **变更登记**：2026-09-21 已执行——材料清单核对齐全 ✓（tools/ scripts/ nav2_ws/src/ 四张表均在）。navigate_to_service.py 四问审核结论待补写 AI辅助表 #3。

### T0.3 填写《预注册单》（动手前！P12）
- **位置**：本任务目录 `预注册单_第4课.md`；**终端**：不需要终端，编辑器填表
- **内容**：四类注入预测（假设栏）；阈值已冻结（自恢复 ≤30s、d_th=0.30、遮挡 30%、预算 60s）；冻结声明栏签名。
- **判据**：假设栏与签字齐全，**之后才开始采集数据**。
- **变更登记**：2026-09-21 假设栏已填——①预计重规划 ②预计安全降级 ③预计重新收敛 ④预计返回带原因 FAILED 实车绑架：预计不能恢复。⚠️ 待补：成员/日期/签字（表格头部与文末）。

### T0.4 run_action1 基线跑分（P14 判据5 / P22 前提）
- **位置**：`~/workspace/zs3_fyue/embodied-sim-lite-master`；**终端**：T1；**环境**：平台端（无 ROS）
- **命令**：
  ```bash
  cd ~/workspace/zs3_fyue/embodied-sim-lite-master
  python3 audit/run_action1.py        # 门3：N≥20 回合，约 5–10 分钟
  ```
- **判据**：输出成功率/碰撞率/平均到达步数，产物 audit/eval_episodes.csv。
- **记录**：三项基线分 → 预注册单「五、基线跑分」。
- **变更登记**：2026-09-21 已执行——三道门全过（门1 3/3 抓假、门2 全绿、门3 产出指标）；基线分：成功率 **84.0%**、碰撞率 **12.0%**、超时率 4.0%、平均到达步数 **80.8**、平均步数 93.0；产物 eval_metrics.png / eval_episodes.csv / eval_summary.json。已回写预注册单「五」。

---

## 阶段 1 · 实验4-1 孪生侧 Nav2 部署与稳定演示（约 50 分钟，P11/P14，40%）

### T1.1 生成真值图（重跑拿障碍表与起点真值）
- **位置**：`~/workspace/zs3_fyue/embodied-sim-lite-master`；**终端**：T1；**环境**：平台端
- **命令**：
  ```bash
  python3 make_gt_map.py --seed 42 --out ~/sim_ops/maps
  ```
- **判据**：回显 起点真值 (8.08,6.24,88°)、**障碍表（6 圆障碍坐标+半径）**、SHA256；与第3课 map_gt 两件套同 SHA。
- **记录**：障碍表 → 预注册单（④选点依据）；起点真值 → ③用。
- **变更登记**：2026-09-21 障碍表由真值图解析补得（make_gt_map 回显未留档；第 6 个疑贴墙并入墙环）：**5 个圆形障碍中心＝(1.83,1.28) r≈0.75／(4.30,2.00) r≈0.98／(7.50,5.40) r≈0.73／(7.20,7.88) r≈0.78／(5.40,8.38) r≈0.52**。
- **变更登记（第 2 次，2026-09-22 更正）**：原 5 障碍表为 **y 镜像解析错误**（y→10−y）——真值（EmbodiedNavEnv seed42 直读，与 map_gt.pgm 栅格簇一致，其中 (4.52,7.80)/(3.99,8.33) 两圆图上重叠合并）＝**6 障碍＝(4.52,7.80,r0.79)／(1.83,8.71,r0.75)／(7.23,2.10,r0.78)／(3.99,8.33,r0.63)／(7.52,4.56,r0.72)／(5.43,1.60,r0.51)**（findings #33；证据：② 轨迹距表障碍 (5.40,8.38) 仅 0.025m、run3_circle 距真值圆心均 ≥0.9m）。原表历史留档不改写；**本课此后所有选点以真值表为准**。

### T1.2 静态世界网关
- **位置**：同 T1.1；**终端**：T1 同窗；**环境**：平台端
- **命令**：
  ```bash
  python3 nav_gateway.py --seed 42 --slip 0     # /odom ≡ 真值（P14）
  ```
- **判据**：回显 `seed=42 slip=0 tick=10Hz 起点真值=(8.08,6.24,88°) 永不reset`。⚠️ 不得与 inference_server.py 同跑（同占 8000）。

### T1.3 桥接 + 话题验证
- **位置**：`~/workspace/zs3_fyue/embodied-sim-lite-master`；**终端**：T2；**环境**：ROS2（source humble）
- **命令**：
  ```bash
  source /opt/ros/humble/setup.bash
  python3 ros_bridge.py          # 同机拓扑：默认 ws://127.0.0.1:8000/ws
  ```
- **T5 验证**：
  ```bash
  source /opt/ros/humble/setup.bash
  ros2 topic hz /odom /scan      # /odom ≈10Hz；/scan 稳定
  ```
- **判据**：桥接回显 `✅ 已成功连接到推理网关！`；hz 正常（越数越高＝双实例，pkill 重起唯一实例）。

### T1.4 生成并核对调优参数（RPP/禁倒车/footprint/膨胀）
- **位置**：本任务目录 `scripts/`（**补丁版**，原平台脚本写死 jazzy）；**终端**：T5；**环境**：无 ROS（python3+yaml）
- **命令**：
  ```bash
  python3 /home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable/scripts/make_nav2_params_navmode.py --out ~/sim_ops/config/nav2_params_sim.yaml
  # 墙钟契约：生成参数 use_sim_time 全量翻 false（15 处，第1课契约）
  sed -i 's/use_sim_time: True/use_sim_time: false/g; s/use_sim_time: true/use_sim_time: false/g' ~/sim_ops/config/nav2_params_sim.yaml
  grep -n "use_sim_time" ~/sim_ops/config/nav2_params_sim.yaml   # 应全为 false
  # 本组值：footprint 0.20（出处 embodied_env.py ROBOT_RADIUS=0.20）；膨胀 0.30 起步（P5）
  sed -i 's/robot_radius: 0.22/robot_radius: 0.20/g; s/inflation_radius: 0.55/inflation_radius: 0.30/g' ~/sim_ops/config/nav2_params_sim.yaml
  sha256sum ~/sim_ops/config/nav2_params_sim.yaml    # 冻结留档
  ```
- **核对四项（P14 巡场三查）**：① controller_server→FollowPath 插件＝`RegulatedPurePursuitController`（RPP）② `allow_reversing: false`（禁倒车）③ robot_radius 0.20＝本组值 ④ inflation_radius 0.30＝起步值；限速 desired_linear_vel 0.8＝S2 验证值（平台 README 5.9 注记；实车 0.25 出处另记）。
- **最窄通道实测（P5）**：在 rviz/地图上量障碍间最窄必经间隙；若 2×(0.20+0.30)=1.0 m 通不过 → 膨胀小步下调（0.30→0.25→…），每次记理由并回归基线。
- **记录**：SHA256 + 四个值 + 理由 → 预注册单「变更登记」#0–#3。
- **变更登记**：2026-09-21 已执行。生成回显：amcl 预置位姿(8.08,6.24,1.536)/RPP(desired 0.8)/goal 容差 0.15；use_sim_time 15 处全翻 false ✓；grep 复核四项：`xy_goal_tolerance: 0.15`、`desired_linear_vel: 0.8`、`allow_reversing: false`、`robot_radius: 0.20`×2、`inflation_radius: 0.30`×2 ✓。**冻结 SHA256（sed 后最终版）：a57b67530e3eab3d660697269041ef13f63cbf1a274ec9b3fab7de8fe8bf2b2c**（生成时刻 SHA ee36492c… 仅存档）。⚠️ 最窄通道实测值未报——预注册单变更登记 #2 该栏待补。

### T1.5 真值定位栈起 Nav2（map→odom 恒等）
- **位置**：本任务目录 `scripts/`（补丁版）；**终端**：T3；**环境**：ROS2（source humble）
- **命令**：
  ```bash
  source /opt/ros/humble/setup.bash
  bash /home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable/scripts/nav_stack_truthloc.sh ~/sim_ops/maps/map_gt.yaml ~/sim_ops/config/nav2_params_sim.yaml
  ```
- **T4 rviz2**：
  ```bash
  source /opt/ros/humble/setup.bash
  rviz2
  # Fixed Frame: map；Add：Map(/map)、LaserScan(/scan，Reliability 改 Best Effort 否则无点)、TF、Costmap(local/global)
  ```
- **判据**：回显 `===== 真值定位就绪（map→odom恒等），起导航栈 =====`；rviz 见真值图+膨胀代价图（对照平台 README 5.9 expected-view 两图）；无 TF extrapolation。

### T1.6 单点 ×3 + 多点巡航一圈（P14 判据 1–2）
- **位置**：T4 rviz2 `2D Nav Goal` 下发；**终端**：T4 操作 + T5 日志；**环境**：ROS2
- **目标选择**（避开障碍表与膨胀区，实际值以障碍表为准并登记）：
  - 目标1（场内自由点）：候选 (6.0, 3.0)
  - 目标2（另一侧自由点）：候选 (3.0, 8.0)
  - 目标3（**贴近不可信区域边缘**）：第3课候选 U1 长走廊区（世界坐标约 (4.2, 0.5) 附近，以本组《定位误差统计表》行号为准）
  - 多点巡航一圈（5–6 航点绕场）：候选 (8.5,1.5)→(1.5,1.5)→(1.5,8.5)→(8.5,8.5)→回起点附近，逐点下发
- **T5 每次导航一份日志（P14 判据 4，10 Hz CSV）**：
  ```bash
  source /opt/ros/humble/setup.bash
  python3 ~/workspace/zs3_fyue/embodied-sim-lite-master/traj_logger.py --out ~/sim_ops/logs/traj_G42_run1.csv
  ```
- **判据**：三目标全部 `Goal succeeded`；巡航不卡死、不碰撞、无人工干预；触发恢复行为→记第几级救回（P3 记录纪律：动作级）。
- **变更登记**：2026-09-21 已执行（bt_navigator 日志复核）。**全部 Goal succeeded，无失败、无人工救援**。探索阶段日志（15:38–15:44）：run0 斜穿 (7.75,7.18)→(1.73,1.94)；run1 西侧北上 (1.73,1.94)→(1.31,6.38)；run2_closetoboard 贴板南行 x≈0.5 (0.52,6.07)→(0.49,0.76)；**run3_circle＝多点巡航一圈** 108s/23.9m 范围 x[0.5,9.1] y[0.6,6.3]。异常记录（动作级）：① t=6828 目标 (3.85,1.05)→(6.26,1.83) 途中 RPP 碰撞预警 ×2，未触发恢复、继续行驶并成功（局部重规划）；② t=7069/7074 两次 goal preemption（人工提前下发下一航点，巡航正常操作）。

### T1.7 连跑两遍（P14 判据 3，P11「稳定」定义）
- **位置/终端/环境**：同 T1.6，同一路线再跑一遍，日志 `traj_G42_run2.csv`
- **判据**：两遍路径形态、用时、恢复行为触发情况一致——第一遍顺利、第二遍撞障碍的不叫稳定。
- **变更登记**：2026-09-21 已执行并补录完成，**判据 3 ✓（两遍一致）**。第一遍 traj_G42_1.csv＝1964 帧/196s/29.8m；第二遍（16:15 补录至 traj_G42_2.csv，再次使用同名文件但覆盖的仅为残缺段，无损失）＝1941 帧/194s/**30.0m**（路径差 0.2m、时长差 2s、起止点与覆盖范围一致）。原 1102 帧第二遍于 16:09 被同名误跑覆盖丢失（findings #17）。全链路 Goal succeeded；恢复行为 1 次（清除局部代价地图→重试成功）；碰撞预警不触发恢复 1 次；预占 2 次。⚠️ 补录仍用同名文件——纪律"唯一文件名"二次提醒。

---

## 阶段 2 · navigate_to 封装与三结果实测（约 30 分钟，P15，20%）

### T2.1 编译接口包与服务包
- **位置**：`/home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable/nav2_ws`；**终端**：T5；**环境**：ROS2（source humble）
- **命令**：
  ```bash
  source /opt/ros/humble/setup.bash
  cd /home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable/nav2_ws
  colcon build --symlink-install
  source install/setup.bash
  ros2 interface show navigate_to_interfaces/srv/NavigateTo
  ```
- **判据**：build 全绿；接口三字段（x/y/theta → result/reason/elapsed）显示正确。
- **变更登记**：2026-09-21 已编译通过（2 包 3.41s），但服务启动崩溃：`AttributeError: __enter__`（rclpy node.py:194）。根因（findings #19）：回调方法名 `handle` 遮蔽 rclpy.Node.handle 只读属性（P15 骨架命名陷阱），基类 `__init__` 中 `with self.handle:` 拿到普通函数。**已修复：改名 `_on_navigate_to` 并加注释；需重新 colcon build**（--symlink-install 下 install 指向 build 目录，改 src 后必须重编）。缺陷与更正记 AI辅助表 #3。
- **变更登记（第 2 次）**：修复重编后节点正常启动 ✓，但 Ctrl+C 退出崩溃 `RCLError: rcl_shutdown already called`——rclpy 的 SIGINT 处理器已先调用 shutdown，except 块里再调 `rclpy.shutdown()` 即二次调用（humble 无 try_shutdown）。**已修复：`if rclpy.ok():` 守卫**。另：组员执行了 `sudo rm -rf install/`（install 已删，需重新 colcon build；目录本属 imain，无需 sudo）。
- **变更登记（第 3 次）**：SUCCEEDED 实测中 T6 请求发出无响应、T5 报"exception never retrieved: too many values to unpack (expected 2)"——根因（findings #21）：`yaw_to_quat` 返回四元组却解包进 2 个变量，异常抛在服务回调内。**已修复：直接写 z/w 两行并删除死函数**；需重编后重测。三处缺陷均记 AI辅助表 #3。

### T2.2 审核 navigate_to_service.py（P13 案例②）
- **位置**：`nav2_ws/src/navigate_to_service/navigate_to_service/navigate_to_service.py`；**终端**：编辑器
- **审什么**：① 超时是否**先取消再返回**（60s 预算→cancel→确认终止→TIMEOUT）② FAILED 是否带可读原因（GetMap 预检 + 错误码翻译，错误码不算）③ 缺字段是否**拒绝执行**而非自动补默认 ④ 有无无限重试。
- **判据**：四问全过（或缺陷已改）。**记录**：审核结论 → AI辅助使用记录表 #3。

### T2.3 实测 SUCCEEDED
- **终端**：T5 起服务（常驻），T6 调用；**环境**：ROS2（source humble + install/setup.bash）
- **命令**：
  ```bash
  # T5
  source /opt/ros/humble/setup.bash
  source /home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable/nav2_ws/install/setup.bash
  ros2 run navigate_to_service navigate_to_service
  # T6（两处都要 source：工作区 install 提供自定义服务类型解析）
  source /opt/ros/humble/setup.bash
  source /home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable/nav2_ws/install/setup.bash
  ros2 service call /navigate_to navigate_to_interfaces/srv/NavigateTo "{x: 6.0, y: 3.0, theta: 0.0}"
  ```
- **判据（P15 验证 SUCCEEDED）**：正常目标 → `result=SUCCEEDED`，reason 可读，0 < elapsed < 60 合理。
- **变更登记**：2026-09-21 实测——T6 仅 source humble 时报 `The passed service type is invalid`（自定义类型解析需工作区 install 在 AMENT_PREFIX_PATH）。已更正：T6 须同时 source 两处 setup.bash。

### T2.4 实测 TIMEOUT（先取消再返回）
- **终端**：T6 调用；**环境**：同 T2.3
- **命令**：
  ```bash
  ros2 service call /navigate_to navigate_to_interfaces/srv/NavigateTo "{x: 0.6, y: 5.0, theta: 0.0}"
  ```
- **原理**（findings.md #4）：西墙内缘 x=0.1；机器人中心禁止区＝距墙 ≤0.20 m（本组值）→ 车停在 x≈0.3，距目标 0.3 m > 容差 0.15 m → 永不满足 → 60 s 预算耗尽。
- **判据（P15 验证 TIMEOUT）**：约 60 s 后 `result=TIMEOUT`、reason="60 s 未到达"；**返回时车已停止**（先取消再返回，顺序不可颠倒）；rviz 见车在墙前停住。
- **变更登记**：2026-09-21 首测 (0.6, 5.0) → **提前 SUCCEEDED（15.03s）**——选点失效（findings #4 更正：车停点由 RPP 前视碰撞主导，约 x≈0.40–0.45，不是代价地图 inscribed 边界 0.30；0.6 恰在 0.15 容差边缘）。**最终 TIMEOUT ✓：目标 (2.0, 9.5)（北墙）→ `result: TIMEOUT / reason: 60 s 未到达 / elapsed: 60.05`**——60s 预算耗尽、先取消后返回、车已停。现象细节（墙前停住或中途受阻，rviz 观察）待组员补记记录表。

### T2.5 实测 FAILED（＝注入④，两个实验共用这一次）
- **终端**：T6 调用；**环境**：同 T2.3
- **命令**（目标＝障碍表圆心，从 T1.1 回显取）：
  ```bash
  ros2 service call /navigate_to navigate_to_interfaces/srv/NavigateTo "{x: <障碍x>, y: <障碍y>, theta: 0.0}"
  ```
- **判据（P15 验证 FAILED / P18 有依据的失败反馈）**：**数秒内** `result=FAILED`、reason="目标位于障碍物内"（服务端 GetMap 预检）。
- **对照观察（P18）**：T4 用 rviz `2D Nav Goal` 对同一障碍内点直接下发（不经服务）→ 观察 Nav2 原生行为：多久放弃、放弃前触发几轮恢复行为（默认 BT NavigateRecovery 重试 6 轮）、放弃时返回什么 → 记录表④行 + 录像。
- **变更登记**：2026-09-21 组员拟用点 **(5.5, 1.5) 经真值图核验为自由格**（栅格值 254）——不能触发 FAILED 分支，须换占用点。**最终 FAILED ✓：组员改用 (0.5, 9.9)（北墙带，墙厚 0.10m，占用）→ `result: FAILED / reason: 目标位于障碍物内 / elapsed: 0.0`**——GetMap 预检零秒返回，P18"有依据的失败反馈"达成。三结果实测全部完成（SUCCEEDED 15.03s／TIMEOUT 60.05s／FAILED 0.0s）。

---

## 阶段 3 · 实验4-2 四类失效注入（顺序 ①→④→②→③，约 40 分钟，P16–P17，40%）

> 纪律：一次一异常；注入前回基线；全程录屏/录像；每类记四要素。时间不足②③课后补测并标"补测"。

### T3.1 注入① 动态障碍（局部绕行/全局重规划/恢复级别）
- **位置**：参数副本放 `~/sim_ops/config/`；**终端**：T6 工具 + T3 重起栈 + T4 下发；**环境**：ROS2
- **命令**：
  ```bash
  # T5 做参数副本：scan 话题 → /scan_injected
  sed 's|topic: /scan|topic: /scan_injected|' ~/sim_ops/config/nav2_params_sim.yaml > ~/sim_ops/config/nav2_params_inj1.yaml
  # T6 起注入工具（默认开启注入！先关回基线）
  source /opt/ros/humble/setup.bash
  python3 /home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable/tools/scan_inject.py --bearing 0 --dist 1.5 --width 0.4
  ros2 topic pub /inject std_msgs/msg/Bool "data: false" --once     # 回基线
  # T3 用 inj1 参数重起真值栈（命令同 T1.5，参数换成 nav2_params_inj1.yaml）
  # 基线：跑与 T1.6 相同路线的一个单点 → 途中 T6 开启注入：
  ros2 topic pub /inject std_msgs/msg/Bool "data: true" --once
  ```
- **观察与记录**：局部绕行还是全局重规划；恢复行为级别（清除代价地图/后退/原地旋转，第几级起效）；绕行成功与否；现象→记录表①行（注入点随车坐标系移动，如实记）；录像 `G42_虚拟障碍_<结果>.mp4`。
- **变更登记**：2026-09-21 首测（课程参数 bearing 0/dist 1.5/width 0.4）：接线核验 ✓（local/global costmap 均订阅 /scan_injected）；现象＝rviz 中车头前方 1.5m 持续出现障碍斑（随车头方位移动），**两段单点导航 (3.14,2.09)→(3.04,4.93) 13.0s、(3.08,4.80)→(2.08,1.00) 19.7s 均照常 Goal succeeded**——无碰撞预警、无恢复行为、无路径跳变。根因（findings #22）：斑每帧随车头重标＋射线清除旧斑＝"萝卜吊车前"，车永远追不上；1.5m 在 RPP 前视碰撞视野（≤0.9m）之外。**建议补测（变更登记）：--dist 0.8**——斑进入前视视野，预期可观测碰撞预警→减速→控制器耐心耗尽→恢复链（清除代价地图/后退/旋转均无效，斑随车转）→恢复用尽。理由：1.5m 无扰动实测；0.8m 进入碰撞视野。
- **变更登记（第 2 次）**：2026-09-21 补测 --dist 0.8 → 效果与 1.5m 相同（障碍出现在车头前方、系统无扰动）。**深层根因（findings #23）：24 线 15° 间隔雷达＋width 0.4 → 半张角 7.6°(1.5m)/14°(0.8m) 均 <15° 波束间距 → 实际仅注入 1 束＝单点障碍**，被膨胀成小斑、随车头移动、全局规划轻松绕开——系统照常到达。**下一步建议（变更登记）：--dist 0.8 --width 1.0（半张角 32°→注入 5 束≈1.1m 宽墙，且进入 RPP 前视视野）→ 预期碰撞预警→停车→控制器耐心耗尽→恢复链**。
- **变更登记（第 3 次）**：2026-09-21 补测 --dist 0.8 --width 1.0（成墙）→ **完整恢复风暴实测**（t≈897–975+，持续 80s 以上，目标 (2.43,2.40)）：① RPP 连续碰撞预警→Failed to make progress→FollowPath 中止 ② 触发后退（backup 10s 超时失败）③ 清除全局+局部代价地图→重试 ④ 碰撞预警密集→Controller patience exceeded→中止→清代价地图→重试 ⑤ Failed to make progress→原地旋转 90°（成功）→重试 ⑥ 全局规划连续 3 次失败（GridBased tolerance 0.50 无法生成到 (2.43,2.40) 路径）→每次清全局代价地图→重试 ⑦ 再次 Failed to make progress→再次旋转…（日志截断处仍在挣扎）。规划器循环率从 20Hz 跌至 1.0–1.3Hz（反复请求过载）。**最终结局（6 轮恢复用尽→FAILED？用户关注入？）待组员补报**。
- **变更登记（第 4 次）**：2026-09-21 晚 T3.1R 补跑取得自然裁决——**恢复用尽→`Goal failed`**（findings #30；①行四要素完稿、录像归档 videos/G42_虚拟障碍_恢复用尽失败.mp4）。预注册单假设①"预计重规划"实测**偏差**（孪生自恢复 ①=0/1）。

### T3.1R 注入①重跑：观测自然结局（2026-09-21 晚补跑，findings #26 决策）
- **目的**：①恢复风暴的自然结局未被拍到（录像末尾仍在挣扎）；重跑至 Nav2 自然裁决（预期 6 轮恢复用尽→FAILED），补齐 P19 录像三要素与①行"系统行为/边界声明"的最终裁决。
- **变更登记**：环境 18:06 已全停，需全链路重启；同参同目标重现：`--dist 0.8 --width 1.0`、目标 (2.43,2.40)。
- **命令**（与 T1.1–T1.5/T3.1 相同，参数用 inj1）：
  ```bash
  # T1 网关（后台）：cd ~/workspace/zs3_fyue/embodied-sim-lite-master && python3 nav_gateway.py --seed 42 --slip 0
  # T2 桥（后台）：source /opt/ros/humble/setup.bash && python3 ros_bridge.py
  # T3 真值栈 inj1（后台，日志留档）：
  #   bash scripts/nav_stack_truthloc.sh ~/sim_ops/maps/map_gt.yaml ~/sim_ops/config/nav2_params_inj1.yaml
  # T6 注入工具（后台）：python3 tools/scan_inject.py --bearing 0 --dist 0.8 --width 1.0
  #   起后立即 ros2 topic pub /inject std_msgs/msg/Bool "data: false" --once   # 回基线
  # 基线单点：ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose:{header:{frame_id:map},pose:{position:{x:2.43,y:2.40},orientation:{w:1.0}}}}"
  #   车行驶 ≥2 m 后开启注入：ros2 topic pub /inject std_msgs/msg/Bool "data: true" --once
  # 全程 traj_logger（唯一文件名！纪律 findings #17）：traj_G42_inj1_rerun.csv；组员录屏（三要素）
  ```
- **判据**：action 返回最终 result（SUCCEEDED/FAILED/aborted）＋ bt_navigator 日志裁决；观测上限 15 分钟——超时无裁决则如实记"持续挣扎无自然裁决"（本身也是结论）。
- **记录**：结局→记录表①行"系统行为"末尾与"边界声明"；录像按 P19 命名 `G42_虚拟障碍_<结局>.mp4`。
- **变更登记（第 1 次）**：执行方式＝组员终端手动（T1–T6 按全局终端布局，Claude 后台进程方案被中断弃用）；inj1 参数由组员 sed 重新生成、SHA 复核一致（82d3e2a1…）✓；traj 文件名改 **traj_G42_inj1_rerun2.csv**（rerun.csv 已被中断的后台实例误录 1.1MB 静止段占用，唯一文件名纪律）；⚠️ T6 注入工具**默认开启注入**，起后必须先 `ros2 topic pub /inject std_msgs/msg/Bool "data: false" --once` 且确认即时返回（此前一次 pub 在工具起之前发出，无订阅者、消息已丢）。

### T3.2 注入④ 不可达目标
- **操作**：同 T2.5（navigate_to FAILED + rviz 原生对照）。
- **记录**：记录表④行四要素：现象（数秒 FAILED+原因 vs Nav2 原生挣扎时长/恢复轮数）；根因（目标在静态层占用）；系统行为（动作级）；边界声明候选；录像。预注册单假设④启封对照。
- **变更登记**：2026-09-22 已执行——rviz 原生对照目标 **(1.89,9.62)**（自由格、墙前 0.28m，**偏离"同 T2.5 障碍内点"设计**）→ 55.3s 恢复风暴（RPP 碰撞预警→patience exceeded→spin 90°→wait→后退失败[朝墙 10s 超时]→spin→wait→重规划）→ **Goal failed（16:44:56，无原因文本）**；无录像（两段当日录屏均晚于失败时刻）。④行四要素已按此完稿；**障碍内点原生对照待补测**（预期 6 轮恢复循环，findings #5）。预注册单假设④启封对照：navigate_to 服务侧＝是（FAILED 0.0s 带原因）；Nav2 原生侧＝无原因 Goal failed（findings #32）。

### T3.3 注入② 感知降级（盲区 30%，与基线相同路线）
- **命令**：
  ```bash
  # T5 参数副本：scan 话题 → /scan_masked
  sed 's|topic: /scan|topic: /scan_masked|' ~/sim_ops/config/nav2_params_sim.yaml > ~/sim_ops/config/nav2_params_inj2.yaml
  # T6 起屏蔽工具（无开关，起即屏蔽）
  python3 /home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable/tools/scan_mask.py --sector 30
  # T3 用 inj2 参数重起真值栈 → T4 跑与基线相同路线
  ```
- **观察与记录**：盲区侧是否先出问题；减速/停止/上报（安全降级）还是照常行驶（危险硬闯）；现象→记录表②行；录像。
- **变更登记**：2026-09-22 执行**无效**——栈未用 inj2 重启（导航栈 16:26:57–17:11:19 单会话未重启，costmap 全程订阅 /scan，mask 无消费者，findings #31），六目标路线为无屏蔽正常导航、Goal succeeded（16:51–16:52 另有两次北墙近点导航 (1.74,9.64)/(0.84,9.56) 均成功，不在 traj 窗口内）。②行按"无效注入+补测"记录，假设②不启封。**补测流程**：① T3 用 nav2_params_inj2.yaml 重启真值栈 ② T6 起 scan_mask --sector 30 ③ T5 接线核验：`ros2 node info /local_costmap/local_costmap | grep -i scan` 应见 scan_masked ④ T4 跑同一六目标路线 ⑤ 唯一文件名 traj_G42_inject2_mask_v2.csv。

### T3.4 注入③ 定位先验扰动（AMCL 栈，切换约 2 分钟；条件 B 复测，不是绑架）
- **命令**：
  ```bash
  # 先把车开回起点（T4 rviz 或 teleop：ros2 run teleop_twist_keyboard teleop_twist_keyboard，回到 (8.08,6.24) 附近）
  # T3：关真值栈 → 起 AMCL 栈（参数含 AMCL 预置位姿）
  ros2 launch nav2_bringup bringup_launch.py map:=/home/imain/sim_ops/maps/map_gt.yaml params_file:=/home/imain/sim_ops/config/nav2_params_sim.yaml use_sim_time:=false
  # T5 核对（先估计后真值，两条证据链独立）：
  ros2 topic echo /amcl_pose --once
  python3 /home/imain/workspace/zongshe_sum/stage3/task3_slamreliance/truth_probe.py --host 127.0.0.1
  # T4 下发单点目标 → 车行驶中（已移动 ≥2 m）发布偏置 1 m（位置＋朝向）的 /initialpose：
  python3 /home/imain/workspace/zongshe_sum/stage3/task3_slamreliance/set_initial_pose.py --x <真值x+1.0> --y <真值y> --yaw-deg <真值yaw+30>
  # 在公共不可信区域附近重复一次
  ```
- **观察与记录**：能否重新收敛、用时、是否锁定；记录表③行（标"条件 B 复测"）；"绑架"行由实车公共基线抄录（本组不执行）。
- **变更登记**：2026-09-22 已出执行手册（见 progress.md「T3.4 执行手册」）；组员 17:11:59 已实测 AMCL bringup 可起（18s 后主动关停）。**选点更正（findings #33）**：本课障碍表已更正为真值 6 障碍，目标按真值表避开；U1 复测目标由 (4.2,0.5) 外移至 **(4.2,1.0)**（原点距南墙仅 0.45m，落在 RPP 前视停线内——④ 教训）。执行后由组员回写结果。

---

## 阶段 4 · 实车公共基线（课堂，教师执行；本组抄录，约 10 分钟，P17）

### T4.1 抄录实车两行并签字
- 实车① 纸箱：路径前方 1~2 m 放纸箱、手离开 → 记录恢复级别
- 实车③ 绑架：空旷区、双人护航，拎起平移 1 m 放下 → 记录粒子云收敛/发散/锁定与用时；公共不可信区域内重复一次
- **记录**：两行四要素抄入《失效模式记录表》+ 签字；P21「实车公共对照」栏同步。

---

## 阶段 5 · 数据解读与边界声明（约 30 分钟，P19–P21）

### T5.1 三条能力边界声明（P19 模板）
- **位置**：本任务目录 `能力边界声明.md`；**判据**：条件量化/能力明确/现象可复现/结论可反驳；至少一条与位置相关；各附录像编号；写完互问（他组能否复现）。
- **变更登记**：________

### T5.2 《失效模式记录表》六行四要素完稿（P20）
- **判据**：系统行为写到动作级（"触发清除代价地图、无效；后退 0.3 m；重试成功"式）；根因写机理；补测行标注"补测"；录像命名规范。

### T5.3 数据解读三则（P21）
1. **预测-实测对照**：启封预注册单——孪生自恢复数 __/3（①②③，③为先验扰动）；④带原因的 FAILED？（是/否）
2. **SR@d_th（选做）**：用预注册 d_th=0.30 对三次单点导航的 NE（traj CSV 终点误差）判成功，初算 SR；册1 以本课日志换 0.30/0.40 两阈值演示翻转（第6课前，与 FROZEN.md 对账）。
3. **冻结基准回归**：本课改过膨胀半径 → 课后用同一基线任务复跑 `run_action1`：基线分不掉且公共不可信区域附近表现不退化才算真改进。
- **记录**：回归分 → 预注册单「变更登记」#2。

---

## 阶段 6 · 验收与归档（10 分钟 + 课后，P22/P24）

### T6.1 阶段验收三项核对（P22）
| # | 验收项 | 判据 | 占比 | 勾 |
|---|---|---|---|---|
| 1 | 导航稳定演示 | 单点×3 全部到达、多点巡航一圈、连跑两遍一致（录屏在库） | 40% | ☐ |
| 2 | 《失效模式记录表》与边界声明 | 六行四要素完整、行为动作级；三条声明附录像编号，至少一条与位置相关 | 40% | ☐ |
| 3 | navigate_to 接口 | 三字段齐全；SUCCEEDED/TIMEOUT/FAILED 三种结果实测；reason 可读文字 | 20% | ☐ |
- **前提**：改过导航参数须提交回归记录（基线跑分＝run_action1 输出）。

### T6.2 归档（作业①）与收尾
- **命令**：
  ```bash
  mkdir -p ~/sim_ops/logs
  cp ~/sim_ops/logs/traj_G42_*.csv /home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable/
  # 依次 Ctrl+C：T6 工具 → T5 服务 → T4 rviz → T3 栈 → T2 桥 → T1 网关
  pkill -f ros_bridge; pkill -f nav_gateway; pkill -f scan_inject; pkill -f scan_mask
  ss -tlnp | grep 8000        # 期望空
  ```
- **归档清单**：失效模式记录表、三条边界声明、全部录像、导航日志 CSV、预注册单、回归记录、AI辅助使用记录表 → 本任务目录 + git 提交。
- **作业②**：册1《指标复算》（选做，第6课前）。**作业③**：确认相机到位；带第1课算力预算页（YOLO 约 5 FPS 预估）。
- **纪律**：道具离场、雷达视场复检；失败录像归档不得删除；实车仅教师操作。

---

## 变更登记汇总（执行中所有修改在此汇总，逐条留痕）

| 日期时间 | 位置（任务号） | 原内容 | 修改后 | 理由 |
|---|---|---|---|---|
| 2026-09-21 课前 | scripts/ 两脚本 | jazzy 路径 | humble 路径 | 本组 ROS2 端为 humble |
| 2026-09-21 课前 | T1.4 参数 | 生成参数未动 | use_sim_time 全量翻 false | 墙钟契约（第1课） |
| 2026-09-21 执行 | T0.1 检查命令 | `ros2 pkg executables nav2_bringup`（无输出） | `ls /opt/ros/humble/share/nav2_bringup/launch/` | nav2_bringup 是纯 launch 包，无 executables |
| 2026-09-21 执行 | T0.3 预注册单 | 假设栏空白 | 五条假设已填；成员/日期/签字待补 | P12 先声明后采集 |
| 2026-09-21 执行 | T0.4 基线跑分 | 空白 | 成功率84.0%/碰撞率12.0%/平均到达步数80.8 已回写预注册单「五」 | P22 前提：改参须有回归对照 |
| 2026-09-21 执行 | T1.6/T1.7 日志 | 计划名 traj_G42_run1/run2.csv | 实际 6 文件：run0/run1/run2_closetoboard/run3_circle（探索+巡航一圈）＋traj_G42_1（第一遍大圈 1964 帧）＋traj_G42_2（第二遍，**原 1102 帧被覆盖**） | 以实际命名为准 |
| 2026-09-21 执行 | T1.7 日志操作 | — | ⚠️ 16:09 误用同名 traj_G42_2.csv 重跑并 Ctrl+C 写盘，**原 1102 帧第二遍数据丢失**（更正：此前"未覆盖"判断已过时） | 纪律：每次起 logger 必须唯一文件名；补跑用 traj_G42_3.csv |
| 2026-09-21 执行 | T1.4 参数冻结 | — | 最终 SHA256：a57b6753…（四项核对全过）；最窄通道实测值待补 | 冻结值入预注册单 |
| 2026-09-21 晚 | T3.1 注入① | 结局未拍到 | 新增 T3.1R 重跑观测自然结局（同参 0.8/1.0、同目标 (2.43,2.40)、traj 唯一文件名、T3 日志留档、观测上限 15 分钟） | findings #26：三段风暴录像末尾均无结局；P19 三要素缺"最终结果" |
| 2026-09-22 执行 | T1.1 障碍表 | 5 障碍（y 镜像解析） | 真值 6 障碍＝(4.52,7.80,r0.79)/(1.83,8.71,r0.75)/(7.23,2.10,r0.78)/(3.99,8.33,r0.63)/(7.52,4.56,r0.72)/(5.43,1.60,r0.51) | 原表 y→10−y 镜像；影响 T1.6/T2.4/T3.x 选点依据（findings #33） |
| 2026-09-22 执行 | T3.2 注入④ | 计划障碍内点（同 T2.5） | 实际 (1.89,9.62) 自由格（墙前 0.28m，RPP 停线内）→ 55.3s 恢复风暴 → Goal failed（无原因文本）；无录像 | 目标点偏离设计，④行如实记录；障碍内点原生对照待补测（findings #32） |
| 2026-09-22 执行 | T3.3 注入② | 计划 inj2 重启栈 + scan_mask | 实际栈未重启、mask 无消费者 → 注入未生效 → 正常 Goal succeeded | ②行按"无效注入+补测"记录；补测流程已写入 T3.3 变更登记（findings #31） |
