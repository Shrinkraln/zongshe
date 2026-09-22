# 进度日志 · 第4课 Nav2 自主导航部署与失效注入实验

> 按时间顺序记录每次操作：谁做了什么、结果、下一步。**操作途中任何修改先回写 task_plan.md 变更登记，再在这里记一条。**

## 2026-09-21（课前准备日）

| 时间 | 事项 | 结果 | 下一步 |
|---|---|---|---|
| 14:40 | 提取 class.ppt 全文（P2–P24），勘察平台工具与第3课归档 | 明确本课交付：实验4-1（40%）+实验4-2（40%）+navigate_to（20%）；环境坑：平台脚本写死 jazzy、本机 humble（findings #1–#2） | 生成任务清单 |
| 15:00 | 生成规划三件套（task_plan/findings/progress）+ 四张记录表模板 | 已建 | 组员审核（T0.2） |
| 15:10 | 预生成执行材料：scripts/ 补丁副本 ×2、tools/ 注入工具 ×2、nav2_ws 两包（接口+服务） | 已建，未经编译/运行验证 | T0.2 审核 → T0.3 预注册单 → 课堂执行 |

## 课堂执行日志（2026-09-__）

| 时间 | 任务 | 执行人 | 结果/回写 |
|---|---|---|---|
| 2026-09-21 | T0.1 预检 | 组员 | 平台依赖 ✓、torch/sb3 ✓；nav2_bringup 无 executables → 检查命令已修正（findings #15/#16，task_plan T0.1 已回写）；pkill/ss 两行未见执行，需补跑确认 |
| 2026-09-21 | T0.2 材料核对 | 组员 | 材料清单齐全（tools/scripts/nav2_ws/四张表）✓；已回写 task_plan T0.2 |
| 2026-09-21 | T0.3 预注册单 | 组员 | 五条假设已填（①重规划②安全降级③重新收敛④带原因FAILED；实车绑架：不能）；成员/日期/签字待补 |
| 2026-09-21 | T0.4 基线跑分 | 组员 | 三道门全过：成功率 84.0%、碰撞率 12.0%、超时率 4.0%、平均到达步数 80.8；已回写预注册单「五」与 task_plan 变更登记 |
| 2026-09-21 | T1.4 参数 | 组员 | 生成+三处 sed 全生效（grep 复核：RPP/禁倒车/0.20/0.30/容差0.15）；冻结 SHA a57b6753…；最窄通道实测待补 |
| 2026-09-21 | T1.6/T1.7 导航 | 组员 | bt 日志复核：全部 Goal succeeded；巡航一圈 run3_circle 108s/23.9m；恢复行为 1 次（清除局部代价地图→重试成功）；碰撞预警不触发恢复 1 次；预占 2 次。**原 traj_G42_2.csv 第二遍 1102 帧被 16:09 同名误跑覆盖丢失（findings #17 更正）** |
| 2026-09-21 | T1.7 补录 | 组员 | 16:15 补录第二遍至 traj_G42_2.csv（1941 帧/194s/30.0m）→ 与第一遍一致（路径差 0.2m、时长差 2s）**判据 3 ✓**（findings #18） |
| 2026-09-21 | T2.1/T2.3 | 组员 | 编译通过；服务启动崩溃 `AttributeError: __enter__` → 根因＝handle 方法名遮蔽 rclpy.Node.handle 属性（findings #19）→ 改名 `_on_navigate_to`，待重编后重测 |
| 2026-09-21 | T2.3 重测 | 组员 | 两缺陷修复后节点启动/退出均正常 ✓；T6 调用报 `service type is invalid` → 根因＝T6 未 source 工作区 install（findings 见 T2.3 变更登记），已更正清单 |
| 2026-09-21 | T2.3/T2.4 实测 | 组员 | 第三缺陷（四元组解包）修复后：(0.6,5.0) → **SUCCEEDED 15.03s**（T2.3 达成 ✓，reason/elapsed 三字段正常）；T2.4 选点失效 → 按预案外移 (0.7,5.0) 重测（findings #4 更正） |
| 2026-09-21 | T2.4 TIMEOUT | 组员 | **(2.0, 9.5) → TIMEOUT 60.05s / reason="60 s 未到达" ✓**（先取消后返回、车已停）；三结果已达成 2/3，FAILED 待测 |
| 2026-09-21 | T1.1 补记 | Claude | 真值图解析得障碍表：5 圆障碍中心 (1.83,1.28)(4.30,2.00)(7.50,5.40)(7.20,7.88)(5.40,8.38)；核验 (5.5,1.5) 为自由格→T2.5 改占用点 |
| 2026-09-21 | T2.5 FAILED | 组员 | **(0.5, 9.9)（北墙带）→ FAILED 0.0s / "目标位于障碍物内" ✓**（GetMap 预检零秒返回）。**阶段 2 完成：三结果实测齐（SUCCEEDED/TIMEOUT/FAILED），P15 验收 20% 达成** |
| 2026-09-21 | T3.1R 重跑 | 组员 | 执行方式改为组员终端手动（Claude 后台进程被中断弃用，findings 见 T3.1R 变更登记）；20:36–20:44 组员已重建 T1 网关/T2 桥/T3 栈/T6 注入工具；inj1 重生成 SHA 一致 ✓；traj 文件名改 rerun2（rerun 被误录占用）；**⚠️ T6 起后注入默认开启，必须先 pub false 回基线** |
| 2026-09-21 | T3.1R 基线 | 组员 | traj_G42_inject0.csv 首录 1023 帧后被**同名二次运行覆盖**（剩 513 帧，findings #27）；组员已起新注入实例 --dist 1.5 --width 0.4（首测参数） |
| 2026-09-21 | T3.1R 复测 | 组员 | T3 21:12 重起失败（参数名笔误 sim1，findings #28）后修复；21:24 新 traj 运行 **3779 帧/378s/31.3m**（inject0.csv 第三次同名覆盖）——轨迹含 t+135–275s 完全冻结 140s（无风暴位移特征，findings #29）；冻结段因果待组员补报 |
| 2026-09-22 | T3.2 ④ | 组员 | rviz 原生对照目标 (1.89,9.62)（自由格，偏离"同 T2.5 障碍内点"设计）→ 55.3s 恢复风暴 → **Goal failed 16:44:56（无原因文本）**；无录像（两段录屏晚于失败时刻）——④行四要素已按日志+traj 完稿（findings #32）；障碍内点原生对照待补测 |
| 2026-09-22 | T3.3 ② | 组员 | **注入未生效**：栈 16:26:57–17:11:19 未重启，inj2（16:47:16）从未加载 → 六目标路线无屏蔽正常导航 Goal succeeded（findings #31）；②行按"无效注入+补测"记录；补测流程已写入 T3.3 变更登记 |
| 2026-09-22 | 数据分析 | Claude | 障碍表 y 镜像更正（真值 6 障碍，findings #33）；②④ traj/日志分析并回写记录表两行；T3.4 执行手册已出（下节）；录像-实验映射（findings #34） |
| 2026-09-22 | T3.4 ③ 主试 | 组员 | **执行无效**——注入工具发布器存活 0.5s < DDS 端点发现延迟 ~1.2s，AMCL 零接收（findings #35）；63.2s 实为无注入正常导航（Goal succeeded 39s，(5.06,2.95)；AMCL 漂移 0.34m 可作基线）；工具已修并实测送达（26 条/3s）；补测待跑（主试重跑＋U1 复测） |
|  | T0.3 预注册单 |  |  |
|  | T0.4 基线跑分 |  |  |
|  | T1.1–T1.7 实验4-1 |  |  |
|  | T2.1–T2.5 navigate_to |  |  |
|  | T3.1–T3.4 四类注入 |  |  |
|  | T4.1 实车抄录 |  |  |
|  | T5.1–T5.3 声明与解读 |  |  |
|  | T6.1–T6.3 验收归档 |  |  |

## T3.4（注入③ AMCL 定位先验扰动）执行手册（2026-09-22 出，组员逐条执行）

**起始状态**：T1 网关(9009)、T2 桥(9712)、T4 rviz(13941) 在跑；T6 scan_mask(21390) 残留；T3 导航栈已关。车位置未知（上次已知 ② 终点 (2.69,8.13)）。

1. **清残留**：T6 `pkill -f scan_mask`；`ros2 node list | grep -E "map_server|controller|planner|bt_navigator|static_transform"` 应为空（若有残留真值栈：T3 终端 Ctrl+C）。
2. **读当前真值**：`python3 /home/imain/workspace/zongshe_sum/stage3/task3_slamreliance/truth_probe.py --host 127.0.0.1`（记下 (x,y,θ)）。
3. **把车开回起点**（findings #12 硬前提：AMCL 预置位姿 (8.08,6.24,1.536)）：
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 run teleop_twist_keyboard teleop_twist_keyboard   # i=前 k=后 j/l=转
   ```
   开到 (8.08,6.24) 附近（±0.3m）、朝向≈88°（朝北）；停好后再跑 truth_probe 复核。
4. **起 AMCL 栈**（T3 终端）：
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 launch nav2_bringup bringup_launch.py map:=/home/imain/sim_ops/maps/map_gt.yaml params_file:=/home/imain/sim_ops/config/nav2_params_sim.yaml use_sim_time:=false
   ```
   （组员 17:11:59 已实测可起；参数含 `set_initial_pose: true` 预置 (8.08,6.24,1.536)——起栈即自定位。）
5. **T5 核对（先估计后真值，两条证据链独立）**：
   ```bash
   ros2 topic echo /amcl_pose --once        # 期望 ≈(8.08,6.24)，yaw≈1.54rad
   python3 /home/imain/workspace/zongshe_sum/stage3/task3_slamreliance/truth_probe.py --host 127.0.0.1
   ```
   两者差 ≈0 → 就绪；差 >0.3m → 车没回到起点，回步骤 3。可选：rviz 加 PoseArray 看粒子云是否聚在起点。
6. **第一试（主试）**：
   a. T5 起日志（**唯一文件名**，findings #17/#27）：`python3 ~/workspace/zs3_fyue/embodied-sim-lite-master/traj_logger.py --out ~/sim_ops/logs/traj_G42_inject3_amcl.csv`
   b. 开录屏（P19 三要素：注入动作＋rviz 反应＋最终结果）。
   c. T4 rviz `2D Nav Goal` 下单点目标 **建议 (6.0,3.0)**（真值障碍表核对：距 (7.52,4.56,r0.72)=2.18m、距 (5.43,1.60,r0.51)=1.51m，自由且路程 ≥5m）。
   d. 车移动 ≥2m 后（看 rviz 或 T5 日志坐标）**立刻**注入（一键工具＝读真值＋加偏置＋发布，输出合并）：
      ```bash
      python3 /home/imain/workspace/zongshe_sum/stage3/task4_nav2_finddisable/scripts/inject_pose_bias.py --host 127.0.0.1
      ```
      （默认偏置 +1.0m x／+30° yaw；输出含真值与注入值可直接抄录。车在动、真值读值有 0.1–0.5m 陈旧，课程 ±1m/30° 口径可容忍——如实记入记录。）
   e. **观察清单**（③行四要素素材）：粒子云是否重新收敛？**自恢复判定 ≤30s** 内是否继续导航？是否"锁定"（聚簇稳定不回摆）？轨迹是否绕圈/回摆（traj 事后分析）？是否触发恢复行为？最终 result（reached/failed/aborted）？全程记墙钟时刻。
   f. 车到达或失败后：Ctrl+C traj_logger（写盘）、停录屏。
7. **第二试（公共不可信区域 U1 复测）**：
   a. 起新日志 `traj_G42_inject3_amcl_repeat.csv`；开录屏。
   b. 目标：U1 长走廊附近（findings #9，(4.2,0.5) 一带）——**建议 (4.2,1.0)**：(4.2,0.5) 距南墙仅 0.45m，落在 RPP 前视停线内（④ 教训）；(4.2,1.0) 距墙 0.95m 可达（真值图 (4.2,1.0) 为自由格）。
   c. 同 6d 注入（**重新读真值再加偏置**）；同 6e 观察。
   d. 收尾：traj Ctrl+C、停录屏。
8. **实验后回写（Claude 执行）**：③行四要素（行名"孪生③ 定位先验扰动（条件 B 复测）"）；"绑架"行仍留空（课堂公共基线抄录）；traj/录像归档（`G42_定位扰动_<结果>.webm`，结果如 重新收敛/锁定失败 按实测）；task_plan T3.4 变更登记填结果；findings 新条目；progress 待办打勾。
9. **收尾**：关 AMCL 栈——Ctrl+C **按两次**（SIGINT 后 5s 才 SIGTERM，17:12:17 日志实证）；网关/桥不关。如需回到真值栈：`bash scripts/nav_stack_truthloc.sh ~/sim_ops/maps/map_gt.yaml ~/sim_ops/config/nav2_params_sim.yaml`。

**后续补测/补录（可选，各 ≤10 分钟，可在 ③ 之后做）**：
- **D1 ②补测（必做——现②行是无效注入）**：按 T3.3 变更登记五步（inj2 重启真值栈→scan_mask→接线核验见 scan_masked→同一六目标路线→traj_G42_inject2_mask_v2.csv）；完成后②行改标"补测"结论并启封假设②。
- **D2 ④录像补录（可选，补 P19 三要素）**：rviz 重发目标 (1.89,9.62)，录 60–90s 拍到恢复挣扎→Goal failed（同参同目标，~55s 裁决）；归档 `G42_不可达目标_恢复用尽失败.webm`，更新④行录像列。

## 当前状态（2026-09-22 傍晚快照）

**已完成**：
- 阶段 0（4/4）✓：预检、材料核对、预注册单假设（签字待补）、基线跑分（84.0%/12.0%/80.8）
- 阶段 1 ✓：真值图+网关+桥接+参数冻结（SHA a57b6753…）+真值栈+单点×3/巡航/贴板+连跑两遍一致（29.8m vs 30.0m，判据 3 达成）
- 阶段 2 ✓：navigate_to 封装（3 处缺陷修复记 AI辅助表 #3）＋三结果实测——SUCCEEDED 15.03s / TIMEOUT 60.05s / FAILED 0.0s；P15 验收（20%）可勾
- 阶段 3：① ✓ 闭环（恢复用尽→Goal failed，findings #30）；④ 已执行已回写（Goal failed 55.3s，无录像，findings #32）；② 无效注入已回写待补测（findings #31）；③ 未执行（执行手册已出，见上节）。**障碍表已更正为真值 6 障碍（findings #33）**
- ②④ injectx 文件已归档入仓库（config/nav2_params_inj2.yaml、logs/traj_G42_inject2_mask.csv、logs/traj_G42_inject4_invailable.csv、videos/G42_遮挡30%_注入未生效.webm）

**环境实况（2026-09-22 傍晚）**：网关(9009)/桥(9712)/rviz(13941)/scan_mask(21390) 在跑，导航栈已关（16:26 真值栈会话 17:11:19 关停；17:12:17 AMCL 起栈测试后关停）。

**已完成**：
- 阶段 0（4/4）✓：预检、材料核对、预注册单假设（签字待补）、基线跑分（84.0%/12.0%/80.8）
- 阶段 1 ✓：真值图+网关+桥接+参数冻结（SHA a57b6753…）+真值栈+单点×3/巡航/贴板+连跑两遍一致（29.8m vs 30.0m，判据 3 达成）；traj 6 份已入库 logs/
- 阶段 2 ✓：navigate_to 封装（3 处缺陷修复记 AI辅助表 #3）＋三结果实测——SUCCEEDED 15.03s / TIMEOUT 60.05s / FAILED 0.0s；P15 验收（20%）可勾
- 阶段 3 进行中：注入①三轮实测——1.5m/0.8m 宽 0.4（单束=点障碍，系统无扰动）+ 0.8m 宽 1.0（成墙→完整恢复风暴：后退/清代价地图/旋转三级恢复全无效，规划 3 连败，80s+ 仍在挣扎）；①行四要素草稿已出

**待办**：
1. ~~①结局补报~~ **✓ 已闭环（findings #30）：恢复用尽→Goal failed，自然裁决，无人工干预**。⚠️ 回基线（/inject false）待组员执行
2. ~~T3.2 ④~~ → **已执行并回写（findings #32）**：Goal failed 55.3s（无原因文本）。⚠️ 无录像（可选补录，见 D2）；目标点偏离设计——**障碍内点原生对照待补测**（findings #5）
3. T3.3 ② → **无效注入，补测待做**（流程在 T3.3 变更登记：inj2 重启栈→scan_mask→接线核验→同一六目标路线→traj_G42_inject2_mask_v2.csv）；**T3.4 ③ → 主试无效已归档（记录表③行标"补测"，traj+录屏入库，findings #35），工具已修实测送达；课后补测＝重跑主试（traj_G42_inject3_amcl_v2.csv）＋U1 复测（traj_G42_inject3_amcl_repeat.csv）**
4. 障碍表更正已回写 T1.1（findings #33）——**此后所有选点用真值 6 障碍表**
5. 实车公共基线抄录（课堂）；三条能力边界声明；六行记录表完稿（②④ 已写，剩 ③ + 实车两行）
6. 数据解读：预测-实测对照（①偏差已记、④已对照 findings #32、②不启封、③待执行）、SR@d_th 选做、回归 run_action1（改过膨胀→必做）
7. 遗留小项：最窄通道实测值、预注册单成员/日期/签字、录像归档命名（剩余段）、**traj_G42_inj1_rerun2.csv 去向待组员说明**（findings #34）
8. T6.1 验收三项核对 + T6.2 归档 git 提交

**数据备份位置（组仓库）**：logs/（traj×6）、config/（冻结参数 sim+inj1）、screenshoots/（T1.6 稳定演示截图）；实车地图沿用 task3 预验证数据。
