# 发现与决策记录 · 第4课 Nav2 部署与失效注入

> 每课在 task_plan.md 中做决策时的依据都在这里；执行中发现的新问题也追加到这里（记录发现 → 改清单 → 继续）。

## 课前环境勘察（2026-09-21）

| # | 发现 | 影响 | 决策 / 去向 |
|---|---|---|---|
| 1 | 本机仅装 ROS **Humble**（/opt/ros/humble）；平台 nav 配套脚本写死 **Jazzy**：`make_nav2_params_navmode.py` 的 SRC 与 `nav_stack_truthloc.sh` 的 source | 直接运行必失败 | 在本任务 scripts/ 提供补丁副本（各一行改动），平台仓库不动；AI辅助表 #1、task_plan 变更登记 |
| 2 | humble 默认 `nav2_params.yaml` 里 **15 处 `use_sim_time: True`**（含 costmap/planner/controller/BT 段）；本课全链路契约＝墙钟（use_sim_time:=false，第1课"时间戳单调"、第3课预验证口径） | 不翻则 TF 时间错乱/外推错误 | T1.4 生成后用 sed 全量翻 false（已写入清单） |
| 3 | humble 默认参数：robot_radius 0.22、inflation_radius 0.55（两处 costmap）；生成器只改 FollowPath/goal 容差，**不碰 footprint 与膨胀** | PPT P14 巡场三查要求 footprint/膨胀＝本组值 | T1.4 追加 sed：0.22→0.20（出处 embodied_env.py `ROBOT_RADIUS=0.20`）、0.55→0.30 起步（P5） |
| 4 | **TIMEOUT 目标点设计（2026-09-21 实测更正）**：原理论（车停于 inscribed 边界 x≈0.30）**错误**——实测 (0.6,5.0) 15s SUCCEEDED，车到达 x≥0.45。真实停点由 **RPP 前视碰撞检测**主导（use_collision_detection＋速度缩放前视 0.3–0.9m）：停点 ≈ 墙表面+前视 ≈ x 0.40–0.45。故 TIMEOUT 目标需 |目标−停点|>0.15 → **外移到 (0.7, 5.0) 重测**（预案路径：±0.1m 阶梯校准） | TIMEOUT 分支可实测 | T2.4 主选 (0.6,5.0) 已证伪 → (0.7,5.0)；校准记录进变更登记 |
| 5 | humble 默认行为树 `navigate_to_pose_w_replanning_and_recovery.xml`：**NavigateRecovery number_of_retries=6**（清除代价地图/后退/原地旋转/等待循环） | 不可达目标会经历 ≤6 轮恢复后 FAILED——正是 P18「伪装执行 vs 有依据失败」的对照素材 | T2.5 观察项：Nav2 原生挣扎时长/恢复轮数 vs navigate_to 数秒 FAILED |
| 6 | 平台 sim 物理常数：ROBOT_RADIUS=0.20、GOAL_RADIUS=0.40、场地 10×10 m、墙厚 0.10 m（make_gt_map `--wall 0.10`）、24 线雷达 15°/5 m | footprint/最窄通道/目标点设计依据 | 已纳入 T1.4/T1.6/T2.4 |
| 7 | colcon + ros2 pkg create 齐备；有外网 | 自定义 srv（navigate_to_interfaces）可编译 | T2.1 colcon build 方案成立 |
| 8 | run_action1.py（S2 基线跑分）依赖 torch + stable_baselines3 | 基线/回归可能跑不了 | T0.1 预检；缺依赖则基线改课外并登记 |
| 9 | 第3课候选不可信区域 U1＝长走廊（AMCL 条件A 误差 2.01 m，世界坐标约 (4.2, 0.5) 一带；以《定位误差统计表》行号为准） | "贴近不可信区域边缘"的单点目标选点 | T1.6 目标3 候选 (4.2, 0.5) 附近 |
| 10 | 真值图 map_gt 两件套已存 ~/sim_ops/maps/（第3课预验证，seed 42） | 可直接复用；但需重跑 make_gt_map 拿障碍表/SHA 核对 | T1.1 重跑并比对 SHA |
| 11 | scan_inject.py 注入点在**机器人坐标系**（每帧随车重放），且启动即开启注入（/inject 可开关）；scan_mask.py 无开关 | ①注入前必须 `data: false` 回基线；现象描述要如实记"注入点随车移动" | 已写入 T3.1 |
| 12 | 注入③用 AMCL 栈；本组参数含 AMCL 预置位姿 (8.08,6.24,1.536)（生成器内置，seed 42 起点） | 起 AMCL 栈前必须把车开回起点，否则先验错误 | 已写入 T3.4 |
| 13 | 第4课 course_tools 仅两个注入工具（scan_inject/scan_mask），**navigate_to 无现成骨架** | 需自行封装（P15 骨架 + P13 案例②审核） | 已由 Claude 起草 nav2_ws 两包，T2.2 人工审核 |
| 14 | 平台 README 5.9：RPP 实测 0.8 m/s 满速、终点误差厘米级；MPPI 在本桥接下低速爬行 | 控制器选 RPP 的理由（P13 案例① 要答得出来） | 生成器 v6 已内置 RPP；审核点记录 |

## 执行中发现（课上/课后追加）

| # | 时间 | 发现 | 对清单的修改 |
|---|---|---|---|
| 15 | 2026-09-21 T0.1 | `ros2 pkg executables nav2_bringup` 无输出属正常——nav2_bringup 是纯 launch 包（bringup/navigation/localization 三 launch 文件），无 executables | T0.1 检查命令改为 `ls /opt/ros/humble/share/nav2_bringup/launch/` |
| 16 | 2026-09-21 T0.1 | 预检通过：平台依赖（fastapi/uvicorn/websockets/numpy/yaml）✓；torch + stable_baselines3 ✓ | T0.4 基线跑分可课上执行（原预案"缺则改课外"不触发） |
| 17 | 2026-09-21 T1.7 | **更正**：traj_logger 在 Ctrl+C 收尾时写盘——同名重启会覆盖旧文件。16:09 误用同名 traj_G42_2.csv 重跑（实际运行 57s/570 帧）后 Ctrl+C 写盘，**原 1102 帧第二遍数据已丢失**（此前"未覆盖"判断已过时）。教训：只要 Ctrl+C 触发写盘路径，任何同名重启都不可侥幸 | 纪律：每次起 logger 必须唯一文件名（traj_G42_3.csv 补跑） |
| 18 | 2026-09-21 T1.7 | 补录完成（16:15）：两遍一致 ✓——路径 29.8m vs 30.0m、时长 196s vs 194s、起止点/覆盖范围一致（findings #17 的教训已兑现：补录时仍用同名文件，本次覆盖的仅为残缺段故无损失，纪律二次提醒） | 判据 3 ✓；T6.1 验收①"连跑两遍一致"可勾（前提：录屏在库） |
| 19 | 2026-09-21 T2.3 | 服务启动崩溃 `AttributeError: __enter__`：回调方法名 `handle` 遮蔽 rclpy.Node.handle 只读属性（基类 `__init__` 内 `with self.handle:` 拿到普通函数）。P15 骨架的 `def handle(self, req)` 是教学示意，落码不可直接用该名。裸环境/colcon 环境建普通 Node 均正常（双重探测排除环境问题） | 改名 `_on_navigate_to` 并注释；重新 colcon build；记 AI辅助表 #3（AI 起草代码的缺陷实审） |
| 20 | 2026-09-21 T2.3 | 修复后节点正常启动，但 Ctrl+C 退出崩溃 `RCLError: rcl_shutdown already called`：rclpy 内置 SIGINT 处理器在 KeyboardInterrupt 前已调用 shutdown，except 块再显式调用即二次 shutdown（humble 无 try_shutdown） | 加 `if rclpy.ok():` 守卫；已改源码待重编 |
| 21 | 2026-09-21 T2.3 | SUCCEEDED 实测：请求发出无响应，T5 报 `too many values to unpack (expected 2)`——`yaw_to_quat` 返回四元组解包进 2 变量，异常抛在服务回调内（"never retrieved"）。教训：py_compile 与四问审核抓不住运行级解包错误，三结果实测本身就是验证手段 | 直接写 z/w 两行、删死函数；重编重测；记 AI辅助表 #3 |
| 22 | 2026-09-21 T3.1 | 注入①首测（dist 1.5）被系统"吸收"：斑定义在机器人坐标系，每帧随车头重标＋障碍层射线清除旧斑——等效"萝卜吊车前"，车永远追不上；且 1.5m 超出 RPP 前视碰撞视野（速度缩放前视 0.3–0.9m）。接线核验方法：`ros2 node info /local_costmap/local_costmap` 查订阅（humble 代价图是独立生命周期节点，不在 controller_server 节点信息里） | 建议变更登记后补测 --dist 0.8（进入前视视野，预期触发碰撞预警→恢复链） |
| 23 | 2026-09-21 T3.1 | dist 0.8 补测同样无扰动。**波束离散化根因**：24 线 15° 间隔 + width 0.4 → 半张角 atan(0.2/d)：1.5m→7.6°、0.8m→14°，均 <15° 间距 → 实际只注入 1 束＝单点障碍。单点斑被膨胀、随车头移动、规划器轻松绕开。与第 3 课"24 线稀疏"同源平台特性 | 建议 --dist 0.8 --width 1.0（半张角 32°→5 束≈1.1m 宽墙＋进入前视视野）→ 预期碰撞预警→恢复链 |
| 24 | 2026-09-21 T3.1 | --dist 0.8 --width 1.0（成墙）触发**完整恢复风暴**：三级恢复全部无效的机理＝①墙定义在机器人坐标系，后退/旋转时墙随车头转动重标，永远堵在正前方 ②清除代价地图无效——墙在下一次扫描（~50ms）即被重标 ③GridBased 反复规划失败（车头被堵＋两侧真实障碍构成口袋时无路可绕）。附观察：规划器循环率 20Hz→1.0–1.3Hz（反复请求过载） | ①行四要素已成形；最终结局待补报；恢复风暴全程录屏待确认 |
