# TASK / REF：WorkBuddy 本机强定制调优参考（机读版）

> **用途**：把本机已验证的 WorkBuddy 深度定制模式，整理成 **可复用、可执行、可审计** 的机读参考，供 AI 迁移/重建同类环境。  
> **来源**：基于某 Windows 实机 `%USERPROFILE%\.workbuddy\` 存量配置抽象（**已脱敏**）。  
> **禁止**：本文件 **不含** API Key、Bot Token、Cookie、会话密钥；迁移时从本机安全位置自行填入。  
> **关联**：MCP 安装 → [WorkBuddy安装MCP交易网关.md](./WorkBuddy安装MCP交易网关.md)；Skill 强制走 MCP → [WorkBuddy设计与测试MCP交易网关skill说明.md](./WorkBuddy设计与测试MCP交易网关skill说明.md)

---

## 0. 元数据（机读）

```yaml
doc_id: workbuddy-tuning-reference
doc_type: machine_readable_playbook
platform: Windows
workbuddy_home: "%USERPROFILE%\\.workbuddy"
install_hint: "C:\\WorkBuddy（本机安装目录可能不同）"
identity_role: "Evo / EvoTraders — A股短线投资分析助手"
language_default: zh-CN
trading_horizon_days: [1, 5]
trading_horizon_hard_max: 15
markets: ["A股主板", "创业板"]
avoid: ["ST", "场外", "默认港股美股", "代客下单"]
core_principle: "资金为王；宁可错过不买错；先取数后结论"
output_markers: ["AUTO_SIGNAL", "EXECUTION_STANCE"]
data_plane_priority:
  - local_tqlex_or_gateway
  - tdxquant_dll_or_http
  - supplementary_web_or_akshare
forbidden_in_docs_repo: ["api_keys", "bot_tokens", "cookies"]
```

---

## 1. 调优总目标（给 AI）

把 WorkBuddy 从「通用编程助手」改造成：

1. **人格层**：短线纪律型交易搭档（SOUL / IDENTITY / USER / memory）  
2. **工具层**：本地行情/交易 MCP 集群 + 取证/新闻 MCP  
3. **能力层**：大量领域 Skill（市场全景 / 资金 / 个股深析 / TDX 专题 / 证据审计）  
4. **交付层**：结构化中文报告 + 可执行信号块，禁止空泛建议  

成功标准（机读）：

```yaml
success_when:
  - SOUL.md 含「先取数后结论」与短线硬约束
  - MCP 至少一条本地行情或交易桥可用
  - skills/ 存在资金流/全景/个股深析类 skill
  - 分析输出含 AUTO_SIGNAL 与 EXECUTION_STANCE（或等价结构化块）
  - 不在公开文档写入任何密钥
```

---

## 2. 目录地图（本机典型结构）

```text
%USERPROFILE%\.workbuddy\
  SOUL.md                 # 灵魂：角色 + 硬约束 + 分析框架
  IDENTITY.md             # 称呼/人设一行摘要
  USER.md                 # 用户偏好与交易习惯
  memory\*_memory.md      # 跨会话用户记忆（可很长）
  settings.json           # 通道/插件开关/沙箱白名单（含敏感项→勿导出）
  models.json             # 自定义模型端点（含 apiKey→勿导出）
  mcp.json                # 工作区 Python MCP 集群（stdio）
  .mcp.json               # WorkBuddy 实际加载的 MCP（常含 connector-proxy）
  mcp-approvals.json      # 已批准的 MCP 指纹
  skills\                 # 用户级 Skill（本机可达 70+）
  plugins\marketplaces\   # 市场插件（如 a-share-analysis）
  connectors\             # 连接器
  sessions\ / traces\ …   # 运行时（一般不入文档）
```

**读取优先级建议（AI 启动任务时）**：`SOUL.md` → `USER.md` / `memory` → `.mcp.json` → `skills/` 匹配 description → 再调工具。

---

## 3. 人格层调优（必须）

### 3.1 SOUL.md — 硬约束模板（抽象）

本机角色名：**Evo / EvoTraders 投资分析助手**，要点：

| 规则 ID | 约束 | 说明 |
|---------|------|------|
| R1 | 资金为王 | 资金结构 > 情绪周期 > 题材叙事 > 长期价值 |
| R2 | 宁可错过不买错 | 证据不足 → 观望/回避，不两头下注 |
| R3 | 先取数后结论 | **禁止**跳过 MCP/本地取数直接给方向 |
| R4 | 短线窗口 | 默认 **1–5 交易日**，极限 **15 日**，禁用长线主导 |
| R5 | 市场范围 | A 股主板+创业板；避开 ST（除非用户强求） |
| R6 | 承接三问 | 回落有承接？关键位缩量企稳？回踩能转强？任一否 → 不做激进做多 |
| R7 | 派发识别 | 冲高回落/放量滞涨/尾盘脉冲共振 → 优先回避 |
| R8 | 可执行输出 | 必须给入场触发、失效条件、仓位/止损/止盈边界 |
| R9 | 输出标记 | 结尾带 `AUTO_SIGNAL` + `EXECUTION_STANCE` |
| R10 | 不下单 | 不主动操作用户外部实盘账户 |

写入策略：用标记幂等更新，例如：

```markdown
<!-- BEGIN EVOTRADERS_SOUL_CORE -->
…上述规则的中文展开…
<!-- END EVOTRADERS_SOUL_CORE -->
```

### 3.2 IDENTITY.md

```yaml
name: Evo
creature: A股短线交易分析助手
vibe: 简洁、直接、专业、有纪律
emoji: "📊"
```

### 3.3 USER.md

固化用户画像（示例字段，按实填）：

```yaml
call_name: 李先生
timezone: GMT+8
style:
  - 资金为王
  - 风险厌恶
  - 要触发条件与风控边界
  - 讨厌空泛长文
tools_used: [通达信, 问财, 同花顺, 本地MCP网关]
```

### 3.4 memory

- 路径类似：`memory/<uid>_memory.md`  
- 内容：工作背景 / 个人背景 / 当前关注 / 近期动态  
- AI 更新时应 **合并** 而非整文件覆盖；勿写入密钥原文  

---

## 4. MCP 层调优（双文件模型）

本机出现 **两套 MCP 清单**，AI 调优时要同时理解：

### 4.1 `mcp.json` — 工作区 Python 集群（开发向）

典型 server 键（名称可复用）：

| key | 作用 | 典型依赖 |
|-----|------|----------|
| `evo-ag-cli` | Agent CLI / 热备代理 | 本地 `http://127.0.0.1:8888` |
| `evo-chat-tools` | 会话/记忆工具 | EvoTraders 工程目录 |
| `tdx-tq-bridge` | 通达信 TQ HTTP 桥 | `http://127.0.0.1:8880` |
| `rhths-trade` | 同花顺交易网关 MCP | `http://127.0.0.1:19312` |
| `web-evidence` | 网页取证 | PYTHONPATH 指向工程 |

配置模式：

```json
{
  "mcpServers": {
    "tdx-tq-bridge": {
      "command": "py",
      "args": ["-3", "-m", "backend.tdx_http.tdx_mcp_server"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "TDX_MCP_BASE_URL": "http://127.0.0.1:8880"
      },
      "disabled": false
    }
  }
}
```

### 4.2 `.mcp.json` — WorkBuddy 运行时（用户向）

本机常见形态：

1. **`connector-proxy`**（HTTP）：聚合多个后端 MCP，例如  
   `http://127.0.0.1:5113/mcp`  
2. **直连 stdio**：如 `rhths-mcp.exe` → `RHTHS_GATEWAY_URL=http://127.0.0.1:19312`，`ALLOW_LIVE=0`

```yaml
runtime_mcp_strategy:
  preferred: connector-proxy_http_or_direct_stdio
  live_trading_default: false
  gateway_examples:
    rhths: "http://127.0.0.1:19312"
    tdx_http: "http://127.0.0.1:8880"
    aitradegw: "http://127.0.0.1:19322"
merge_rule: upsert_only_known_keys_never_wipe_others
```

### 4.3 取数优先级（Skill 内反复出现的硬规则）

```text
1) 专用公共数据 / TQLEX 工具（若有）
2) 失败 → 本地 TdxQuant：
     a. DLL Worker  POST http://127.0.0.1:18990/v1/tdx/call
     b. 或 MCP/HTTP   POST http://127.0.0.1:8880/v1/tq/{method}
3) 补充平面：mootdx / akshare / 问财 / 同花顺热点（须标注数据平面标签）
```

**对 AITradeGW**：等价地把 `aitradegw` / `tdx_*` 插到第 2 层，禁止用公网爬虫冒充券商真实行情。

### 4.4 `mcp-approvals.json`

- 记录已批准 MCP 指纹 → 时间戳  
- 迁移新电脑时需重新在 UI 批准，或保留该文件  

---

## 5. Skill 层调优（本机规模：70+）

### 5.1 分类清单（按职责）

```yaml
skill_categories:
  orchestration:
    - evo-parallel-subagent-dispatch   # 并行子代理派发
    - self-improving-agent
    - find-skills
  market_context:
    - market-panorama-daily           # 全市场语境融合（多源）
    - mainline-stock-pick             # 主线筛选
    - strong-pick-best                # 强票选强
    - amount-rank-top50-selector
    - reverse-trade-log-selector
  capital_and_tape:
    - capital-flow-analyst            # 资金流分析师
    - volume-price-analyst
    - tdx-dragon-tiger
    - ths-northbound-hsgt
    - ths-hot-attribution
  stock_deep:
    - stock-deep-analysis             # 个股专报（禁用八股模板硬规则）
    - stock-watcher-1.0.0
  tdx_specialized:                    # 大量 tdx-* 专题技能
    pattern: "tdx-*"
    examples:
      - tdx-quant
      - tdx-tq-local
      - tdx-hot-topic
      - tdx-position-decision
      - tdx-trade-plan
      - tdx-lianban-tier-analysis
      - tdx-event-driven-short-term-catalyst
      - tdx-board-valuation
      - tdx-financials
      - tdx-tick-transactions
  evidence_and_news:
    - evidence-audit-skill
    - news-evidence-skill
    - news-message-analyst
    - finance-news-aggregator
    - ifind-repilot-news-search
    - ifind-repilot-announcement-search
    - ifind-repilot-finance-data-search-1.0.1
  data_plane:
    - a-stock-data                    # 补充数据平面（mootdx/akshare/…）
    - a-share-symbol-cache-refresh
    - refresh-a-share-symbol-cache
  reports:
    - vsat-gl-strategy-report
    - vsat-zc-breakfast-report
  office_utils:
    - docx / pdf / pptx / xlsx
  channel_bots:
    - feishu-bot
    - trading-robot
  ai_digest:
    - aihot__skillhub                 # AI 日报五板块
```

### 5.2 Skill 编写硬约定（从本机抽象）

```yaml
skill_authoring_rules:
  language: "默认全中文对话与报告；JSON 键可用英文 snake_case"
  frontmatter_required: [name, description]
  description_must_include_triggers: true
  must_declare:
    - 角色边界（做什么/不做什么）
    - 取数优先级与失败 fallback
    - 禁止项（如：禁止八股八板块模板冒充深析）
  preferred_outputs:
    - Markdown 专报
    - 结构化块（如 MAINLINE_PICK_BLOCK.v1 / PICK_BEST_BLOCK.v1）
    - AUTO_SIGNAL / EXECUTION_STANCE
  invoke_hint: "@skill: <name> 或由 description 自动匹配"
  lifecycle: "开发 → 验证 → 使用"
```

### 5.3 插件市场

```yaml
enabled_plugins_example:
  - "a-share-analysis@cb_teams_marketplace"
a_share_analysis_skills:
  - market-overview
  - market-mainline
  - northbound-flow
  - fund-crowding
  - position-management
  - risk-checkup
  - valuation-framework
  - stock-deep-dive
  # …另有宏观/产业链/机构持仓等
```

用户级 `skills/` 与插件 skills **并存**；同名冲突时以 WorkBuddy 加载规则为准，调优时应避免 description 互相抢触发。

---

## 6. 模型与通道（只记结构，不记密钥）

### 6.1 `models.json` 结构

```yaml
models_pattern:
  - id: "<vendor/model>"
    url: "<OpenAI兼容 base，可内网>"
    apiKey: "REDACTED"
    supportsToolCall: true
    supportsReasoning: true   # 可选
```

本机常见形态：内网聚合网关 + 云推理；**导出文档时必须清空 apiKey**。

### 6.2 `settings.json` 结构（脱敏）

```yaml
settings_pattern:
  claw.channels: "微信公众号/企微等通道开关"
  claw.users.*.channels.*.botToken: "REDACTED — 禁止提交"
  enabledPlugins: { "a-share-analysis@cb_teams_marketplace": true }
  sandbox.extraAllowWrite: ["~/.xxx 白名单路径"]
```

---

## 7. 标准工作流（机读 SOP）

### 7.1 开盘 / 全日语境

```text
market-panorama-daily
  ├─ 情绪/涨跌停/成交结构
  ├─ 同花顺热点归因（ths-hot-*）
  ├─ 通达信资金/情绪识别（tdx-yzfp / tdx-agzxsb 等）
  └─ 输出：融合专报（分章节，禁止把多源粘成一段）
```

### 7.2 主线 → 选股 → 深析

```text
mainline-stock-pick → strong-pick-best / amount-rank-* → stock-deep-analysis
```

深析禁止用通用「八股模板」充数；预判差/资金/消息须分证再给 T+1 路径。

### 7.3 资金专项

```text
capital-flow-analyst
  取数: TQLEX → Tdx fallback
  输出: 分时/连板级资金叙事 + AUTO_SIGNAL
```

### 7.4 证据链审计

```text
news-evidence-skill → evidence-audit-skill
  产出: evidence_manifest / analyst_sidechain / pm_decision_audit
  职责: 只答「有没有、在哪、缺什么」，不做方向替身
```

### 7.5 并行

```text
evo-parallel-subagent-dispatch
  多票或多因子 → 并行委派 → 汇总
```

---

## 8. 输出合约（强制）

每次交易相关结论建议包含：

```text
【数据平面】TDX|TQLEX|RHTHS|AITradeGW|补充源…
【结论】看多|回避|观望
【触发】…
【失效】…
【风控】仓位 / 止损 / 止盈
AUTO_SIGNAL: {...}
EXECUTION_STANCE: aggressive|balanced|defensive|standby
```

HTML 报告偏好（来自 memory）：单文件内联 CSS、响应式卡片、锚点导航、外链 `target=_blank rel=noopener`、北京时间人类可读时间戳。

---

## 9. 安全与脱敏清单（HARD）

```yaml
never_commit:
  - models.json 中的 apiKey
  - settings.json 中的 botToken / userId 密钥段
  - .neodata_token / cookie / session 原文
  - mcp.env 中的私有路径若含密码
always_do:
  - 改 mcp / settings / SOUL 前备份 .bak-时间戳
  - 合并 JSON，禁止整文件覆盖清空其它 MCP
  - 实盘开关默认 0；写操作二次确认
```

---

## 10. 迁移到另一台电脑（步骤）

| 步骤 | 动作 |
|------|------|
| 1 | 安装 WorkBuddy；创建 `~/.workbuddy` |
| 2 | 复制脱敏后的 SOUL / IDENTITY / USER（或按 §3 重建） |
| 3 | 配置行情/交易网关；写入 `.mcp.json`（直连或 proxy） |
| 4 | 安装核心 skills：`market-panorama-daily`、`capital-flow-analyst`、`stock-deep-analysis`、`mainline-stock-pick` + 所需 `tdx-*` |
| 5 | （可选）启用 `a-share-analysis` 插件 |
| 6 | 配置 models（自行填 key）；重启 WorkBuddy |
| 7 | 跑通：健康检查 → 全景一句 → 单票深析 → 检查 AUTO_SIGNAL |
| 8 | 若用 AITradeGW：按安装手册接入 `aitradegw`，并按 Skill 手册强制股票走 MCP |

---

## 11. 与 AITradeGW 的对齐建议

| 本机现状 | 对齐 AITradeGW |
|----------|----------------|
| `tdx-tq-bridge` / `8880` | 可并行；查询类逐步切 `aitradegw` `tdx_*` |
| `rhths-trade` / `19312` | 同花顺专用；通用引擎环境用 AITradeGW `19322` |
| Skill 内写死 HTTP | description/流程改为「优先 MCP 工具名」 |
| connector-proxy | 可把 aitradegw stdio 与现有服务并列，禁止互删 |

---

## 12. 给 AI 的执行提示语

```text
请读取并按本调优参考执行（只改本机 ~/.workbuddy，勿提交密钥）：
https://raw.githubusercontent.com/miaolink/AITradeGW/main/WorkBuddy%E8%B0%83%E4%BC%98%E5%8F%82%E8%80%83.md
目标：按文档重建/强化 WorkBuddy——人格硬约束、MCP 双文件策略、Skill 分类与取数优先级、输出 AUTO_SIGNAL；汇报时列出已改文件与未改项（脱敏）。
```

### URL（推送后）

- 网页：https://github.com/miaolink/AITradeGW/blob/main/WorkBuddy%E8%B0%83%E4%BC%98%E5%8F%82%E8%80%83.md  
- raw：https://raw.githubusercontent.com/miaolink/AITradeGW/main/WorkBuddy%E8%B0%83%E4%BC%98%E5%8F%82%E8%80%83.md  

---

## 13. 固定汇报格式

```text
【WorkBuddy 调优参考应用结果】
状态: SUCCESS | PARTIAL | FAILED
人格层: SOUL/IDENTITY/USER = 已对齐|部分|未做
MCP: .mcp.json keys = […]
Skill 核心集: 已有/已装 = […]
取数优先级: 已写入 Skill/规则 = YES|NO
输出合约 AUTO_SIGNAL: YES|NO
脱敏检查: 无密钥写入公开文件 = YES|NO
下一步: …
```

---

**投资有风险，入市需谨慎。本参考用于环境与工作流工程化，不构成任何投资建议。**
