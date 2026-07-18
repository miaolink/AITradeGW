# TASK：为 WorkBuddy 安装并接入「通用AI交易网关」MCP

> **给 AI / Agent 的机读安装手册**（人类也可照做）  
> **任务一句话**：检测本机是否已安装交易网关；若已安装则安全写入 WorkBuddy MCP 配置；最后用健康检查确认可查行情/持仓。  
> **不要上传/改写本仓库源码**；只操作用户本机程序与 `%USERPROFILE%\.workbuddy\` 配置。

---

## 0. 元数据（机读）

```yaml
task_id: workbuddy-install-aitradegw-mcp
product_name: 通用AI交易网关
product_slug: AITradeGW
mcp_server_key: aitradegw
mcp_client: WorkBuddy
os: Windows
gateway_health: http://127.0.0.1:19322/health
mcp_mode: stdio
mcp_args: ["stdio"]
default_env:
  TDX_GATEWAY_URL: http://127.0.0.1:19322
  TDX_ALLOW_LIVE: "0"
config_candidates:
  - "%USERPROFILE%\\.workbuddy\\mcp.json"
  - "%USERPROFILE%\\.workbuddy\\.mcp.json"
bin_names:
  gui: aitradegw-gui.exe
  gateway: aitradegw-gateway.exe
  mcp: aitradegw-mcp.exe
  cli: aitradegw.exe
success_criteria:
  - mcp.exe 路径存在
  - gateway health HTTP 200 / ok
  - WorkBuddy mcp.json 含键 aitradegw 且 command 指向真实 mcp.exe
  - （可选）CLI: aitradegw health 成功
```

---

## 1. 你必须完成的目标

按顺序执行，**每一步通过再进入下一步**：

1. **DETECT**：本机是否已安装 AITradeGW（是否有 `aitradegw-mcp.exe`）
2. **RUNTIME**：HTTP 网关是否在跑（`http://127.0.0.1:19322/health`）
3. **CONFIG**：把 MCP 安全写入 WorkBuddy 配置（**合并**，禁止清空用户已有其它 MCP）
4. **VERIFY**：配置可解析；提示用户重启 WorkBuddy；用工具或 CLI 做一次探针
5. **REPORT**：用固定格式向用户汇报结果（见文末）

若 DETECT 失败：明确告诉用户下载安装包，并给出文档入口，**不要假装配置成功**。

---

## 2. DETECT — 检测本机是否已安装

在 PowerShell 中按下列候选路径查找 **`aitradegw-mcp.exe`**（取第一个存在的）：

```text
C:\Program Files\AITradeGW\bin\aitradegw-mcp.exe
C:\Program Files (x86)\AITradeGW\bin\aitradegw-mcp.exe
%LOCALAPPDATA%\Programs\AITradeGW\bin\aitradegw-mcp.exe
D:\AITradeGW\bin\aitradegw-mcp.exe
```

额外探测（推荐执行）：

```powershell
# 注册表安装目录（若有）
Get-ItemProperty 'HKLM:\Software\AITradeGW' -ErrorAction SilentlyContinue | Select-Object InstallDir, Version

# 进程是否在跑
Get-Process aitradegw-gui,aitradegw-gateway,aitradegw-mcp -ErrorAction SilentlyContinue |
  Select-Object Name, Id, Path

# Everywhere 搜索（可能较慢，前两步失败时再用）
Get-ChildItem -Path C:\,D:\ -Filter aitradegw-mcp.exe -Recurse -ErrorAction SilentlyContinue |
  Select-Object -First 5 FullName
```

### 判定

| 结果 | 动作 |
|------|------|
| 找到 `aitradegw-mcp.exe` | 记下绝对路径为 `$McpExe`；其同级目录应有 `aitradegw-gateway.exe`、`aitradegw-gui.exe` → 进入 §3 |
| 未找到 | **停止配置**。告知用户：请先安装「通用AI交易网关」，安装后再把本页 URL 发你继续。安装说明：https://github.com/miaolink/AITradeGW/blob/main/USER-INSTALL.md ；在线站：https://www.miaolink.cn/AITradeGW/index.php |

绿色包/自定义目录：用户若告知安装根目录 `$Root`，则 MCP 路径为：

```text
$Root\bin\aitradegw-mcp.exe
```

---

## 3. RUNTIME — 检测网关是否就绪

网关是 MCP 背后的 HTTP 服务，**默认端口 19322**。

```powershell
try {
  $r = Invoke-RestMethod -Uri 'http://127.0.0.1:19322/health' -TimeoutSec 3
  $r | ConvertTo-Json -Compress
} catch {
  Write-Host "GATEWAY_DOWN: $($_.Exception.Message)"
}
```

### 判定

| 结果 | 动作 |
|------|------|
| 能访问 health | 继续 §4 |
| 访问失败 | 请用户打开 **`aitradegw-gui.exe`** →「服务」页 → **启动网关**（状态变绿）。也可：`Start-Process "$Root\bin\aitradegw-gui.exe"`。启动后再测 health，最多等 15 秒重试 5 次 |

可选 CLI 探针（若存在 `aitradegw.exe`）：

```powershell
& "$Root\bin\aitradegw.exe" health
& "$Root\bin\aitradegw.exe" version
```

---

## 4. CONFIG — 写入 WorkBuddy MCP（安全合并）

### 4.1 配置文件位置（按优先级读写）

1. `%USERPROFILE%\.workbuddy\mcp.json`（优先，常见）
2. `%USERPROFILE%\.workbuddy\.mcp.json`（备选）

目录不存在则创建：`New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.workbuddy"`。

### 4.2 目标片段（将路径换成 DETECT 得到的真实路径）

JSON 中反斜杠必须写成 `\\`：

```json
{
  "mcpServers": {
    "aitradegw": {
      "command": "C:\\Program Files\\AITradeGW\\bin\\aitradegw-mcp.exe",
      "args": ["stdio"],
      "env": {
        "TDX_GATEWAY_URL": "http://127.0.0.1:19322",
        "TDX_ALLOW_LIVE": "0"
      }
    }
  }
}
```

说明：

- 服务键名固定用 **`aitradegw`**（或与现有文档一致时可用 `aitradegw-trade`，二选一，**全机只注册一个**）
- `args` 必须含 **`stdio`**（WorkBuddy 用子进程 stdio；不要误写成仅 HTTP）
- `TDX_ALLOW_LIVE` 默认 `"0"`：查询可用；实盘写操作需用户知悉风险后再改

### 4.3 合并规则（强制）

1. 若文件不存在：写入完整 JSON（仅含 `mcpServers.aitradegw`）
2. 若文件已存在：
   - 用 JSON 解析，保留其它 `mcpServers` 条目
   - **仅 upsert** 键 `aitradegw`
   - **禁止**删除、覆盖其它 MCP（如腾讯连接器、飞书等）
   - 写前备份：`mcp.json.bak-YYYYMMDD-HHMMSS`
3. 写完后用 `ConvertFrom-Json` 再读一遍，确认可解析

PowerShell 合并参考：

```powershell
$cfgPath = Join-Path $env:USERPROFILE '.workbuddy\mcp.json'
$mcpExe  = 'C:\Program Files\AITradeGW\bin\aitradegw-mcp.exe'  # <- 换成 DETECT 结果
if (-not (Test-Path $mcpExe)) { throw "MCP exe missing: $mcpExe" }

$dir = Split-Path $cfgPath
New-Item -ItemType Directory -Force -Path $dir | Out-Null

$obj = @{ mcpServers = @{} }
if (Test-Path $cfgPath) {
  Copy-Item $cfgPath ($cfgPath + ".bak-" + (Get-Date -Format 'yyyyMMdd-HHmmss')) -Force
  $obj = Get-Content -LiteralPath $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if (-not $obj.mcpServers) { $obj | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{}) -Force }
}

$entry = [pscustomobject]@{
  command = $mcpExe
  args    = @('stdio')
  env     = [pscustomobject]@{
    TDX_GATEWAY_URL = 'http://127.0.0.1:19322'
    TDX_ALLOW_LIVE  = '0'
  }
}
$obj.mcpServers | Add-Member -NotePropertyName aitradegw -NotePropertyValue $entry -Force
($obj | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath $cfgPath -Encoding UTF8
Write-Host "WROTE $cfgPath"
Get-Content -LiteralPath $cfgPath -Raw | ConvertFrom-Json | Out-Null
Write-Host "JSON_OK"
```

### 4.4 生效方式

修改后必须让用户 **完全退出并重启 WorkBuddy**（不只关窗口，托盘也退出），否则 MCP 列表可能不刷新。

---

## 5. VERIFY — 验收清单

按顺序勾选：

- [ ] `Test-Path $McpExe` 为 True  
- [ ] `Invoke-RestMethod http://127.0.0.1:19322/health` 成功  
- [ ] `%USERPROFILE%\.workbuddy\mcp.json`（或 `.mcp.json`）含 `mcpServers.aitradegw`  
- [ ] `command` 与 `$McpExe` 一致，且文件真实存在  
- [ ] 已提示用户重启 WorkBuddy  
- [ ] 重启后：在 WorkBuddy 中能看到 MCP / tools（名称含 `aitradegw` 或工具前缀 `tdx_`）  
- [ ] 试问：「网关连上了吗？」或「000001 现在多少钱？」——应调用 `tdx_health` / `tdx_market_snapshot` 一类工具  

可选确认工具名（查询类，安全）：

| 工具 | 用途 |
|------|------|
| `tdx_health` | 网关健康 |
| `tdx_status` | 连接状态 |
| `tdx_probe` | 行情探针 |
| `tdx_market_snapshot` | 行情快照 |
| `tdx_trade_positions` | 持仓（需交易客户端已登录） |

> 默认以 **查询** 为主；实盘下单需用户确认，且网关侧常需 `allow_live` / GUI 实盘开关。

---

## 6. 失败速查

| 现象 | 处理 |
|------|------|
| 找不到 mcp.exe | 未安装产品 → 引导 USER-INSTALL，不要写假路径 |
| health 失败 | GUI「服务」启动网关；检查 19322 被占用 |
| WorkBuddy 无 tools | 确认写的是 `.workbuddy\mcp.json`；JSON 合法；已彻底重启 |
| 查持仓失败 | 启动交易客户端并登录；服务页「启动交易」 |
| 改完配置被覆盖 | 合并时丢了其它键 → 从 `.bak-*` 恢复后再 upsert |
| Python / TQ 未就绪 | 引导 GUI「初始化」页环境检测（用户本机操作） |

---

## 7. 对用户的固定回报格式

完成后原样使用（填空）：

```text
【WorkBuddy × AITradeGW MCP 安装结果】
状态: SUCCESS | PARTIAL | FAILED
本机 MCP 程序: <绝对路径或 NOT_FOUND>
网关 health: OK | DOWN
配置文件: <mcp.json 路径>
是否合并保留其它 MCP: YES | NO | N/A
下一步: <重启 WorkBuddy / 去安装网关 / 启动网关 …>
验证建议: 重启后问我「帮我查一下 000001 现价」
```

---

## 8. 人类一键可用链接（把本 URL 发给 WorkBuddy / AI）

- **本任务手册（当前文档）**  
  https://github.com/miaolink/AITradeGW/blob/main/WorkBuddy%E5%AE%89%E8%A3%85MCP%E4%BA%A4%E6%98%93%E7%BD%91%E5%85%B3.md  
- 原始文本（便于 Agent `fetch`）  
  https://raw.githubusercontent.com/miaolink/AITradeGW/main/WorkBuddy%E5%AE%89%E8%A3%85MCP%E4%BA%A4%E6%98%93%E7%BD%91%E5%85%B3.md  
- **下一步（MCP 已装好后）**：设计 Skill + 强制股票走 MCP  
  https://raw.githubusercontent.com/miaolink/AITradeGW/main/WorkBuddy%E8%AE%BE%E8%AE%A1%E4%B8%8E%E6%B5%8B%E8%AF%95MCP%E4%BA%A4%E6%98%93%E7%BD%91%E5%85%B3skill%E8%AF%B4%E6%98%8E.md  
- **调优参考（人格/MCP/Skill 清单脱敏版）**  
  https://raw.githubusercontent.com/miaolink/AITradeGW/main/WorkBuddy%E8%B0%83%E4%BC%98%E5%8F%82%E8%80%83.md  
- 产品安装说明：https://github.com/miaolink/AITradeGW/blob/main/USER-INSTALL.md  
- Cursor/Codex 通用 MCP 说明：https://github.com/miaolink/AITradeGW/blob/main/CURSOR.md  
- 在线站：https://www.miaolink.cn/AITradeGW/index.php  

**对 AI 的提示语示例（可复制）：**

```text
请打开并严格执行这份任务文档（机读安装手册）：
https://raw.githubusercontent.com/miaolink/AITradeGW/main/WorkBuddy%E5%AE%89%E8%A3%85MCP%E4%BA%A4%E6%98%93%E7%BD%91%E5%85%B3.md
任务：检测本机「通用AI交易网关」是否已安装；检测网关是否运行；把 aitradegw MCP 安全合并进 WorkBuddy 的 mcp.json；最后按文档格式汇报。
```

---

**投资有风险，入市需谨慎。本软件为技术工具，不构成投资建议。**
