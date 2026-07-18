# CLI 使用说明（aitradegw.exe）

`aitradegw.exe` 是**本机**命令行客户端：通过安装目录旁的 **HTTP 网关**（默认 `http://127.0.0.1:19322`）访问本地行情与交易能力。

适合 PowerShell 脚本、计划任务、本机调试；与 [Cursor / Codex MCP](./CURSOR.md) 共用同一网关。  
**不用 QMT、不用券商特殊权限**；走行情软件 **标准 API**，非 PyGUI 点屏。

> 安装与图形界面操作见 [安装指南](./USER-INSTALL.md)、[图形控制台](./GUI.md)。AI 对话式用法见 [AI 交易示例](./AI交易示例.md)。

---

## 一、适用场景

| 适合 | 不适合 |
|------|--------|
| 本机 PowerShell / 批处理 / 计划任务 | 未安装网关、未配置行情引擎目录的电脑 |
| 本机对账、定时拉持仓、脚本自动化 | 替代 MCP 做跨机器 AI 对话（请用 MCP HTTP，联系作者） |
| 与 GUI、MCP 共用同一台「交易机」 | 在无行情环境的云服务器上直接跑 CLI |

---

## 二、准备（本机）

1. 图形控制台 **服务** 页 → **启动网关**（状态变绿）
2. 需要交易时：**启动交易** 并登录 **交易客户端**
3. 使用完整路径或加入 PATH，例如：

```powershell
$bin = "C:\Program Files\AITradeGW\bin"
& "$bin\aitradegw.exe" health
```

4. 检查连通：

```powershell
& "$bin\aitradegw.exe" health --pretty
& "$bin\aitradegw.exe" version
```

---

## 三、全局选项

| 选项 | 说明 |
|------|------|
| `--json` | 输出 JSON（默认开启） |
| `--pretty` | 格式化 JSON，便于阅读 |
| `--gateway-url URL` | 临时指定网关（默认 `http://127.0.0.1:19322`） |

环境变量：

| 变量 | 默认 | 说明 |
|------|------|------|
| `TDX_GATEWAY_URL` | `http://127.0.0.1:19322` | 网关地址（须指向**本机**） |
| `TDX_ALLOW_LIVE` | `0` | 设为 `1` 才允许实盘 |

---

## 四、系统命令

```powershell
aitradegw health          # 网关与行情核心连接
aitradegw status          # 连接状态
aitradegw probe           # 轻量行情探针
aitradegw catalog         # 网关 API 路由列表
aitradegw version         # 版本号
aitradegw system initialize   # 初始化 TQ 连接
aitradegw system close        # 关闭连接
```

### 通用 `call`（覆盖全部 59 个 TdxQuant API）

任意 `/v1/*` 路由均可直接调用，适合脚本集成或未单独封装子命令的接口：

```powershell
# POST + JSON body
aitradegw call POST /v1/market/stock_info --body '{"stock_list":["000001.SZ"]}'

# 从文件读取 body
aitradegw call POST /v1/market/data --body-file req.json

# GET
aitradegw call GET /v1/system/status
```

图形控制台 **CLI** 页提供等价快捷测试。

---

## 五、行情查询

```powershell
# 快照（可多只股票）
aitradegw market snapshot --stocks 000001.SZ --stocks 600000.SH

# K 线
aitradegw market data --stocks 000001.SZ --period 1d --count 30

# 证券搜索
aitradegw market match 平安

# 交易日列表（get_trading_dates，market 暂固定 SH）
aitradegw market trading-dates --market SH --start 20220101 --count 10
aitradegw market trading-dates --market SH --start 20250101 --end 20251231 --count -1

# 调用客户端功能（exec_to_tdx，须行情客户端已开）
aitradegw market exec "http://www.treeid/code_000001"
aitradegw market exec --url "http://www.treeid/zb_MACD"
aitradegw market exec "http://www.treeid/ZXG"

# 更多行情子命令
aitradegw market stock-info --stocks 000001.SZ
aitradegw market divid-factors --stock 000001.SZ --start 20200101 --count 10
aitradegw market ipo-info
aitradegw market relation --stock 000001.SZ
aitradegw market pricevol --stocks 000001.SZ
aitradegw market gb-info --stocks 000001.SZ
aitradegw market refresh-cache
aitradegw market subscribe-list
```

> 交易日列表需先在客户端下载上证指数（999999）盘后数据。详见 [通达信官方 get_trading_dates](https://help.tdx.com.cn/quant/docs/markdown/ctx.stock.md/mindoc-1h10q7i3702rk.html)。

> `exec_to_tdx` 可在客户端内打开指定股票、指标、版面等；功能串以 `http://www.treeid` 开头。详见 [通达信量化平台官方说明](https://help.tdx.com.cn/quant/docs/markdown/ctx.stock.md/mindoc-1h85iq443j44c.html)。

---

## 六、板块 / 财务 / 公式 / 消息

```powershell
# 板块
aitradegw sector list
aitradegw sector user
aitradegw sector stocks --block 880001

# 财务（需先在客户端下载数据包）
aitradegw financial data --stocks 000001.SZ

# 公式
aitradegw formula get-all --formula-type 0

# 客户端消息
aitradegw message send --title "test" --content "hello"
```

未单独封装的接口一律用 `aitradegw call POST /v1/...`。

---

## 七、交易查询

```powershell
# 交易账户句柄
aitradegw trade account

# 资金
aitradegw trade asset --account-id 0

# 持仓
aitradegw trade positions --account-id 0

# 当日委托
aitradegw trade orders --account-id 0
```

---

## 八、下单与撤单

**默认均为模拟（dry-run）**，不会真实成交。

### 模拟

```powershell
aitradegw trade buy --account-id 0 --stock 000001.SZ --volume 100 --price 10.5
aitradegw trade sell --account-id 0 --stock 000001.SZ --volume 100
aitradegw trade cancel --account-id 0 --order-id 12345
```

### 实盘（须显式开启，风险自负）

```powershell
$env:TDX_ALLOW_LIVE = "1"
aitradegw trade buy --account-id 0 --stock 000001.SZ --volume 100 --price 10.5 --live --confirm
```

须同时满足：`TDX_ALLOW_LIVE=1`、命令行 `--live`、`--confirm`（或在 GUI **交易** 页勾选确认）。

---

## 八（附）、计划任务与盘后数据

下载通达信官网汇总包到设置页「安装目录」下的 `vipdoc`（需网关运行；定时任务还需交易日判定）。

```powershell
aitradegw schedule vipdoc-status                    # 远端 / 本地更新时间
aitradegw schedule vipdoc-download --packages day,fin   # 下载（未变则跳过）
aitradegw schedule vipdoc-download --packages day --force  # 强制重下
aitradegw schedule list                             # 列出计划任务
aitradegw schedule enable --id vipdoc-day-daily --on    # 启用日线定时
aitradegw schedule enable --id vipdoc-fin-daily --on    # 启用财务定时
aitradegw schedule run --id vipdoc-day-daily        # 立即执行
aitradegw schedule trading-day                      # 今天是否交易日
aitradegw schedule trading-day --date 20260718
```

包对应：`day`=`hsjday.zip` → `vipdoc`；`fin`=`tdxfin.zip` → `vipdoc/cw`；`gp`=`tdxgp.zip` → `vipdoc/cw`。  
AI / MCP 一句话启用日线+财务定时：`tdx_schedule_enable_vipdoc`（见 [AI 交易示例](./AI交易示例.md)）。

---

## 九、与 MCP 的区别

| | CLI | MCP（Cursor / Codex） |
|---|-----|------------------------|
| 谁调用 | 你、本机脚本 | AI Agent |
| 程序 | `aitradegw.exe` | `aitradegw-mcp.exe` |
| 典型用途 | 自动化、定时、调试 | 对话查行情、查持仓、更新盘后数据 |
| 下单 | 支持（须 dry-run / 实盘确认） | 当前以**查询**为主，下单建议用 GUI 或 HTTP |

二者都访问**同一台机器**上的网关 `:19322`；CLI 须在本机执行。

配置 MCP 见 [AI 接入指南](./CURSOR.md) · 示例话术见 [AI 交易示例](./AI交易示例.md)。

---

## 十、常见问题

| 现象 | 处理 |
|------|------|
| 连接拒绝 | **服务** 页启动网关；检查 **设置** 中行情引擎目录 |
| 交易查不到 | 启动并登录 **交易客户端** |
| 实盘被拦截 | 设置 `TDX_ALLOW_LIVE=1` 并加 `--live --confirm` |
| JSON 乱码 | 使用 `--pretty` 或 `ConvertFrom-Json` |

---

**投资有风险，入市需谨慎。**
