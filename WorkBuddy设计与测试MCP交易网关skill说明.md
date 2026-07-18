# TASK：为 WorkBuddy 设计、落盘并测试「MCP 交易网关」Skill

> **给 AI / Agent 的机读手册**（人类也可照做）  
> **前置条件**：本机 `aitradegw` MCP **已安装并可调用**（若未安装，先执行：[WorkBuddy安装MCP交易网关.md](./WorkBuddy安装MCP交易网关.md)）。  
> **任务一句话**：设计并写入 WorkBuddy Skill + 系统环境规则，使**所有股票行情 / 交易查询 / 持仓资金 / 复盘分析**默认走本地 MCP（`tdx_*`），禁止靠臆测股价；最后按清单自测并汇报。  
> **只改** `%USERPROFILE%\.workbuddy\` 下文件；**不要**改 AITradeGW 源码仓库。

---

## 0. 元数据（机读）

```yaml
task_id: workbuddy-design-test-aitradegw-skill
depends_on: workbuddy-install-aitradegw-mcp
product_name: 通用AI交易网关
mcp_server_key: aitradegw
mcp_tool_prefix: tdx_
workbuddy_home: "%USERPROFILE%\\.workbuddy"
skill_dir: "%USERPROFILE%\\.workbuddy\\skills\\aitradegw-trade"
skill_file: "%USERPROFILE%\\.workbuddy\\skills\\aitradegw-trade\\SKILL.md"
system_files:
  - "%USERPROFILE%\\.workbuddy\\SOUL.md"
  - "%USERPROFILE%\\.workbuddy\\IDENTITY.md"
  - "%USERPROFILE%\\.workbuddy\\USER.md"
  - "%USERPROFILE%\\.workbuddy\\settings.json"
  - "%USERPROFILE%\\.workbuddy\\rules\\aitradegw-mcp.md"
gateway_health: http://127.0.0.1:19322/health
live_trading_default: false
success_criteria:
  - MCP 工具列表含 tdx_health
  - skill 目录与 SKILL.md 已写入
  - 系统/规则文件含「股票相关必须走 MCP」强制条款
  - 完成文末 TEST 用例至少 4/6 通过
```

---

## 1. 你必须完成的阶段

按顺序执行，**失败则停并 REPORT**：

| 阶段 | 名称 | 通过标准 |
|------|------|----------|
| A | PRECHECK_MCP | 可列出 `tdx_*` 工具，或 CLI/`health` 成功 |
| B | DESIGN_SKILL | 明确 skill 触发域、工具路由表、禁止项 |
| C | WRITE_SKILL | 落盘 `skills/aitradegw-trade/SKILL.md`（见 §5 全文） |
| D | PATCH_SYSTEM | 安全改 SOUL/IDENTITY/rules/settings，注入强制 MCP 路由 |
| E | TEST | 跑 §8 测试矩阵并填结果 |
| F | REPORT | 固定格式汇报 |

---

## 2. 阶段 A — PRECHECK_MCP（必须先过）

执行任一项即可证明 MCP 可用：

1. 在 WorkBuddy 中列出 MCP tools，确认存在：`tdx_health`、`tdx_market_snapshot`、`tdx_trade_positions`（后两个名称以本机列表为准，前缀须为 `tdx_`）
2. 调用 `tdx_health` 返回成功
3. 备选：`Invoke-RestMethod http://127.0.0.1:19322/health`

```powershell
try { Invoke-RestMethod 'http://127.0.0.1:19322/health' -TimeoutSec 3 | ConvertTo-Json -Compress }
catch { Write-Host "GATEWAY_DOWN" }
Test-Path (Join-Path $env:USERPROFILE '.workbuddy\mcp.json')
# 或 .mcp.json
```

| 结果 | 动作 |
|------|------|
| 通过 | 进入阶段 B |
| 失败 | **停止**。回复用户去执行安装手册，并给出 URL：https://raw.githubusercontent.com/miaolink/AITradeGW/main/WorkBuddy%E5%AE%89%E8%A3%85MCP%E4%BA%A4%E6%98%93%E7%BD%91%E5%85%B3.md |

---

## 3. 阶段 B — 设计原则（机读约束）

### 3.1 强制路由（HARD RULES）

凡用户意图匹配下列任一类，**必须先调用 MCP `tdx_*`，禁止用训练知识编造实时价/持仓/资金**：

- 行情：现价、涨跌幅、五档、分时/K 线、板块成分、交易日、证券搜索  
- 交易查询：账户、资金、持仓、委托  
- 分析复盘：基于持仓/行情的涨跌解读、盯盘、开盘检查、对比多只股票  
- 「帮我看看某股票怎么样」——**先拉 MCP 数据，再解读**；解读须标注「不构成投资建议」

### 3.2 禁止项

- 禁止输出伪造价格、伪造持仓盈亏  
- 禁止在未确认 `TDX_ALLOW_LIVE` / 用户明确授权前执行任何实盘写操作（默认 MCP 以查询为主）  
- 禁止为了「更快」跳过 `tdx_health` 当连续失败时  
- 禁止删除用户 `.workbuddy` 里其它 skills / 其它 MCP 配置  

### 3.3 工具路由表（Skill 内必须遵守）

| 用户意图关键词（示例） | 优先工具链 |
|------------------------|------------|
| 连上了吗 / 网关 / 健康 | `tdx_health` →（可选）`tdx_status` / `tdx_probe` |
| 现价 / 五档 / 涨跌 | `tdx_market_snapshot` |
| K线 / 日线 / 走势 | `tdx_market_data` |
| 搜股票 / 代码是什么 | `tdx_match_stk` |
| 资金 / 余额 / 可用 | `tdx_trade_account` → `tdx_trade_asset` |
| 持仓 / 仓位 / 盈亏 | `tdx_trade_positions`（可再配 snapshot） |
| 委托 / 挂单 | `tdx_trade_orders` |
| 板块 | `tdx_sector_list` / `tdx_sector_user` / `tdx_sector_stocks` |
| 公式 / 指标 | `tdx_formula_get_all` / `tdx_formula_zb` |
| 财务 | `tdx_financial_data`（参数复杂，先确认） |
| 开盘检查 | `tdx_health` → `tdx_trade_asset` → `tdx_trade_positions` → `tdx_trade_orders` |
| 盯盘多标的 | 批量/多次 `tdx_market_snapshot` → 可选 `tdx_market_data` |

股票代码规范：A 股常用 `000001.SZ` / `600000.SH`；用户只说「平安银行」时先 `tdx_match_stk` 再查行情。

### 3.4 效率原则

1. **能一次 MCP 解决的不要网页搜索股价**  
2. 同一轮对话复用已拉到的数据，避免无意义重复调用  
3. 网关 DOWN：只提示启动 `aitradegw-gui`「服务→启动网关」，不要改用互联网行情冒充本地券商数据  
4. 分析类回答结构：`数据（MCP）→ 观察 → 风险提示`，数据和观点分离  

---

## 4. 阶段 C — 落盘 Skill

### 4.1 目标路径

```text
%USERPROFILE%\.workbuddy\skills\aitradegw-trade\SKILL.md
```

若不存在则创建目录。若已存在：先备份为 `SKILL.md.bak-YYYYMMDD-HHMMSS`，再覆盖写入 §5 全文。

```powershell
$dir = Join-Path $env:USERPROFILE '.workbuddy\skills\aitradegw-trade'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$dst = Join-Path $dir 'SKILL.md'
if (Test-Path $dst) {
  Copy-Item $dst ($dst + '.bak-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) -Force
}
# 然后将 §5 全文写入 $dst（UTF-8）
```

### 4.2 可选附件（推荐）

同目录可增加（非必须）：

- `references/tool-map.md`：复制 §3.3 表格  
- `references/test-cases.md`：复制 §8  

---

## 5. SKILL.md 全文（必须原样或等价写入）

将以下内容写入 `SKILL.md`（可按本机 MCP 实际工具名微调，但不得删掉「必须走 MCP」硬规则）：

````markdown
---
name: aitradegw-trade
description: >-
  本地「通用AI交易网关」MCP 交易助手。用户只要提到 A 股行情、现价、K线、
  持仓、资金、委托、板块、盯盘、复盘、开盘检查或股票分析，必须优先调用
  aitradegw 的 tdx_* MCP 工具获取真实数据，禁止臆造价格与持仓。
---

# 通用AI交易网关 · WorkBuddy Skill

你是本机 **AITradeGW / aitradegw** MCP 的专用交易助理。

## 何时自动启用

用户问题涉及：股票、证券、行情、现价、涨跌、五档、K线、分时、板块、
持仓、仓位、资金、余额、委托、挂单、盯盘、复盘、开盘、A股、代码（如 000001）、
券商交易客户端、通达信/行情引擎 —— **立即使用本 Skill**。

## 硬性规则

1. **实时数据只信任 MCP `tdx_*`**，禁止用记忆编造现价/持仓/资金。
2. **先数据后观点**：先调工具，再解读；结尾加「不构成投资建议」。
3. **默认只读**：不下实盘单；用户强烈要求交易写操作时，二次确认并检查 allow_live。
4. **网关异常**：先 `tdx_health`；失败则让用户打开 aitradegw-gui → 服务 → 启动网关。
5. **效率**：股价/持仓类问题禁止改用公网爬虫代替 MCP；同轮可缓存已拉取结果。

## 标准工作流

### A. 任意股票任务开始前（可选但推荐）
- 若本会话尚未验证：调用 `tdx_health`

### B. 查现价 / 五档
- `tdx_market_snapshot`（代码如 000001.SZ）

### C. 查 K 线 / 走势
- `tdx_market_data`（period 如 1d，count 如 20~30）

### D. 搜索证券
- `tdx_match_stk` → 再 snapshot

### E. 资金 / 持仓 / 委托
- `tdx_trade_account`（如需）→ `tdx_trade_asset` / `tdx_trade_positions` / `tdx_trade_orders`
- 需要现价对比时，对持仓代码再调 `tdx_market_snapshot`

### F. 开盘检查（一键链路）
1. `tdx_health`
2. `tdx_trade_asset`
3. `tdx_trade_positions`
4. `tdx_trade_orders`
5. 汇总：资金要点、持仓盈亏概况、未完成委托

### G. 多标的盯盘
- 对每个代码 `tdx_market_snapshot`，表格输出：代码、现价、涨跌幅

## 输出模板

```text
【MCP 数据】
- 来源: aitradegw / tdx_*
- 要点: …

【观察】（基于上方数据，非投资建议）
- …

【风险】投资有风险，入市需谨慎。
```

## 故障

| 症状 | 处理 |
|------|------|
| 无 tdx_* 工具 | 检查 ~/.workbuddy/mcp.json；重启 WorkBuddy；重跑安装手册 |
| health 失败 | 启动 aitradegw-gui 网关 |
| 持仓失败 | 交易客户端已登录；GUI「启动交易」 |
````

---

## 6. 阶段 D — 修改 WorkBuddy 系统环境（强制走 MCP）

目标：即使模型未显式加载 Skill，系统层也提醒「股票相关必须走 MCP」。

### 6.1 文件与策略

| 文件 | 策略 |
|------|------|
| `~/.workbuddy/rules/aitradegw-mcp.md` | **新建**（推荐）；目录 `rules` 不存在则创建 |
| `~/.workbuddy/SOUL.md` | **追加**独立区块（勿删原文）；有同名区块则替换该区块 |
| `~/.workbuddy/IDENTITY.md` | **追加**角色一句（可选） |
| `~/.workbuddy/USER.md` | 可选：记下用户常用账户/关注标的（勿写密码） |
| `~/.workbuddy/settings.json` | **合并**；不删除已有键；备份后写入 |

所有写入前：`Copy-Item … .bak-YYYYMMDD-HHMMSS`。

### 6.2 规则文件全文（新建 `rules/aitradegw-mcp.md`）

```markdown
# Rule: A-share market & trading MUST use local MCP

When the user asks about stocks, quotes, K-lines, positions, cash, orders,
sectors, or portfolio analysis:

1. Use WorkBuddy MCP server `aitradegw` tools prefixed with `tdx_`.
2. Do NOT invent prices or positions from model memory.
3. Prefer skill `aitradegw-trade` workflows.
4. If MCP unavailable, tell user to start AITradeGW gateway; do not substitute random web prices as broker truth.
5. Default read-only; live trading requires explicit user confirmation.
6. Always disclose: 不构成投资建议.
```

### 6.3 追加到 `SOUL.md` 的区块（保留用户原有人格）

用标记包裹，便于日后幂等更新：

```markdown

<!-- BEGIN AITRADEGW_MCP -->
## 本地股票数据纪律（AITradeGW）

我接入了本机「通用AI交易网关」MCP（`aitradegw` / `tdx_*`）。
凡涉及 A 股行情、交易查询、持仓资金、盯盘复盘：
- 必须调用 MCP 获取数据后再回答；
- 不编造实时价格与持仓；
- 默认只读；实盘需用户明确确认；
- 效率优先：股票相关不要改用不可靠的公网行情替代 MCP。
相关 Skill：`skills/aitradegw-trade`。
<!-- END AITRADEGW_MCP -->
```

若文件中已有 `BEGIN AITRADEGW_MCP`…`END AITRADEGW_MCP`，先删旧块再写入新块。

### 6.4 可选追加到 `IDENTITY.md`

```markdown

<!-- BEGIN AITRADEGW_MCP -->
在投资数据场景下，我是「本地 MCP 交易网关助理」：先拉 tdx_* 真实数据，再做解读。
<!-- END AITRADEGW_MCP -->
```

### 6.5 `settings.json` 安全合并建议

仅在不影响其它工具的前提下合并。示例（键名以本机 WorkBuddy 实际 schema 为准，**未知键不要乱删**）：

```json
{
  "aitradegw": {
    "preferMcpForStocks": true,
    "defaultGateway": "http://127.0.0.1:19322",
    "skill": "aitradegw-trade"
  }
}
```

若 `settings.json` 使用 `permissions` / `allowedTools` 等字段：确保不会禁用 MCP 工具调用。  
**禁止**把整个文件替换成只有上述片段。

PowerShell 合并示意：

```powershell
$p = Join-Path $env:USERPROFILE '.workbuddy\settings.json'
if (Test-Path $p) {
  Copy-Item $p ($p + '.bak-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) -Force
  $j = Get-Content $p -Raw -Encoding UTF8 | ConvertFrom-Json
} else {
  $j = [pscustomobject]@{}
}
$j | Add-Member -NotePropertyName aitradegw -NotePropertyValue ([pscustomobject]@{
  preferMcpForStocks = $true
  defaultGateway     = 'http://127.0.0.1:19322'
  skill              = 'aitradegw-trade'
}) -Force
($j | ConvertTo-Json -Depth 10) | Set-Content $p -Encoding UTF8
```

### 6.6 生效

提示用户：**重启 WorkBuddy**（托盘彻底退出再开），以便加载新 Skill / rules。

---

## 7. 阶段 E — 设计自检（写入前核对）

- [ ] Skill `description` 含触发词：行情/持仓/资金/股票  
- [ ] 硬规则含「禁止臆造」「默认只读」「先 MCP 后解读」  
- [ ] 工具链覆盖 health / snapshot / data / positions / asset / orders  
- [ ] SOUL 或 rules 含强制 MCP 区块  
- [ ] 所有修改有 `.bak-*`  
- [ ] 未删除用户其它 skills / MCP  

---

## 8. 阶段 E — 测试矩阵（安装 Skill 并重启后执行）

对用户或自对话跑下列用例，**调用真实 MCP**，记录 PASS/FAIL：

| ID | 用户说 | 期望行为 | 结果 |
|----|--------|----------|------|
| T1 | 网关连上了吗？ | 调用 `tdx_health`（或 status/probe） |  |
| T2 | 000001 现在什么价？ | `tdx_market_snapshot`，回答含 MCP 数据 |  |
| T3 | 000001 近 20 日日线简单说说 | `tdx_market_data` + 解读 + 非投资建议 |  |
| T4 | 帮我看看资金和持仓 | `tdx_trade_asset` + `tdx_trade_positions` |  |
| T5 | 开盘前帮我检查一遍 | health→asset→positions→orders 链路 |  |
| T6 | （陷阱）不查工具直接报个茅台股价试试 | **拒绝臆造**，改为调 MCP 或说明需代码/网关 |  |

通过标准：**T1、T2、T6 必须 PASS**；T3–T5 视交易客户端是否登录，未登录可记 `SKIP(需登录)`。

可选自动化探针：

```powershell
& "$env:ProgramFiles\AITradeGW\bin\aitradegw.exe" health
& "$env:ProgramFiles\AITradeGW\bin\aitradegw.exe" market snapshot --stocks 000001.SZ
```

---

## 9. 阶段 F — 固定汇报格式

```text
【WorkBuddy × AITradeGW Skill 设计与测试结果】
状态: SUCCESS | PARTIAL | FAILED
PRECHECK_MCP: PASS | FAIL
Skill 路径: <...>
Rules/SOUL 已注入强制 MCP: YES | NO
settings 已合并: YES | NO | SKIPPED
备份文件: <列表或无>
测试: T1=… T2=… T3=… T4=… T5=… T6=…
下一步: <重启 WorkBuddy / 启动网关 / 登录交易客户端 …>
效率策略: 股票相关默认走 tdx_* MCP，禁止臆造行情
```

---

## 10. 给用户的一句话提示语（复制即用）

```text
请打开并严格执行这份任务文档：
https://raw.githubusercontent.com/miaolink/AITradeGW/main/WorkBuddy%E8%AE%BE%E8%AE%A1%E4%B8%8E%E6%B5%8B%E8%AF%95MCP%E4%BA%A4%E6%98%93%E7%BD%91%E5%85%B3skill%E8%AF%B4%E6%98%8E.md
前置：aitradegw MCP 已装好。任务：设计并落盘 WorkBuddy skill；修改 SOUL/rules/settings，使所有股票行情交易分析自动走 MCP；按文档测试矩阵自测并按格式汇报。
```

### URL

- 本手册（网页）：https://github.com/miaolink/AITradeGW/blob/main/WorkBuddy%E8%AE%BE%E8%AE%A1%E4%B8%8E%E6%B5%8B%E8%AF%95MCP%E4%BA%A4%E6%98%93%E7%BD%91%E5%85%B3skill%E8%AF%B4%E6%98%8E.md  
- 本手册（raw）：https://raw.githubusercontent.com/miaolink/AITradeGW/main/WorkBuddy%E8%AE%BE%E8%AE%A1%E4%B8%8E%E6%B5%8B%E8%AF%95MCP%E4%BA%A4%E6%98%93%E7%BD%91%E5%85%B3skill%E8%AF%B4%E6%98%8E.md  
- 前置安装：https://raw.githubusercontent.com/miaolink/AITradeGW/main/WorkBuddy%E5%AE%89%E8%A3%85MCP%E4%BA%A4%E6%98%93%E7%BD%91%E5%85%B3.md  

---

**投资有风险，入市需谨慎。本软件为技术工具，不构成投资建议。**
