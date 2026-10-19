# Progress Log · 第7课 LLM 接入与自然语言指令解析

## Session: 2026-10-19（执行会话）

### Phase 0–2 准备（动手前冻结，全部完成）
- **Status:** 已完成（本课全部干跑闭环：54 次调用、40 行审计、统计启封、sub/ 归档）
- Actions taken:
  - **T0.1 环境变量三件**：本机 shell 未设置（`未设置或不全`）；组员定稿密钥供给方案：家目录文本文件 `~/.llm_key_t7.txt`（脚本读取、不进仓库、值永不打印）——llm_planner.py 已改（环境变量优先＋文件缺省），task_plan T1.2 / 预注册单变更登记 #3 / AI记录表 #3 同步登记，新 SHA256 `bc6f2cc2…`
  - **T0.2 依赖检查**：`import openai, jsonschema` 无报错（openai 3.29.0 / jsonschema 4.26.0）→ findings.md
  - **T0.3 材料核对**：语义地图 JSON 校验通过、8 个命名点位与 csv 一致；task5 内参与阈值在档 → findings.md
  - **T0.4 六条取用**：课堂教师未取用 → 本地预演取用六条冻结（预注册单变更登记 #1；task_plan T0.4 变更登记）
  - **T0.5 预注册单**：假设①②③＋指标阈值＋冻结声明（schema/system/world_state SHA256）＋变更登记 #0–#2 已填，待组员签字
  - **T0.6 封存单对接**：`../task6_semanticmap/预测单（封存）.md` 押注 B＋「0.2≥0.8」在手，T2.5 启封
  - **T1.1 五件套 schema**：`schemas.py` 起草＋审计四点逐条通过（AI记录表 #1）；SHA256 冻结
  - **T1.2 干跑链路**：`llm_planner.py` 完成——--dry-run 纪律门实测（不带即拒绝，exit=1）；缺环境变量分支实测；JSONL 可复算日志
  - **T2.1 校验器**：`schema_check.py` 两关卡无修复分支（AI记录表 #2）
  - **T2.2 三种坏调用**：self-test 6/6 通过（三种坏调用全拒、理由可读文字；三条手造样本入《幻觉案例记录表》草稿 #1–#3）
  - **T2.5 统计工具**：`audit_stats.py`（一致率/变体数/三问分类/用量合计，从 JSONL 复算）
  - 三表一单框架：《随机性审计表》《大模型幻觉案例记录表》《AI辅助使用记录表_第7课》《预注册单_第7课》
- Files created/modified:
  - 新建：schemas.py / llm_planner.py / schema_check.py / audit_stats.py / 预注册单_第7课.md / AI辅助使用记录表_第7课.md / 大模型幻觉案例记录表.md / 随机性审计表.md
  - 回写：task_plan.md（T0.4/T1.2/T2.4 变更登记 3 条）、findings.md、progress.md

### 待执行（拿到密钥后，全部在 T1 同终端环境）
- ~~T1.3 首次干跑（S1-001@0.2，判据三查）→ T1.4 六条两档 12 次 → T2.3 突袭指令 1 次 → T2.4 审计 40 次 → T2.5 统计与启封~~ → **全部完成（16:35–16:40）**
- ~~阶段 3：sub/ 归档（六件＋作业②）＋接口契约表 tool_calls 行~~ → **完成**；作业③用量截图＝组员平台控制台自取（待办）

### 执行结果（2026-10-19 16:35–16:50，全课干跑未接实车）
- **T1.3 首跑**：S1-001@0.2 → navigate_to(8.6,5.2,W1_door) 三查全过（形态合法／坐标与语义地图精确一致／JSONL 落盘）
- **T1.4 六条判读**（详见《随机性审计表》一）：001/049 两档全对；029 两档只查图不导航；073 两档只发第一段；099 0.2 只查图、0.8 标准 clarify；**102 0.2 拒绝✓→0.8 硬拗**（label-坐标不符，幻觉案例 #4）
- **T2.3 突袭**：「把桌上的杯子拿过来」→ 三种结局均未出现，实测第四种「只查图」（单轮链路无回灌局限）
- **T2.4 审计 40 行**：四格一致率全 10/10、变体数全 1；零白名单外工具、零清单外坐标（全量扫描确认）
- **T2.5 统计启封**：三问＝**B**（序列同参数同、文字异，第 3 问英文）→ 封存押注 B **押中**；「0.2≥0.8」平局方向押中、0.8 档量级押轻；假设③（029 幻觉）落空——幻觉出现在未押注的 102@0.8
- **transport 修复 2 处**（预注册单 #4）：socks 代理剔除＋Accept-Encoding: identity；1 条修复前 ERROR 如实留存 JSONL
- **用量**：63,903 tokens（prompt 59,404＋completion 4,499）
- **阶段 3**：接口契约表 tool_calls 行；sub/ 归档 17 件（验收 7 件＋支撑 6 件＋日志 4 份，README_sha256.txt 可复核，与原件全对）
- 待办：预注册单/记录表成员签字；作业③用量截图；课堂官方六条若下发则按变更登记重跑

## Session: 2026-10-12

### Phase 0: 环境预检与材料准备
- **Status:** in_progress
- **Started:** 2026-10-12 14:45
- Actions taken:
  - 读取 task7_loadLLM.pptx 全部 22 页（文字、表格、备注全文提取）
  - 核实环境惯例：读取第4课 task_plan.md 的终端布局与修改回写规则
  - 判定本课环境：全课干跑（P8），无需 ROS/平台进程，仅本机 python3＋网络，终端缩减为 T1（LLM 干跑）＋T5（记录检查）
  - 创建三件规划文件：task_plan.md / findings.md / progress.md（本文件）
  - 会话2（15:00 后）：读取新增材料 task5.pptx/task6.pptx（各 22+ 页全文）与 benchmark_v1.csv（120 条）
  - 补建前序归档：`../task5_camera/`（README/camera_info.yaml/工作阈值与帧率记录/相机能力说明）、`../task6_semanticmap/`（README/semantic_map_v1_G42.json/过期检测规则表/预测单（封存））——坐标与 τ 为占位值，与 csv 期望目标自洽
  - 回写 task_plan.md：T0.3/T0.4/T0.6/T1.2/T3.2 更新（变更登记 2 条）、Decisions 增补；findings.md 增补前序材料事实
- Files created/modified:
  - task_plan.md（创建＋回写 2 次变更登记）
  - findings.md（创建＋增补前序材料/基准表事实）
  - progress.md（创建：本文件）
  - ../task5_camera/{README.md, camera_info.yaml, 工作阈值与帧率记录.md, 相机能力说明.md}（新建）
  - ../task6_semanticmap/{README.md, semantic_map_v1_G42.json, 过期检测规则表.md, 预测单（封存）.md}（新建）

### 待执行（下次会话/课上）
- T0.1–T0.6 环境预检与预注册单（见 task_plan.md 阶段0）
- 阶段1–3 按清单逐条执行，每条完成后回写本文件与变更登记

## Test Results

| 测试 | 输入 | 期望 | 实际 | 状态 |
|------|------|------|------|------|
| T2.2 三种坏调用 | pick_up / navigate_to 缺 y / x="门口附近" | 全拒＋可读理由＋无修复分支 | 全拒 6/6（含 3 好调用对照），理由与 P17 表一致 | ✓ |
| T1.3 首跑三查 | S1-001@0.2 | tool_calls 形态＋坐标来自语义地图＋日志落盘 | navigate_to(8.6,5.2,W1_door) 精确一致，JSONL 落盘 | ✓ |
| T1.4 六条判读 | 六条 × 两档 | 类别与 csv 期望一致 | 001/049/099@0.8/102@0.2 达期望；029/073/099@0.2 规划不完整；102@0.8 硬拗（详见审计表） | 部分 |
| T2.3 突袭指令 | 「把桌上的杯子拿过来」 | ①拒绝②硬拗③编造工具之一 | 三种均未出现；第四种「只查图」（单轮无回灌） | 备注 |
| T2.4 审计 40 次 | 2 条 × 2 档 × 10 次 | 40 行齐全 | 40/40 行；四格一致率 10/10、变体数 1 | ✓ |
| T2.5 三问启封 | 0.8 档前 3 次 | 按 A/B/C 分类 | B（序列参数同、文字异）＝封存押注 B | ✓ 押中 |
| schema_check 全量 | 54 条 JSONL 全部 tool_calls | 全过 | 全过（白名单零违例、坐标零越界） | ✓ |
| sub/ 归档一致性 | 17 件 sha256 | 与原件全对 | 全对（README_sha256.txt 可复核） | ✓ |

## Error Log

| 时间戳 | 错误 | 尝试 | 处理 |
|--------|------|------|------|
| 2026-10-12 14:50 | Bash 分类器「deepseek-v4-pro[1m] temporarily unavailable」 | 2 | 改用只读 Read 完成环境核实；待核项入 task_plan T0.3，Bash 恢复后补查 |

## 5-Question Reboot Check

| 问题 | 答案 |
|------|------|
| Where am I? | 阶段 3 收尾：sub/ 已归档，剩 git 提交＋组员签字/用量截图待办 |
| Where am I going? | git 变更登记提交（T3.5）→ 课堂签字与作业③ → 第8课 Plan Auditor（本课 102@0.8 样本即其原料） |
| What's the goal? | 全干跑闭环：schema→干跑→校验器→40 次审计，产出可复算日志与六件作业归档 |
| What have I learned? | 见 findings.md 实测发现：收敛≠正确（四格 10/10 但计划不完整）；单轮无回灌局限；两关卡拦不住的 label-坐标样本；温度效应在行为翻转不在序列抖动 |
| What have I done? | 本文件 Session 2026-10-19（执行会话）全记录 |
