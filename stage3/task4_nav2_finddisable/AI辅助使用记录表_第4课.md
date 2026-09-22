# 《AI 辅助使用记录表》· 第4课（P13 两处审核点）

> 原则：AI 生成的配置与代码同属**未经独立验证的输入**——允许用 AI 起草，但控制器选型要答得出适配理由、
> 每个数值要有本组出处、超时与失败分支要按契约写。巡场逐组查条目。
> 组号：G42　成员：________ / ________　日期：________

| # | AI 输入 | 缺陷判断 | 更正 / 审核结论 | 记录表条目 |
|---|---|---|---|---|
| 1 | 平台脚本 make_nav2_params_navmode.py / nav_stack_truthloc.sh 写死 jazzy 路径 | 本组环境为 humble，直接运行必失败（SRC 文件不存在 / setup.bash 不存在） | 在本任务 scripts/ 提供补丁副本（jazzy→humble，一行改动）；原平台仓库不动 | "平台脚本写死 jazzy／本组 humble／改 humble／已更正" |
| 2 | 平台参数生成器输出（RPP desired 0.8、robot_radius 0.22、膨胀 0.55、use_sim_time True） | 参数无本组出处；use_sim_time 与墙钟契约冲突；footprint 非本组值 | 生成后核对四项（P14）：RPP✓ 禁倒车✓；robot_radius→0.20（embodied_env.py）；膨胀→0.30 起步实测最窄通道；use_sim_time 全量翻 false；SHA256 冻结 | "AI 给出参数默认值／无本组出处／按四项核对改写／已更正" |
| 3 | navigate_to_service.py（Claude 起草，nav2_ws/src/navigate_to_service/） | 对照 P13 案例② 审核：无限重试？缺字段自动补默认？失败无原因？超时未先取消？ | 按契约核：预算 60s→先 cancel 再返回 TIMEOUT；FAILED 带可读原因（GetMap 预检+错误码翻译）；缺字段拒绝执行；无无限重试。**实测缺陷 ×3**：① 回调名 `handle` 遮蔽 rclpy.Node.handle 属性→启动崩溃，改名 `_on_navigate_to`；② Ctrl+C 二次 shutdown 崩溃，加 `rclpy.ok()` 守卫；③ `yaw_to_quat` 四元组解包进 2 变量→回调内异常无响应，改为直接写 z/w 并删死函数 | "AI 写了 navigate_to 封装／实测发现 3 处缺陷（handle 遮蔽、二次 shutdown、四元组解包）／均已更正" |
| 4 | task_plan.md 任务清单（Claude 生成） | 命令与判据未经执行验证 | 执行前逐条审核；执行中修改回写清单「变更登记」 | "AI 生成任务清单／执行中回写 N 处修改／已更正" |
| 5 | Claude 分析 ②④ traj/ROS2 日志并起草记录表四要素、T3.4 执行手册、障碍表镜像更正与"②注入未生效"结论 | AI 结论均为日志推断，未经组员复核 | 组员复核结论（填写）：□④目标 (1.89,9.62) 与 Goal failed 55.3s □②六目标与 Goal succeeded □真值 6 障碍表 □采纳 T3.4 手册 | "AI 分析实验数据并起草记录/手册／组员复核后采纳" |
| 6 | inject_pose_bias.py（Claude 起草，scripts/） | 发布 /initialpose 后仅 spin_once 0.5s 即退出——DDS 端点发现延迟 ~1.2s（2026-09-22 实测），消息全部丢失、AMCL 零接收 → ③ 主试无效注入（findings #35） | 改为存活 3s、每 0.1s 重复发布 30 次；实测 AMCL 收到 26 条/3s ✓；③ 补测重跑 | "AI 写了注入一键工具／发布器寿命 < DDS 发现延迟（实测缺陷）／已修复" |

**签字**：填写：________　审核员：________　日期：________
