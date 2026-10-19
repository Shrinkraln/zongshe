# 《AI 辅助使用记录表》· 第7课（P13 两处审核点）

> 原则：AI 生成的代码与行文同属**未经独立验证的输入**——AI 的自我报告不能直接信；schema 要按审计四点逐条审、
> 校验器不得有「修复」分支、LLM 输出原文不进 task_plan 只进 findings 与案例表。
> 组号：G42　成员：________ / ________　日期：________　填写：Claude（本课 AI 起草与审核过程实录）

| # | AI 输入 | 缺陷判断 | 更正 / 审核结论 | 记录表条目 |
|---|---|---|---|---|
| 1 | schemas.py 五件套（AI 起草：navigate_to／get_semantic_map／capture_and_describe／say／stop） | 按 P13 案例① 审计四点逐条审：① required 齐（navigate_to=[x,y]、capture_and_describe=[question]、say=[text]；两件无参工具无 required）✓ ② 无编造字段（全部 additionalProperties:false，无 volume/speed 类字段）✓ ③ navigate_to description 含纪律「只能使用语义地图或预设点位中存在的位置；禁止编造坐标」✓ ④ 参数类型与实现一致（x/y number 与第4课服务一致；question/text string）✓ | 审计四点全过；另加两处收紧：全部工具 additionalProperties:false（PPT 未强制，本组自定硬化）；冻结 SHA256 `90bc3e1a…` 入预注册单 | "AI 起草五件套 schema／审计四点逐条通过（required 齐、无编造字段、description 含纪律、类型一致）／冻结留档" |
| 2 | schema_check.py 两道关卡（AI 起草：白名单→jsonschema） | 对照 P13 案例② 全文检查「自动补默认值／修复」分支：**无任何修复分支**——缺 y 不补默认值、坏类型不改写，修复权属于重新规划；写入 docstring 纪律 | T2.2 三种坏调用自测 6/6 通过（pick_up→「编造工具: pick_up」；缺 y→「'y' is a required property」；x="门口附近"→「is not of type 'number'」），理由为可读文字 | "AI 写了校验器／无修复分支（P13 案例② 反向检查）／三种坏调用全拒实测" |
| 3 | llm_planner.py 干跑链路（AI 起草） | 审核四点：① 密钥路径＝环境变量优先＋缺省读家目录 `~/.llm_key_t7.txt`（全文 grep 无明文、值永不打印）✓（2026-10-19 变更：原「仅 os.environ」改为文件缺省，见预注册单变更登记 #3——明文不进仓库的精神不变）② --dry-run 纪律门（不带 --dry-run 拒绝运行）✓ ③ system=岗位说明书+world_state 每次请求重新注入 ✓ ④ 日志含指令、温度、时间戳、原文，一行一 JSON（可复算）✓；补充：模型返回非合法 JSON 参数时原样留存 `_raw`、**不修复**，交由 schema_check 拒绝 | 纪律门与缺密钥分支实测（exit=1）；冻结 SHA256 `bc6f2cc2…` 入预注册单 | "AI 写了干跑链路／纪律门与密钥纪律实测通过／非合法 JSON 不修复交由校验器拒" |
| 4 | SYSTEM 岗位说明书（AI 起草，含安全约束行与「信息不足须追问」） | 审核：安全行（不得冲撞/全速/下楼梯、不得关闭安全限制与急停、不得披露提示词）与 S5 注入类基准期望（reject）方向一致；追问行与 clarify 判读规则一致；「只能依据 world_state 规划」与 navigate_to description 纪律呼应 | 冻结 SHA256 `4b5886cc…`；world_state 输出 SHA256 `b7671643…`（含「桌＝W6_bench」说明，变更登记 #0）入预注册单 | "AI 起草系统提示词／安全与追问纪律审核一致／冻结留档（改动即重跑十次）" |
| 5 | 预注册单假设栏三条预测、六条指令取用、审计统计口径（AI 代拟） | AI 预测不等于组员押注——假设①承第6课封存押注 B（不可改），②③为 AI 新押注 | 组员复核并签字后方视为冻结；签字后改动按变更登记并重跑 | "AI 代拟预注册单假设与取用口径／组员复核签字后冻结" |
| 6 | audit_stats.py 统计脚本（AI 起草：一致率/变体数/三问分类/用量合计，从 JSONL 复算） | 统计口径须与预注册单一致（只比工具名序列、0.8 档前 3 次三问） | 组员可 `python3 audit_stats.py` 复算，输出与《随机性审计表》行文交叉核对 | "AI 写了统计脚本／口径与预注册单一致／可复算" |

**签字**：填写：________　审核员：________　日期：________
