# AI 接入指南 — 让 Cursor / Codex 帮你查行情、查持仓

配置完成后，在 **Cursor** 或 **Codex** 里直接对话：**「帮我查一下持仓」**、**「000001 现在什么价」** — AI 通过网关读取真实数据。

**同花顺 PC 用户**请用姊妹项目 **[THS_MCP_Quant](https://github.com/miaolink/THS_MCP_Quant)**，配置方式类似。

---

## 使用前准备

1. 打开 **通用 AI 交易网关** 图形控制台
2. **服务** 页 → **启动网关**（状态变绿）
3. 若要查持仓/资金：启动 **交易客户端** 并登录
4. **服务** 页 → **启动 MCP**（或在 Cursor / Codex 配置中使用 stdio 模式，见下文）

---

## 三步配置（Cursor / Codex）

### 第 1 步：找到 MCP 程序路径

安装目录下的 `bin\aitradegw-mcp.exe`，例如：

```text
C:\Program Files\AITradeGW\bin\aitradegw-mcp.exe
```

### 第 2 步：写入 MCP 配置

**Cursor** 用户：打开（没有则新建）文件

```text
C:\Users\你的用户名\.cursor\mcp.json
```

**Codex** 用户：在 Codex 的 MCP 服务器设置中填入相同内容（界面路径以 Codex 当前版本为准）。

粘贴以下内容，**把路径改成你的实际安装路径**：

```json
{
  "mcpServers": {
    "aitradegw": {
      "command": "C:\\Program Files\\AITradeGW\\bin\\aitradegw-mcp.exe",
      "args": ["stdio"],
      "env": {
        "TDX_GATEWAY_URL": "http://127.0.0.1:19322"
      }
    }
  }
}
```

### 第 3 步：刷新客户端

- **Cursor**：**Settings → MCP** → 刷新，或 **Reload Window**
- **Codex**：保存 MCP 配置后重启或刷新 Codex

看到 `aitradegw` 显示绿色、有 tools 列表即成功。

---

## AI 能帮你做什么

| 场景 | 示例对话 |
|------|----------|
| 健康检查 | 「网关连上了吗？」 |
| 查行情 | 「平安银行现在多少钱？五档多少？」 |
| 查 K 线 | 「000001 最近 30 日日线」 |
| 搜股票 | 「代码里带『银行』的有哪些」 |
| 查账户 | 「我现在有多少资金？」 |
| 查持仓 | 「帮我列一下持仓」 |
| 查委托 | 「今天有哪些委托？」 |
| 板块 / 公式 | 「有哪些自定义板块？」「列出公式」 |

> 当前 MCP 以 **查询** 为主。实盘下单请在图形控制台 **交易** 页操作，并遵守模拟/实盘确认规则。

更多话术与工具对照见 **[AI 交易示例](./AI交易示例.md)**；本机脚本与 PowerShell 见 **[CLI 使用说明](./CLI使用说明.md)**。

---

## 也可以从 GUI 启动 MCP

不想改 json？在图形控制台 **服务** 页点 **启动 MCP**，Cursor / Codex 配置中使用 HTTP 模式（进阶用户联系作者获取模板）。

大多数用户推荐上文 **stdio 方式**，更简单稳定。

---

## 常见问题

| 现象 | 处理 |
|------|------|
| MCP 红色 / 无 tools | 确认 **服务** 页网关已启动；检查 exe 路径是否正确 |
| 查持仓失败 | 服务页 **启动交易** 并在交易客户端登录 |
| 改配置不生效 | Cursor / Codex 里 Reload 或重启客户端 |

---

## 同系列产品

| 产品 | AI 接入文档 |
|------|-------------|
| 通用 AI 交易网关（本项目） | 本文 |
| RHTHS（同花顺专用） | [THS_MCP_Quant MCP 说明](https://github.com/miaolink/THS_MCP_Quant/blob/main/MCP%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E.md) |

---

**投资有风险，入市需谨慎。本软件为技术工具，不构成任何投资建议。**
