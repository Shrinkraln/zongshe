# Task Plan: 第3课·实车SLAM建图与定位可信度实验（task3_slamreliance）

## Goal
依据《PPT_III-C03.pptx》（第3课·任务二第①课，4学时）制定并执行本课工作流程：完成孪生侧建图→重定位→5点×2条件采样、实车公共基线抄录、数据解读与验收六项交付。核心命题：**地图质量良好 ≠ 定位可信**——量化"在哪里不可信"，产出《定位误差统计表》（孪生版+实车版并列）、《定位不可信区域图》、TF树诊断报告、参数迁移说明。

## Current Phase
Phase 3.5 预验证完成；Phase 4 等待态（课上正式执行，本组 seed/先验口径）

## Phases

### Phase 3.5: 孪生链路预验证（本机手动，随跑随修，已完成）
- [x] 全链路跑通：真值图→nav_gateway→桥接→SLAM→存图→重定位（四判据全过）
- [x] 建图 A/B 归因：slip=0.05 漂移、slip=0 仍不干净 → 主因＝稀疏观测（24线/15°/5m），slip 为放大因子
- [x] 参数修复：max_laser_range 5.0；min_travel 0.1/0.1；回环方差 4.0、loop_search 6.0；smear 0.25 越界崩溃→改回 0.1（karto 硬校验 [0.005,0.1]）
- [x] 重定位预演：条件A 正确初始位姿收敛到错误位置，误差 2.01m、椭圆长轴 0.69m（长走廊签名）——不可信区域候选 U1
- [x] 工具产出：truth_probe.py、set_initial_pose.py、compare_maps.py（均实测验证）
- **Status:** complete

### Phase 1: 任务解析（PPT 24页拆解）
- [x] 提取 PPT 全文（24 页：核心问题/三工程原理/二具身纵深/三系统机制/两实验卡/七分步操作/数据表/验收/安全/收束）
- [x] 拆解交付物：地图两件套与真值图对照 · 《定位误差统计表》 · TF树诊断报告 · 《定位不可信区域图》 · 参数迁移说明 · 预注册单 · 《AI辅助使用记录表》
- [x] 实验矩阵：实验3-1 孪生侧（各组并行，7步）＋ 实验3-2 实车公共基线（全班共用）
- [x] 验收六项 + 评分结构（30% 地图质量互评 / 40% 采样数据完整性 / 30% TF树与参数迁移说明）
- [x] 课堂时间线：工程原理与具身纵深 30 → 系统机制 14 → 建图/互评/采样 78 → 课堂验证与数据解读 30 → 验收与收束 10（分钟）
- **Status:** complete

### Phase 2: 资产盘点（本组有什么 / 缺什么）
- [x] 平台脚本：~/workspace/zs3_fyue/embodied-sim-lite-master——README 5.9 静态世界模式、/health robot_truth、契约（/odom /scan tf QoS）已核实
- [x] truth_probe.py 不在平台仓库 → 本组自写（stdlib urllib，Phase 3 产出）
- [x] S1 第10课闭合误差表——用户确认：没有 → 噪声先验留空待填（材料提供推导规则）
- [x] S2 验证版 slam 参数——仓库无；以 humble 默认 mapper_params_online_async 为基底（本机已装 slam_toolbox），标注"到手后以其为准"
- [x] 平台无 odometry_noise_prior 同名参数（PPT 标注"示意"）→ 实际载体：扫描匹配搜索空间/响应阈值/回环方差阈值
- [ ] 硬件状态：本组以 PC Ubuntu 代替树莓派（已确认，材料已按此口径更新）；实车可用？（课上确认，清单中列为检查项）
- [ ] 组号（seed）与 --slip 值——课上确定，材料留空
- **Status:** complete

### Phase 3: 课前材料准备
- [x] config/mapper_real.yaml = humble 默认（帧对齐平台）+ 三项迁移参数标注 + 噪声先验占位与推导规则（出处：S1第10课闭合误差表第N行）——YAML 解析校验通过
- [x] 预注册单（假设 / 指标·阈值 / 冻结声明 / 变更登记四栏；先声明判据后采集数据）
- [x] 《定位误差统计表》模板（孪生版＋实车版并列，10行无空行，含统计栏与两版归因栏）
- [x] 《AI辅助使用记录表》条目格式（"AI 给出 X ／ 缺陷判断 ／ 实测为 Y ／ 已更正"＋P13 两案例预填）
- [x] 互评打分表（重影/缺口/畸变，1~5分，分数必须指出图上位置＋对应缺陷处置提示）
- [x] 参数迁移说明模板（三项：地图分辨率 / 扫描匹配阈值 / 里程计噪声先验＋出处＋(a)/(b)两量辨析）
- [x] 《定位不可信区域图》模板（证据编号＝统计表行号；证据三级；公共不可信区域登记；去向链）
- [x] 现场执行清单（课前检查6项＋180min时间线＋孪生7步命令 P14/P16＋实车公共基线 P19＋验收六项＋安全六条＋常见坑速查）
- [x] truth_probe.py（GET /health → robot_truth；stdlib urllib，平台无此脚本需自写）——语法校验与错误路径实测通过
- [x] 孪生链路预验证步骤.md（本机手动版：10 步，5 终端布局，含判据与常见坑）——本机依赖已核实全齐（nav2/slam_toolbox 2.6.10/rviz2/websocket-client）
- [x] compare_maps.py（建图↔真值图世界坐标对齐对照：覆盖率/墙命中缺口率/假墙量化 + 叠合PNG）——已用实跑地图验证：正确识别"地图只绕了 2.1%"
- **Status:** complete

### Phase 4: 现场执行·实验3-1 孪生侧（P14–P16，78min 主体）
- [ ] ① 真值图＋静态世界：make_gt_map.py --seed N → nav_gateway.py --seed N --slip（不得与 inference_server.py 同跑）
- [ ] ② 桥接：SIM_GATEWAY_WS=ws://IP:8000/ws python ros_bridge.py → ros2 topic hz /odom /scan ≈10Hz
- [ ] ③ 迁移参数并建图：slam_toolbox online_async + mapper_real.yaml；慢速绕行 2 圈（纪律：慢、两圈、判据 map→odom 非恒等）
- [ ] ④ 存图·对照真值图：map_saver_cli → maps/sim_<组号>.pgm+.yaml 两件套
- [ ] ⑤ 互评：相邻组交换工位，对照真值图打分（重影/缺口/畸变，指出位置）
- [ ] ⑥ 重定位→5×2采样：nav2 localization_launch；每点四项（AMCL估计 | 真值 | 误差 | 协方差目视三档）；条件B 记 收敛(用时)/发散/锁定；两条证据链独立
- [ ] ⑦ view_frames：TF 四段链齐全＋频率健康
- **Status:** pending

### Phase 5: 现场执行·实验3-2 实车公共基线（P18–P19）
- [ ] 示范车建图三命令（教师操作，清场后）；两件套分发
- [ ] 轮值测量员按分配表实测真值（卷尺量位置、量角器量朝向，先估计后真值）
- [ ] 抄录《定位误差统计表（实车版）》并签字；与孪生版并列、差异写入备注
- [ ] 公共不可信区域（多组同点发散/锁定）记入本组区域图
- **Status:** pending

### Phase 6: 数据解读与验收交付（P20–P22）
- [ ] 统计栏：误差均值 / 最大值 / 条件B收敛点数 __/5（口径与预注册单一致）
- [ ] 《定位不可信区域图》标注＋证据编号；不可信区域留白＝第六项不得分
- [ ] 验收六项核对（两件套备份 / 互评留档 / view_frames 归档 / 采样表10行+实车版签字 / 统计栏 / 区域图+参数迁移说明）
- [ ] 教师与审核员双签；maps 目录当堂备份组仓库
- [ ] git 提交（stage3 当前 untracked）
- **Status:** pending

## Key Questions
1. ~~本 session 范围~~ → 已定：课前材料准备，现场课上执行（同 task1 模式）
2. ~~闭合误差表~~ → 已定：没有，噪声先验留空待填（材料提供推导规则）
3. ~~平台脚本位置~~ → 已定：~/workspace/zs3_fyue/embodied-sim-lite-master（本地）
4. 组号（seed）与 --slip 值 → 课上确定，材料留空
5. S2 验证版参数基底 → 盘点平台后确认（make_nav2_params_navmode.py?）

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 规划文件放于 stage3/task3_slamreliance/ | 本课工作目录（同 task1 约定） |
| 工作流程按 PPT 时间线组织：准备→孪生→实车→解读验收 | 对应 PPT P10–P22 结构 |
| 本 session 只做课前材料准备 | 用户确认；现场建图/采样在课上执行 |
| 噪声先验留空待填 | 用户确认无闭合误差表；材料提供推导规则与填写位 |
| 平台＝~/workspace/zs3_fyue/embodied-sim-lite-master | 用户提供路径；本地已确认存在 |
| ROS2 端＝PC Ubuntu 代替树莓派 | 用户确认；①分辨率重调理由改为场景尺度＋真值图对照（算力非瓶颈）；桥接按同机/跨机两种拓扑写清单 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| 仓库内无平台脚本（make_gt_map/nav_gateway/ros_bridge/truth_probe） | 1 | 已确认：平台在 ~/workspace/zs3_fyue/embodied-sim-lite-master |
| 仓库内无 S1 闭合误差表、无 S2 slam 参数 | 1 | 闭合误差表确认没有（留空待填）；S2 参数待盘点平台确认 |
| 会话中 workspace 目录被重命名（zongshe→zongshe_sum） | 1 | 定位新路径，规划文件均完好 |

## Notes
- 每阶段完成后更新状态；决策前重读本文件
- 三条纪律：参数文件＝S2验证版＋本组噪声先验；地图两件套缺一不可；采样时估计与真值分别记录、互不参照
- 安全六条前三条直接决定数据有效性：建图清场 / 静态世界模式专用 / 桥接唯一实例（pkill -f ros_bridge）
- 分工：一人操作、一人记录
- 平台特性：24线稀疏雷达 AMCL 单腿漂移 0.2–0.5m（README 5.9），与实车 LD19 不作直接比较
