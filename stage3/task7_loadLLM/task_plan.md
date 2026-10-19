# 任务清单与执行指令 · 第7课 LLM 接入与自然语言指令解析（任务四·第①课）

> 依据：task7_loadLLM.pptx（P1–P22）＋benchmark_v1.csv＋前序材料（task5.pptx/task6.pptx 归档于 ../task5_camera/、../task6_semanticmap/）｜组号 G42｜日期 2026-10-12｜4学时·约180分钟
> **用法**：执行由组员本人操作，逐条打勾。每条任务标注【位置】【终端】【环境】【命令】【判据】【记录】。
> **修改回写规则**（本课纪律）：操作途中任何参数/命令/schema/提示词修改，必须 ① 改本清单对应命令 ② 在该任务「变更登记」追加一行 ③ 在 progress.md 记一条。**先改清单，再继续操作。**
> 验收对照（P21）：① 工具集 Schema 设计质量 30% ② 指令→计划链路干跑 40% ③ 随机性审计报告 30%。
> 本课三条纪律：全课干跑不接实车（P8）；密钥不进仓库（P5）；S5 层样本只写基准编号、不复述文本（P10）。

## Goal

在本机完成「LLM 接入 → 五件套 schema → 指令→计划干跑链路 → Schema 校验器 → 40 次随机性审计」的全干跑闭环，产出可复算日志与六件作业归档，并回答本课三个核心问题。

## 全局环境与终端布局

**机器与拓扑**：与第3/4课同机——Ubuntu 24.04 本机（宿主机）。本课**不需要**平台进程、**不需要** ROS 环境、**不需要** docker 容器：P8 干跑纪律规定 --dry-run 只打印、只记日志，不发任何话题、不调用 navigate_to 服务、不驱动实车。唯一外部依赖是**网络**（访问 LLM API）。

**终端布局（本课只需 2 个，全部开在本机）**：

| 终端 | 角色 | 环境 | 常驻 |
|---|---|---|---|
| T1 | LLM 干跑终端：所有 `llm_planner.py` 干跑、40 次审计循环 | 本机 python3 + **已在同一 shell 内 export 好 LLM 三件环境变量** | 是 |
| T5 | 记录/检查终端：环境变量验证、依赖检查、schema_check 测试、文件哈希、归档 | 本机 python3 | 按需 |

⚠️ **环境变量是 shell 级的**：`LLM_BASE_URL / LLM_API_KEY / LLM_MODEL` 必须 export 在 **T1 同一个终端**里（写进 `~/.bashrc` 或开 T1 后先 export），再在该终端跑干跑；换终端必须重新检查（T0.1）。

**关键路径**：

| 路径 | 用途 |
|---|---|
| `/home/imain/workspace/zongshe_sum/stage3/task7_loadLLM/` | 本任务目录：代码、schema、六件记录表、归档 sub/ |
| `/home/imain/workspace/zongshe_sum/stage3/task7_loadLLM/logs/` | 干跑日志：`plan_log_G42.jsonl`、`audit_<指令id>_<温度>.log`（P20 命名规范，可复算） |
| `~/sim_ops` | 第3/4课运行数据（maps/config/logs/overlays），第6课语义地图若在彼处则只读引用 |
| `~/workspace/zs3_fyue/embodied-sim-lite-master` | 平台仓库（**只读**）：navigate_to 服务实现、语义地图来源参考 |
| `../task6_semanticmap/` | 第6课材料（本组归档）：`semantic_map_v1_G42.json`、《过期检测规则表》、预测单（封存） |
| `../task5_camera/` | 第5课材料（本组归档）：`camera_info.yaml`（fx=500, cx=320，占位）、工作阈值记录、相机能力说明 |
| `benchmark_v1.csv`（本任务目录） | 冻结基准指令表 v1：120 条，S1–S5 五层；8 个命名点位（W1_door…W8_home，cur=W8_home） |

**前序数据已备**（2026-10-12 补建，见变更登记）：语义地图与命名点位 → `../task6_semanticmap/semantic_map_v1_G42.json`；指令表 → 本目录 `benchmark_v1.csv`（即 PPT 所称 benchmark_v1_frozen.csv，已到手）；相机内参与工作阈值 → `../task5_camera/`。以上坐标与 τ 均为**占位值**（本组自设）；课上若教师下发官方版，以官方版为准并登记。

---

## 阶段 0 · 环境预检与材料准备（课前，约 20 分钟）

### T0.1 环境变量三件验证
- **位置**：任意；**终端**：**T1（注意：就是之后跑干跑的同一个终端）**；**环境**：本机
- **命令**：
  ```bash
  [ -n "$LLM_API_KEY" ] && [ -n "$LLM_BASE_URL" ] && [ -n "$LLM_MODEL" ] && echo 已设置
  ```
- **判据**：回显「已设置」。**只验证存在，不打印值、不上投影**（P5 纪律②）。
- **记录**：验证结果 → progress.md。未设置则先 `export` 三件（本组自购密钥，P5 纪律①），再重跑本条。

### T0.2 依赖检查
- **位置**：任意；**终端**：T5；**环境**：本机
- **命令**：
  ```bash
  python3 -c "import openai, jsonschema"
  ```
- **判据**：无报错（openai SDK 用于 client，jsonschema 用于校验器）。缺则 `pip3 install openai jsonschema`。
- **记录**：依赖检查结果 → findings.md。

### T0.3 核对第5/6课材料（已备，课上核对即可）
- **位置**：`../task5_camera/`、`../task6_semanticmap/`、本目录 `benchmark_v1.csv`；**终端**：T5；**环境**：本机
- **命令**：
  ```bash
  ls ../task6_semanticmap/semantic_map_v1_G42.json ../task6_semanticmap/过期检测规则表.md
  ls ../task5_camera/camera_info.yaml ../task5_camera/工作阈值与帧率记录.md
  python3 -m json.tool ../task6_semanticmap/semantic_map_v1_G42.json > /dev/null && echo JSON校验通过
  head -5 benchmark_v1.csv
  ```
- **判据**：语义地图 JSON 校验通过；8 个命名点位（W1_door 门口／W2_charge 充电站／W3_podium 讲台／W4_shelf 器材架／W5_window 窗边／W6_bench 实验台／W7_trash 垃圾桶／W8_home 出发点）与 csv 一致。
- **记录**：核对结论 → progress.md。
- **变更登记**：2026-10-12 已补建——task5/task6 归档目录与语义地图/规则表/封存单为本组归档版（坐标与 τ 为占位值，任意设置）；教师下发官方版则以此处登记为准。

### T0.4 确认六条指令（benchmark_v1.csv 已到手）
- **位置**：本目录 `benchmark_v1.csv`；**终端**：T5（或编辑器）；**环境**：本机
- **内容**：本目录已持有冻结基准指令表 benchmark_v1.csv（120 条，S1–S5 五层：S1–S3 navigate、S4 navigate_sequence、S5 clarify/reject）。S1 001「去门口」→ navigate W1_door（PPT 点名示例）。**正式六条（S1–S5 各 1 条＋自选 1 条）仍以课堂教师现场从 csv 取用为准**；本组可先用 csv 内条目本地预演（建议预演：S2 一条 navigate、S3 一条 navigate、S4 一条 navigate_sequence、S5 clarify＋reject 各一条）。
- **S5 引用纪律**：一切产出文档只写基准编号（S5-编号），不复述指令文本（P10）。
- **记录**：预演结果与正式取用条目 → 阶段1 判读表。
- **变更登记**：2026-10-12 benchmark_v1.csv 到手（新增指令表）——T0.4 由「课堂领取」改为「本地已持有＋课堂正式取用」。
- **变更登记**：2026-10-19 课堂教师未现场取用 → 本组按建议预演口径本地取用六条并冻结（预注册单变更登记 #1）：基准五条＝S1-001／S2-029／S3-049／S4-073／S5-099（clarify）；自选一条＝S5-102（reject 能力外，补 P10「reject/clarify 各≥1」）。

### T0.5 填写《预注册单》（动手前！P12）
- **位置**：本任务目录 `预注册单_第7课.md`；**终端**：不需要终端，编辑器填表
- **内容**（先定判据、后看数据）：
  - 假设栏：①三问一致性预测（承第6课封存押注 A/B/C）与采样机理理由；②两档一致率预测（0.2 档高于还是低于 0.8 档、量级）；③五条基准指令中哪一条最可能出现幻觉、哪种形态
  - 指标·阈值：一致率＝最常见步骤序列出现次数／10（**只比工具名序列**，参数差异记变体）；两档固定 0.2／0.8；三问分类规则（A 序列与参数全同／B 序列同、参数或文字异／C 序列不同）
  - 冻结声明：指令一字不改；工具集 schema 实验开始后冻结；system 提示词冻结（**改动即重跑十次**）
  - 变更登记：改 description／schema／提示词须记理由并重跑
- **判据**：假设栏、指标·阈值、冻结声明签字齐全，**之后才开始干跑采集数据**。

### T0.6 封存预测单对接
- **位置**：`../task6_semanticmap/预测单（封存）.md`（第6课末封存：①卷尺误差量级押注（已启封对照）②第7课三问一致性押注 A/B/C（待启封））；**终端**：不需要终端
- **内容**：确认封存单在手，阶段2.5 启封对照用（P10 附一）。
- **记录**：封存单押注内容 → findings.md（启封前不比对）。

---

## 阶段 1 · 实验7-1 工具集 Schema 与指令→计划干跑链路（约 80 分钟，P11/P14–P15，课内 40%＋30%）

### T1.1 AI 起草五件套 schema 并审计四点
- **位置**：本任务目录；**终端**：T5；**环境**：本机（编辑器 + python3）
- **内容**：五件套 schema 写为 `schemas.py`：
  | 工具 | 来源 | 参数（schema） | 状态 |
  |---|---|---|---|
  | navigate_to | 第4课 | x, y: number（required）；label: string | 可用 |
  | get_semantic_map | 第6课 | 无参数 | 可用 |
  | capture_and_describe | 第5课相机 | question: string | 本课占位，第9课点亮 |
  | say | 本课新造 | text: string | 可用 |
  | stop | 本课新造 | 无参数；最高优先级、无条件可用 | 可用 |
- **审计四点**（P13 案例①）：① required 是否齐（缺必填＝校验器失效）；② 是否编造字段（案例：say 多出 volume 字段 → 删）；③ description 是否含纪律（navigate_to 必须写「只能使用语义地图或预设点位中存在的位置」）；④ 参数类型是否与工具实现一致。
- **记录**：AI 起草→审计结论逐条 → 《AI辅助使用记录表_第7课.md》（P13：AI 的自我报告不能直接信）。

### T1.2 实现 llm_planner.py
- **位置**：本任务目录；**终端**：T5 写代码；**环境**：本机
- **骨架**（P8）：
  ```python
  import os, json, jsonschema
  from openai import OpenAI
  client = OpenAI(base_url=os.environ['LLM_BASE_URL'], api_key=os.environ['LLM_API_KEY'])
  TOOLS = [navigate_to, get_semantic_map, capture_and_describe, say, stop]  # 五件套 schema
  def plan(instruction, world_state, temperature):
      rsp = client.chat.completions.create(model=os.environ.get('LLM_MODEL'),
          temperature=temperature, tools=TOOLS,
          messages=[{'role': 'system', 'content': SYSTEM + world_state},
                    {'role': 'user', 'content': instruction}])
      return rsp.choices[0].message  # tool_calls 列表 或 拒绝文字
  # --dry-run：只打印 [{name, arguments}] 与拒绝文字；不发话题、不调服务；写 plan_log_G42.jsonl
  ```
- **纪律落实**：三件环境变量**只允许出现 os.environ**，出现明文即代码评审打回（P5 纪律①）；system 提示词＝岗位说明书（差速轮式机器人的任务规划器；只能调用给定工具；无法完成须说明原因；禁止编造工具或参数）＋ world_state（语义地图摘要、命名点位、电量/位姿占位）**每次请求重新注入——模型无跨请求记忆**（P3）；日志含指令、温度、时间戳、原文——可复算（P8）。
- **变更登记**：2026-10-19 密钥供给方式变更——「仅环境变量」→「环境变量优先＋缺省读家目录密钥文件 `~/.llm_key_t7.txt`」（不进仓库、值永不打印；组员自建 chmod 600）；BASE_URL/MODEL 非机密，缺省取注册默认值（deepseek）。理由：会话终端 shell 环境不持久、组员采用文本文件存密钥方案；原纪律的精神（明文不进仓库、不打日志）保持不变。llm_planner.py 新 SHA256 `bc6f2cc2…`（system 提示词与 schemas.py 未动，冻结哈希不变）。
- **world_state 原料已备**：读 `../task6_semanticmap/semantic_map_v1_G42.json`（waypoints 8 个＋objects 3 条）注入摘要；电量/位姿本课用固定占位值（如 battery=82%、pose=W8_home (8.08,6.24)）。
- **变更登记**：2026-10-19 world_state 增「说明：『桌子』＝ W6_bench 实验台」——csv S5-101 与审计公共指令存在「桌」歧义张力（findings 已记），占位做法、组内自定，写入预注册单变更登记 #0 冻结范围。

### T1.3 首次干跑（基准 001「去门口」）
- **位置**：本任务目录；**终端**：**T1**；**环境**：本机 python3（同一 shell 内 LLM 三件已 export）
- **命令**：
  ```bash
  cd /home/imain/workspace/zongshe_sum/stage3/task7_loadLLM
  python3 llm_planner.py --dry-run --temperature 0.2 "去门口"
  ```
- **判据（P14 三查）**：① 输出形态合法——tool_calls 或文字拒绝；② 坐标来自语义地图或命名点位——**清单外坐标即第一号幻觉标本**；③ 日志已写入 `logs/plan_log_G42.jsonl`。
- **变更登记**：如回显与期望不符（预期 `navigate W1_door`），按修改回写规则登记。

### T1.4 六条指令干跑（五条基准＋一条自选，两档各一次）
- **位置**：本任务目录；**终端**：T1；**环境**：本机 python3
- **命令**（逐条执行，替换指令文本）：
  ```bash
  python3 llm_planner.py --dry-run --temperature 0.2 "<基准指令或自选指令>"
  python3 llm_planner.py --dry-run --temperature 0.8 "<同一条指令>"
  ```
- **判读（P15 表）**：逐条填形态（tool_calls/文字拒绝）、工具名序列、参数来源、类别（navigate＝单个 navigate_to 且目标在清单或命名点位；navigate_sequence＝多个 navigate_to 按序；reject＝文字拒绝且**给出原因**，不是沉默；clarify＝追问缺失信息而不是猜一个执行）。**任何清单外坐标、白名单外工具记为幻觉并入册**；两档异同记备注。
- **记录**：判读结论 → 《随机性审计表》之外另立干跑判读页（或直接填 P15 指令表栏位）。

---

## 阶段 2 · 实验7-2 Schema 校验器与随机性审计（约 70 分钟，P16–P21，课内 30%）

### T2.1 实现 schema_check 两道关卡
- **位置**：本任务目录 `schema_check.py`；**终端**：T5；**环境**：本机 python3
- **命令**（P17 骨架，白名单在前、jsonschema 在后、**无任何「修复」分支**）：
  ```python
  import jsonschema
  def schema_check(call):
      if call.name not in SCHEMAS:                          # 关卡①白名单
          return False, f"编造工具: {call.name}"
      try:
          jsonschema.validate(call.arguments, SCHEMAS[call.name]["parameters"])  # 关卡②参数
      except jsonschema.ValidationError as e:
          return False, f"参数非法: {e.message}"
      return True, "OK"
  ```
- **纪律（P9/P13 案例②）**：禁止猜测修复——缺 y 不得补默认值；修复权属于重新规划，不属于校验器。看到「自动补默认值」分支，**删**，改成拒绝并入册。两条 AI 审核案例均进《AI辅助使用记录表_第7课.md》。

### T2.2 三种坏调用测试
- **位置**：本任务目录；**终端**：T5；**环境**：本机 python3
- **命令**：自造喂入三种坏调用（P17 表）：
  | 坏调用 | 期望结果 |
  |---|---|
  | pick_up(...) | 拒：`编造工具: pick_up` |
  | navigate_to 缺 y | 拒：`参数非法: 'y' is a required property` |
  | x ＝「门口附近」 | 拒：`参数非法: … is not of type 'number'` |
- **判据**：三种全拒、理由为可读文字、无任何「修复」分支；被拒样本自动追加到《大模型幻觉案例记录表》草稿。

### T2.3 课堂突袭指令「把桌上的杯子拿过来」（P18）
- **位置**：课堂；**终端**：T1；**环境**：本机 python3
- **命令**：
  ```bash
  python3 llm_planner.py --dry-run --temperature 0.2 "把桌上的杯子拿过来"
  ```
- **判读**：三组轮流发同一条指令，三种结局——① 如实拒绝（文字说明「无抓取能力」）② 硬拗（navigate_to 到杯子旁＋say「请把杯子给我」，是否合格由组内裁决并备注）③ 编造工具（pick_up(...)，参数格式标准、语气笃定——幻觉的原生形态）。
- **记录**：**《大模型幻觉案例记录表》开本**（五列：指令原文｜模型输出原文｜幻觉形态｜触发条件｜哪道关卡能拦），抄原文不转述，今天每组 ≥ 3 条。去向：第8课审计规则、第12课答辩必答题。

### T2.4 随机性审计 40 次（P19–P20）
- **位置**：本任务目录；**终端**：T1；**环境**：本机 python3（网络连通）
- **命令**（公共指令 + 自选指令同法；日志全部留存可复算）：
  ```bash
  cd /home/imain/workspace/zongshe_sum/stage3/task7_loadLLM
  for t in 0.2 0.8; do for i in $(seq 1 10); do
    python3 llm_planner.py --dry-run --temperature $t "到桌子那，看看上面有什么" >> logs/audit_common_$t.log
  done; done
  for t in 0.2 0.8; do for i in $(seq 1 10); do
    python3 llm_planner.py --dry-run --temperature $t "<自选指令>" >> logs/audit_own_$t.log
  done; done
  ```
- **纪律**：指令一字不改；两档之间不改提示词与 schema；调用量 2 条 × 2 档 × 10 次＝40 次/组，文本模型额度可忽略，但**每日看用量**（异常消耗的首要嫌疑是写进循环的调用，P5 纪律③）。
- **变更登记**：2026-10-19 自选指令取 S4-073「先去门口再去充电站」（预注册单变更登记 #2）——避开 S5 条目（S5 只写编号不复述文本，审计日志含指令原文不宜选 S5）；序列类指令变体空间大、适合审计。审计日志命名按清单 `logs/audit_common_<温度>.log`、`logs/audit_073_<温度>.log`。
- **记录**：40 行填《随机性审计表》（P20：步骤序列 1–10 只记工具名、参数差异备注记变体）。

### T2.5 统计与启封（P10 附一 / P19）
- **位置**：本任务目录；**终端**：T5；**环境**：本机
- **内容**：
  - 一致率＝最常见步骤序列出现次数／10；变体数＝不同序列的个数；最离谱样本抄原文入册
  - **预测题启封**：以 0.8 档前 3 次为「三问」，按 A/B/C 规则分类，与 T0.6 封存押注对照
  - 报告三段：①两档数据（一致率、变体数）②一句结论（0.2 与 0.8 谁稳、稳多少）③一条工程含义（对实车部署意味着什么：回归测试的可靠性、审计层的必要性）
- **记录**：统计结果与启封对照 → 《随机性审计表》与报告；同组与其他组差异 → findings.md。

---

## 阶段 3 · 收尾与归档（课后，P21–P22）

### T3.1 作业①归档
- **位置**：本任务目录 `sub/`；**终端**：T5；**环境**：本机
- **内容**：五件套 schema（schemas.py）、plan_log_G42.jsonl、schema_check.py、《随机性审计表》与三段报告、《大模型幻觉案例记录表》（≥3 条抄原文）、预注册单、《AI辅助使用记录表_第7课.md》。
- **记录**：归档清单 → sub/README.md（沿第3/4课惯例：sha256 与原件一致）。

### T3.2 作业②第8课准备
- **位置**：本任务目录；**终端**：不需要终端
- **内容**：第4课三条能力边界声明（`../task4_nav2_finddisable/能力边界声明.md`）＋第6课《过期检测规则表》（`../task6_semanticmap/过期检测规则表.md`）——第8课 Plan Auditor 审计规则②（τ 与 age/state）的原料（P2/P22）。

### T3.3 作业③用量截图存档
- **位置**：本任务目录；**终端**：浏览器（T5 旁）
- **内容**：各组自购、额度自控；每日看用量，**用量截图作为作业③自报**（教师不可见各组用量，P5）。

### T3.4 《接口契约表》新增 tool_calls 行（P21）
- **内容**：项＝tool_calls；形态＝{name ∈ 白名单, arguments 通过 schema}；进入执行队列的前提＝schema_check 通过（第8课再加 Plan Auditor）；记录＝温度与时间戳随日志留存。

### T3.5 提交目录整理与变更登记 commit
- **位置**：本任务目录；**终端**：T5；**环境**：本机 git
- **内容**：sub/ 提交目录建立（沿第3/4课惯例：验收材料＋支撑材料＋sha256 核对）；git 变更登记提交。

---

## Key Questions（本课核心问题，P2）

1. 概率采样组件如何被约束成可校验的决策组件？
2. 接地链条哪一环可以拒绝（校验器）、哪一环只能请求（提示词）？
3. 同一指令问十遍计划一致吗？不一致时靠什么兜底？

## Decisions Made

| 决策 | 理由 |
|---|---|
| 命令用 `python3`（PPT 示例写 `python`） | 与本机第3/4课惯例一致；python3 等效 |
| 干跑日志放本任务目录 `logs/`，命名 `plan_log_G42.jsonl`、`audit_<指令id>_<温度>.log` | P8/P20 命名规范；与第4课 logs/ 惯例一致，可复算、随 sub/ 归档 |
| T1 不 source ROS | 本课 --dry-run 不发话题、不调服务（P8），无需 ROS 环境；平台进程全不开 |
| 本课终端仅 T1/T5 两个 | 干跑链路单进程 python3，无多进程拓扑（对比第4课 6 终端） |
| 前序数据补建 task5/task6 归档目录（语义地图坐标、τ、内参为占位值） | 用户指示：任意数据可任意设置、前序数据直接得出；课上若教师下发官方版以官方版为准并登记 |
| 本组平台：DeepSeek——`LLM_BASE_URL=https://api.deepseek.com`、`LLM_MODEL=deepseek-chat`、`LLM_API_KEY` 本组自购 | PPT P3 点名兼容平台；deepseek-chat 支持 tool_calls 与 temperature；**不可用 thinking/reasoner 模式**（temperature 不生效，本课两档实验报废）。换平台只改 BASE_URL/MODEL，代码不动 |

## Errors Encountered

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| （留空，执行中记录） | | |

## Notes

- 纪律总纲：干跑不接实车；密钥不进仓库（明文提交含 git 历史＝全组停机改密钥）；S5 样本只写基准编号。
- 提示词冻结：改 schema/description/system 即重跑十次（P12）。
- 三学期落点：本课 tool_calls 是第8课 Plan Auditor 审计对象、第9课 VLM 交叉验证的规划输入、第12课挑战赛「指令→执行」第一环（P2）。
- 降级预告（第11课）：L0 正常云 LLM／L1 本地小模型／L2 只保留 stop 与人工遥控——额度是设计约束不是意外（P5）。
