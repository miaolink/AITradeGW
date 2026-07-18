# AI 交易示例（Cursor / Codex）

在 **Cursor** 或 **Codex** 中配置 MCP 服务 **`aitradegw`** 后，用自然语言即可查行情、查资金、查持仓。

- **默认以查询为主**；MCP 工具侧重读操作。  
- **实盘下单**建议在图形控制台 **[交易](./GUI.md)** 页操作，并遵守模拟/实盘确认规则。  
- MCP 配置见 **[AI 接入指南](./CURSOR.md)**；命令行脚本见 **[CLI 使用说明](./CLI使用说明.md)**。

---

## 使用前（建议先说给 AI）

| 你可以对 AI 说 | MCP 工具 |
|----------------|----------|
| 「网关连上了吗？」 | `tdx_health` |
| 「行情核心正常吗？」 | `tdx_status` / `tdx_probe` |
| 「有哪些接口可以用？」 | `tdx_catalog` |

---

## 一、查行情

| 你可以对 AI 说 | MCP 工具 | 说明 |
|----------------|----------|------|
| 「000001 现在什么价？」 | `tdx_market_snapshot` | 快照、涨跌幅等 |
| 「平安银行五档多少？」 | `tdx_market_snapshot` | 含买卖盘口 |
| 「000001 最近 30 日日线」 | `tdx_market_data` | 默认可传代码、周期 |
| 「代码里带『银行』的有哪些？」 | `tdx_match_stk` | 证券搜索 |

**示例对话：**

> 用户：帮我看下平安银行现在多少钱，五档分别多少。  
> AI：调用 `tdx_market_snapshot`，解读现价与五档。

> 用户：000001 最近一个月日 K 大概什么走势？  
> AI：`tdx_market_data`，用文字概括趋势（不构成投资建议）。

---

## 二、查账户与持仓

| 你可以对 AI 说 | MCP 工具 | 说明 |
|----------------|----------|------|
| 「我现在有多少资金？」 | `tdx_trade_asset` | 须已登录交易客户端 |
| 「帮我列一下持仓」 | `tdx_trade_positions` | 成本、盈亏、数量 |
| 「今天有哪些委托？」 | `tdx_trade_orders` | 当日委托列表 |
| 「交易账户是哪个？」 | `tdx_trade_account` | 账户句柄 |

**示例对话：**

> 用户：帮我看下资金和持仓，重点有没有亏损超过 10% 的。  
> AI：`tdx_trade_asset` → `tdx_trade_positions`，汇总解读。

> 用户：今天有没有未成交的买单？  
> AI：`tdx_trade_orders`，筛选未完成委托。

---

## 三、板块与公式

| 你可以对 AI 说 | MCP 工具 |
|----------------|----------|
| 「有哪些板块？」 | `tdx_sector_list` |
| 「我的自定义板块有哪些？」 | `tdx_sector_user` |
| 「列出本地公式」 | `tdx_formula_get_all` |
| 「查一下财务数据」（复杂参数） | `tdx_financial_data` |

---

## 三（附）、盘后数据与计划任务

| 你可以对 AI 说 | MCP 工具 |
|----------------|----------|
| 「盘后日线 / 财务数据是不是最新？」 | `tdx_vipdoc_status` |
| 「帮我更新盘后日线和财务包」 | `tdx_vipdoc_download` |
| 「帮我开启盘后日线与财务的定时自动下载（交易日盘后拉取，网关保持运行）」 | `tdx_schedule_enable_vipdoc` |
| 「今天是不是交易日？」 | `tdx_trading_day` |
| 「有哪些计划任务？启用日线定时了吗？」 | `tdx_schedule_list` |
| 「立刻跑一次日线下载任务」 | `tdx_schedule_run_day` |
| 「立刻跑一次财务下载任务」 | `tdx_schedule_run_fin` |

**示例对话：**

> 用户：看看本地盘后数据更新时间，如果落后就下载日线。  
> AI：先 `tdx_vipdoc_status`，再按需 `tdx_vipdoc_download`（远端未变会跳过）。

> 用户：帮我开启盘后日线与财务的定时自动下载，交易日盘后拉取，网关我会保持运行。  
> AI：调用 `tdx_schedule_enable_vipdoc`（默认约 16:10 日线、16:20 财务，仅交易日；可用 `tdx_schedule_list` 核对是否已启用）。

图形界面也可在 **[计划任务](./GUI.md)** 页操作；命令行见 [CLI 使用说明](./CLI使用说明.md) 的 `schedule` 子命令。

---

## 四、组合场景（推荐话术）

### 4.1 开盘前检查

> 「检查网关是否正常 → 查资金与持仓 → 看今日已有委托，全部只读。」

工具链：`tdx_health` → `tdx_trade_asset` → `tdx_trade_positions` → `tdx_trade_orders`

### 4.2 盯盘 + 解读

> 「000001、600519 现价和涨跌幅报一下，再各拉 20 根日 K 简单说说走势。」

工具链：`tdx_market_snapshot` → `tdx_market_data`

### 4.3 选股辅助

> 「搜名称里带『新能源』的股票，挑前 5 只报现价。」

工具链：`tdx_match_stk` → `tdx_market_snapshot`

### 4.4 持仓复盘

> 「列出持仓，对每只报现价和当日涨跌幅。」

工具链：`tdx_trade_positions` → 对每只 `tdx_market_snapshot`

---

## 五、下单说明

当前 MCP **以查询为主**。若需 AI 驱动下单：

1. 优先在 **图形控制台 [交易](./GUI.md)** 页手动操作（默认模拟）  
2. 进阶用户可通过 HTTP 网关写操作（须 `TDX_ALLOW_LIVE` + 二次确认），联系作者获取说明  

**示例（仅查询，推荐）：**

> 用户：我现在适合买吗？先别下单，只帮我查资金和 000001 行情。  
> AI：只调用 `tdx_trade_asset`、`tdx_market_snapshot`，**不执行**写操作。

---

## 六、工具速查

| 分类 | 工具名 |
|------|--------|
| 系统 | `tdx_health`、`tdx_status`、`tdx_probe`、`tdx_catalog` |
| 行情 | `tdx_market_snapshot`、`tdx_market_data`、`tdx_match_stk`、`tdx_trading_dates`、`tdx_stock_info`、`tdx_divid_factors`、`tdx_ipo_info`、`tdx_relation`、`tdx_pricevol`、`tdx_gb_info`、`tdx_kzz_info`、`tdx_subscribe_list`、`tdx_refresh_cache` |
| 交易查询 | `tdx_trade_account`、`tdx_trade_asset`、`tdx_trade_positions`、`tdx_trade_orders` |
| 板块/公式 | `tdx_sector_list`、`tdx_sector_user`、`tdx_sector_stocks`、`tdx_financial_data`、`tdx_formula_get_all`、`tdx_formula_zb` |

---

## 七、常见错误

| 现象 | 处理 |
|------|------|
| MCP 红 / 无 tools | [服务](./GUI.md) 页启动网关；检查 `mcp.json` 路径 |
| 查持仓失败 | 启动 **交易客户端** 并登录 |
| 工具超时 | 重启网关；检查行情引擎目录 |

更多配置：[AI 接入指南](./CURSOR.md) · 安装：[安装指南](./USER-INSTALL.md)

---

**投资有风险，入市需谨慎。本软件为技术工具，不构成任何投资建议。**
