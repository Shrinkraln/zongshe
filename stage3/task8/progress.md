# Progress Log · 第8课 规划执行器与防幻觉审计层

## Session: 2026-10-19（课前规划）

### Phase 0: 环境预检与材料准备
- **Status:** in_progress
- **Started:** 2026-10-19 14:55
- Actions taken:
  - 提取 task8.pptx 全部 23 页文字（状态机、四规则溯源表、八发测试表、对照实验 12 格、拆封四条件、验收三项全文）
  - 逐项核对前序数据在盘状态：第3课地图（10×10 m 数值域）、第4课失效记录表④行/能力边界声明/孪生环境（nav2_ws＋平台仓库＋冻结参数）、第6课语义地图与 τ 表（占位值）、第7课 benchmark_v1.csv
  - **发现缺口 E2**：task7_loadLLM/ 无实验产物（schemas/llm_planner/schema_check/plan_log/案例表均不在盘）——P9 干跑回归与 P4 溯源硬依赖 → task_plan.md 立 T0.2 核对/补跑项
  - 发现 LLM 三件环境变量本机未设置（E1）；openai＋jsonschema 已装 ✓
  - 由已核数据推导八发测试用例坐标（地图外 (50,50)、障碍内 (4.52,7.80)、fresh/stale cup、NaN/1e9、kitchen 等）并写入 task_plan.md T0.5
- Files created/modified:
  - task_plan.md（创建：执行清单，含 ⚠️ 环境准备清单 E1–E8、阶段0–5、八发用例、溯源表模板、变更登记）
  - findings.md（创建：前序数据核对表、缺口、导出数据）
  - progress.md（创建：本文件）

### 待执行（课上/下次会话）——阻塞原因两重：**GUI/录屏 ＋ 扫描**（LLM env 已解除：本机密钥文件口径，见下）
- T0.4 预注册单组员签字（假设①按封存单填）；课堂补 12 格截图与全程录像（真数据已在盘，logs/contrast_12.jsonl）
- 阶段2 孪生真执行链、阶段4 实车（**阻塞：GUI/录屏 ＋ 扫描**——孪生链需要平台 24 线雷达 `/scan` 扫描流（gateway/bridge 起后才有），无扫描流＝真值定位与导航无输入；实车另需教师栈与公共语义地图）
- 阶段5 归档与提交

## Session: 2026-10-19 深夜（真 LLM 数据执行）

### Phase 1/3 干跑数据真跑（LLM 阻塞解除后）
- **Status:** in_progress
- Actions taken:
  - LLM 阻塞解除：并行会话发现本机密钥文件 `~/.llm_key_t7.txt`＋三坑修复（剔 socks 代理／Accept-Encoding: identity），llm_planner.py 已按新口径更新（call_llm 新签名）→ agent_loop 对齐
  - agent_loop.py 第2次修改：schema_check 驻场接入 AUDITING（P4 白名单前置）＋突袭模式（--unbounded-replan/回注/--max-loops）＋outcome 出口 bug 修复；冒烟增至**七例全过**
  - **T1.4 干跑回归真跑**：六条指令（S1-001/S2-029/S3-049/S4-073/S5-099/S5-102，S5 只编号）temperature 0.2 → S1–S4 全部放行→EXECUTING→完成；S5 两条模型无 tool_calls（与第7课 0.2 档一致）→ `logs/regression_G42.md` 并排表
  - **阶段3 对照 12 格真跑**（`run_contrast_12.py`，0.2/0.8 两档）：0.2 档接下 2/6（T5、T6）、0.8 档接下 3/6（T3、T5、T6），两档均落 B 区间；T1/T2/T4 模型自行拒绝（未复现幻觉，如实记录）；开审计 2/2 与预判一致（T5→①、T6→②，真 LLM 输出实弹拦截）→ 官方对照表已回填
  - **T3.4 突袭真跑**：循环 2 次、调用 2 次、终止方式＝回注后模型改口（cup→W6_bench）→《突袭记录》实数据；无限重试本配置未复现（如实记录）
  - 预注册单变更登记③④、接口契约表 audit 行（schema+audit 双重前提）、AI辅助表条目5、SHA256 重算入冻结声明
- Files created/modified:
  - run_contrast_12.py（新建）；agent_loop.py（第2次修改）
  - 幻觉证伪对照表_第8课.md（真数据回填）、突袭记录.md（真数据）、AI辅助使用记录表_第8课.md（+条目5）、接口契约表.md（audit 行更新）、预注册单_第8课.md（变更登记③④＋SHA256）
  - logs/regression_G42.md、logs/contrast_12.jsonl、logs/contrast_12_rows.md（新建）
  - task_plan.md（T1.4/T3.2/T3.3/T3.4 实际命令行＋变更登记回正）

## Session: 2026-10-19 晚间（课前执行）

### Phase 0–1 干跑部分执行
- **Status:** in_progress
- Actions taken:
  - **T0.1** LLM 三件验证：未设置（阻塞项，如实登记）
  - **T0.3** 前序数据核对：map_gt 200×200@0.05（数值域 [0,10]²）、语义地图 JSON 校验通过、第4课三件在盘 ✓
  - **T0.6** 孪生预检：无残留进程、8000 空、nav2_bringup launch 在、依赖齐全 ✓
  - **T0.2** 第7课产物核对：并行会话已补建六件（代码＋四张表）；六条指令干跑输出仍缺（LLM env 阻塞）
  - **T0.5/T1.1** plan_auditor.py＋test_plan_auditor.py 起草落盘；**占据判据变更登记①**（平台调色板 254=自由/0=占据，首跑 3/10 → 改判据＋y 翻转 → 10/10）
  - **T1.2** 八发测试 **10/10 通过**（八发基线＋2 冗余），日志 logs/audit_8shots.log
  - **T1.3** agent_loop.py 状态机＋冒烟五例全过（完成/整案拒绝/重规划/超限/关审计），日志 logs/state_machine_smoke.log；《接口契约表》audit 行登记
  - **T0.4** 预注册单代拟（假设①留白待组员按封存单填）；溯源表/对照表模板/突袭记录/AI辅助表（4 条目）落盘
  - SHA256 冻结：plan_auditor `ddc57c89…`、agent_loop `e2b746b3…`、test `b34c2abc…`
- Files created/modified:
  - plan_auditor.py / agent_loop.py / test_plan_auditor.py（新建）
  - 规则溯源表_第8课.md / 预注册单_第8课.md / 幻觉证伪对照表_第8课.md / 突袭记录（并入对照表） / AI辅助使用记录表_第8课.md / 接口契约表.md（新建）
  - logs/audit_8shots.log、logs/state_machine_smoke.log（新建）
  - task_plan.md（变更登记 4 处回写）

## Test Results

| 测试 | 输入 | 期望 | 实际 | 状态 |
|------|------|------|------|------|
| 八发测试 | 四规则好/坏各1＋2冗余 | 10/10 全中 | **10/10**（首跑 3/10：占据判据调色板不符→改判据重跑） | ✅ |
| 状态机冒烟 | 七例（完成/整案拒绝/重规划/超限/关审计/schema拦截/突袭打断） | 三出口＋关审计＋突袭语义正确 | 七例全过（初稿 REPORTING 硬编码 bug、outcome 残留 bug 均被实测暴露→已改） | ✅ |
| 第7课 schema_check 自测 | 6 例 | 6/6 | 6/6 | ✅ |
| T1.4 干跑回归（真 LLM） | 六条指令 0.2 档 | 可行→EXECUTING | S1–S4 放行→完成；S5 两条模型自行拒绝（与第7课一致） | ✅ |
| 对照 12 格（真 LLM，0.2/0.8 两档） | 6 陷阱×关/开×2 档 | 拦截与预判一致 | 0.2 接下 2/6、0.8 接下 3/6（均 B 区间）；开审计 2/2 与预判一致（T5→①、T6→②） | ✅ |
| 突袭（真 LLM） | T6 指令无上限 4 轮兜底 | 记录循环/调用/终止方式 | 循环2/调用2/回注后改口终止（无限重试未复现，如实记录） | ✅ |

## Error Log

| 时间戳 | 错误 | 尝试 | 处理 |
|--------|------|------|------|
| 2026-10-19 14:55 | 首次 PPT 提取调用被会话中断，结果未记录 | 1 | 重跑提取，23 页全文到手 |
| 2026-10-19 16:19 | 八发首跑 3/10：占据判据沿用教学判据「栅格值≥50」，本平台 map_gt 调色板相反（254=自由/0=占据） | 1 | 取 make_gt_map.py L38–52 源码为据，改「栅格值 < 50」＋PGM y 翻转；变更登记①；重跑 10/10 |
| 2026-10-19 16:21 | 冒烟(b) 拒绝案断言失败：REPORTING 日志 result 硬编码"完成" | 1 | outcome 变量随三出口如实记录；重跑五例全过 |

## 5-Question Reboot Check

| 问题 | 答案 |
|------|------|
| Where am I? | 阶段1 与阶段3 干跑数据**全部完成**（八发/冒烟/回归/12格/突袭）；剩课堂项：截图录像、孪生链（GUI＋扫描）、实车 |
| Where am I going? | 阶段2 孪生链（需 /scan 扫描流）→ 阶段4 实车 → 课堂补截图/录像 → 阶段5 归档提交 |
| What's the goal? | 规划-审计-执行分离闭环：四规则八发全中 ✓、12 格对照数据 ✓（课堂补录像）、实车/孪生三段式汇报（课堂） |
| What have I learned? | 见 findings.md（平台调色板、0.2/0.8 幻觉分布、回注改口、阻塞清单只剩 GUI＋扫描） |
| What have I done? | 见本文件三个 Session 记录 |
