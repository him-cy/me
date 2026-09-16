# pexels-image-crawl

图片采集流水线：从图片网站批量爬取真实照片 → 小样本测合格率 → 估算大批量 → 核查筛选 → 写入采集表。
默认站点 Pexels；提供 Wikimedia / Unsplash 适配器模板。

---

## 快速开始（10 分钟跑通）

从零开始到跑通整个流程，按步骤走即可。

### 0. 准备三样东西

| 东西 | 怎么准备 |
|------|----------|
| **一台电脑**（Win 10/11、macOS、Linux 均可） | 你已经有了 |
| **Python 3.8 或更新版本** | 没装就去 [python.org/downloads](https://www.python.org/downloads/) 下载安装；**安装时务必勾上 "Add Python to PATH"**（最关键的一步） |
| **一个支持 Skill 的 AI 助手** | QClaw / Claude / Cursor 均可，详见下方「适配的 AI 工具」 |
| **能联网** | 爬图需要 |

### 1. 确认 Python 装好了

打开**终端**（也叫命令行、命令提示符、Terminal）：

- **Windows**：按 `Win + R`，输入 `cmd`，回车
- **macOS**：按 `Cmd + 空格`，输入 `Terminal`，回车
- **Linux**：应用菜单里找「终端」或「Terminal」

在终端里输入下面这行（注意是英文横杠和两个短横）：

```
python --version
```

看到类似 `Python 3.11.5` 的输出就 OK。`3.` 后面那个数字 ≥ 8 即可。

如果提示 `python 不是内部或外部命令` / `command not found`：说明 Python 没装或没加到 PATH，请重新安装并**勾上 "Add Python to PATH"**。

### 2. 把 Skill 文件夹放到正确位置

把整个 `pexels-image-crawl` 文件夹（连同里面的 `SKILL.md`、`scripts/`、`references/`）复制到下面其中一个位置（根据你用的 AI 工具选）：

| AI 工具 | 文件夹放这里 |
|---------|--------------|
| QClaw / OpenClaw | `C:\Users\你的用户名\.qclaw\skills\`（Win）或 `~/.qclaw/skills/`（Mac/Linux） |
| Claude Code | `~/.claude/skills/` |
| Claude Desktop / claude.ai | 同上 `~/.claude/skills/`，并开启 Skills 功能 |
| Cursor / Windsurf | 看对应工具文档的 skills 目录 |

文件夹不存在就手动新建一个。复制完成后**重启 AI 助手**，让 Skill 生效。

### 3. 跟 AI 说一句话

重启 AI 后，对它说：

```
爬取图片
```

AI 会问你 8 个问题，照实回答：

1. **网站** — 答 `Pexels`（或填别的网站）
2. **主题** — 你想要什么类型的图片，比如「景观规划」「广场庭院」
3. **需求量** — 你最终要多少张图，比如 `30`
4. **样本量** — 先爬多少张试试，比如 `30`
5. **合格标准** — 什么样的图算合格，AI 会给个默认模板可改
6. **核查方式** — 选「人工」会用 HTML 页面让你点选；选「AI」会让 AI 自己看图判
7. **分类编号** — 你这个分类的编号，比如 `01`
8. **输出目录** — 默认即可，图片会存到 `~/photos/<分类名>/`

回答完，AI 会按 5 步自动跑完全流程。

### 4. 你会得到什么

跑完后你会拿到：

- 一堆图片，编号 `01_0001.jpg` 这种，存到 `~/photos/<分类名>/`
- 你的采集记录表 Excel 多出 N 行（自动追加，不会覆盖已有数据）
- 中间 AI 会跟你确认关键步骤，**不会偷偷删你电脑里的东西**

### 第一次跑常踩的坑

| 现象 | 原因和解决 |
|------|------------|
| 终端中文显示乱码 | Windows：控制面板 → 区域 → 管理 → 更改系统区域设置 → 勾「Beta：使用 Unicode UTF-8」→ 重启。脚本已经做了一部分处理，这步能彻底解决 |
| `python` 命令找不到 | 重装 Python 时忘了勾 "Add Python to PATH"，重装时记得勾。或在终端用 `where python`（Win）/ `which python3`（Mac）查实际路径 |
| 脚本说 `pip install` 失败 | 先在终端执行 `python -m pip install --upgrade pip` 再试 |
| 想中途停掉爬虫 | 在终端按 `Ctrl + C`（Mac 是 `Cmd + C`） |
| 不知道图片存哪了 | 默认 `~/photos/<分类名>/`，例如 `~/photos/01_景观规划/`。`~` 在 Windows 上等于 `C:\Users\你的用户名\` |
| 核查页打不开/图片不显示 | 双击 `review.html` 会用浏览器打开；如果图片空白，是浏览器安全策略拦截本地文件。右键缩略图 → 「在新标签页打开图片」可单独查看 |
| AI 不响应「爬取图片」 | 检查 Skill 文件夹路径是否正确，重启 AI 助手后再试 |

---

## 小项目示例：Pexels 爬「01 景观规划」48 张入库

下面用一个最小闭环走完 5 步流水线：需求 30、样本 30、全量 ~55、删除 7、最终入库 48 行。

### 0. 启动对话

> 调用方：爬取图片
> Agent：以下 8 项请确认：
>   1. 网站 → Pexels
>   2. 主题 → 景观规划，搜索词 `landscape planning`
>   3. 需求量 → 30
>   4. 样本量 → 30
>   5. 合格标准 → 真实景观/规划照片，主体清晰；排除地图、平面图、示意图、纯文字截图、短边 <800px、带水印广告
>   6. 核查方式 → 人工
>   7. 分类编号 → 01
>   8. 输出目录 → 默认（自动）

### 1. 样本测试（爬 30 张）

```bash
# 改 scripts/crawl_sample.py 顶部：
#   QUERY = "landscape planning"; SAMPLE_N = 30; CATEGORY = "01"
#   CAT_FOLDER = "01_景观规划"; PREFIX = "S01_"
python -u scripts/crawl_sample.py
```

```
样本爬取: site=pexels query=landscape planning n=30
  [1/30] S01_0001.jpg Alice 312044B
  ...
  [30/30] S01_0030.jpg Frank 287115B
样本完成: 30 张 -> ~/photos/01_景观规划/_pending_sample.json
```

### 2. 核查 + 估算

```bash
python -u scripts/gen_review_html.py
# → ~/photos/_work/review.html  （亦在 ~/photos/01_景观规划/review.html 留一份）
```

本地双击 `review.html`，点图或勾选框标记不合格（红框），点「下载删除列表」得到 `delete_list.txt`，放入 `~/delete_lists/`。

假设本轮 30 张样本中 **24 张合格**（剔除 6 张地图/示意图）。

```bash
# 改 scripts/estimate.py：
#   DEMAND = 30; SAMPLE_N = 30; QUALIFIED = 24; FAIL_BUF = 0.15
python -u scripts/estimate.py
```

```
样本量 n      = 30
合格数 q      = 24
点估计 p_hat  = 0.800
Wilson 95% 下界 p_lower = 0.627
失败缓冲      = 15%
→ 估算爬取量 N = 55 张
  预期合格 ≈ 44 张 (留缓冲后保留 30)
```

### 3. 大批量爬取（目标 55 张）

```bash
# 改 scripts/crawl_full.py 顶部：
#   QUERY = "landscape planning"; TARGET = 55; CATEGORY = "01"
#   CAT_FOLDER = "01_景观规划"; PREFIX = "01_"
python -u scripts/crawl_full.py
```

```
续传: 已有 0 条记录
  [1/55] 01_0001.jpg Alice 312044B
  ...
  [20/55] 01_0020.jpg ...    # 每 20 张落盘一次
  ...
  [55/55] 01_0055.jpg Iris 198432B
完成: 共 55 张 -> ~/photos/01_景观规划/_pending.json  失败/跳过: 0
```

特性：
- **断点续传**：中断后重跑自动从已落盘位置继续（每 20 张存一次）
- **MD5 内容去重**：同图（已下载过的）跳过
- **单实例锁** `.crawl_lock`：防止并发幽灵进程污染元数据

### 4. 核查清理

```bash
python -u scripts/gen_review_html.py
# → 重新生成 55 张核查页（覆盖 _work/review.html）
# 本轮勾选 7 张不合格 → 下载 delete_list.txt → 放入 ~/delete_lists/
python -u scripts/apply_results.py
```

```
输入来源: delete_list.txt | 待删: 7 张
  已删: 01_0008.jpg
  ...
  已删: 01_0042.jpg
实际删除: 7
重命名完成: 01_0001.jpg ~ 01_0048.jpg
元数据更新: 48 条 -> ~/photos/01_景观规划/_pending.json
```

### 5. 写入采集表

```bash
python -u scripts/finalize_table.py
```

```
待写入(新): 48 | 已存在跳过: 0
已写入 Excel: 48 行于 row 3 ~ 50
磁盘: 48 | 元数据: 48 | Excel 分类: {'01': 48}
一致: True
```

闭环结束：48 张合格图入库到 `采集记录表.xlsx` 第 3~50 行，function_category=`01`，source_type=`Pexels`。

---

## 安装（开发者向简版）

放入 Agent 的 skills 路径（详见上方「适配的 AI 工具」表格）。依赖 `requests`、`openpyxl`，脚本首次运行会自动 `pip install`。

## 触发与脚本

由 Agent 触发时，Agent 先询问 8 项任务参数，再按 5 步流程调用以下脚本。直接调用时改脚本顶部任务常量即可。所有脚本的机器相关路径均由 `scripts/_config.py` 自动解析，无需手动配置。

| 脚本 | 用途 | 关键输入（任务常量） |
|------|------|---------------------|
| `scripts/crawl_sample.py` | 爬小样本 | `SITE / QUERY / SAMPLE_N / CATEGORY / CAT_FOLDER / PREFIX` |
| `scripts/estimate.py` | 估算大批量目标数 | `DEMAND / SAMPLE_N / QUALIFIED / FAIL_BUF` |
| `scripts/crawl_full.py` | 大批量爬取 | `SITE / QUERY / TARGET / CATEGORY / CAT_FOLDER / PREFIX` |
| `scripts/gen_review_html.py` | 生成人工核查页 | `CAT_FOLDER / PREFIX / PENDING` |
| `scripts/verify_ai.py` | 生成 AI 核查清单 | `CAT_FOLDER / PREFIX / PENDING` |
| `scripts/apply_results.py` | 删不合格 + 重命名 + 更新元数据 | `CAT_FOLDER / DELETE_LIST` 或 `AI_RESULTS` |
| `scripts/finalize_table.py` | 写入采集表 | `CAT_FOLDER / CATEGORY / SOURCE_TYPE` |
| `scripts/integrate.py` | 多批次合并 | `CAT_FOLDER / META_BATCH1 / META_BATCH2 / PREFIX1 / PREFIX2 / BATCH2_START` |

站点适配器在 `scripts/sites/`：`pexels.py`（已验证）、`template.py`（照抄实现 `search()` / `download()` 即可加新站）。

## 配置

### 路径与解释器自动解析

所有机器相关路径（照片目录、采集表、删除清单目录、工作目录）和 Python 解释器由 `scripts/_config.py` 在运行时解析。默认值：

| 变量 | 默认值 | 兜底 |
|------|--------|------|
| `PHOTOS_DIR` | `~/photos` | Windows 若 `D:\photos` 存在则沿用 |
| `TABLE_PATH` | `~/采集记录表.xlsx` | Windows 若 G 盘那份已存在则沿用 |
| `DELETE_DIR` | `~/delete_lists` | — |
| `WORKSPACE` | `~/photos/_work` | — |
| `PYTHON` | 自动探测 | 当前解释器 → `PATH` → 常见 bundled |

### 环境变量覆盖

```powershell
$env:COLLECT_PHOTOS     = "D:\photos"             # 照片根目录
$env:COLLECT_TABLE      = "C:\path\采集记录表.xlsx" # 采集表
$env:COLLECT_DELETE_DIR = "C:\path\lists"         # 删除清单目录
$env:COLLECT_WORKSPACE  = "C:\path\work"          # 工作/临时目录
$env:COLLECT_PYTHON     = "C:\path\python.exe"    # 留空走自动探测
```

### Pexels API Key

默认使用从 `pexels.vercel.app` 公开 SPA 提取的 demo key（共享、限流 200/小时）。生产环境请到 https://www.pexels.com/api/ 申请自己的 key：

```powershell
$env:PEXELS_API_KEY = "你的key"
```

### 依赖自动安装

`requests`、`openpyxl` 缺失时脚本首次运行会自动 `pip install`。

## 适配的 AI 工具

| 档 | 工具 | 用法 |
|----|------|------|
| 原生 | QClaw / OpenClaw | 放 `~/.qclaw/skills/` |
| 原生 | Claude Code | 放 `~/.claude/skills/` |
| 原生 | Claude Desktop / claude.ai（Pro/Max） | 放 `~/.claude/skills/`，并开启 Skills 功能 |
| 兼容 | Cursor、Windsurf 等支持 Agent Skills 的工具 | 放各自的 skills 目录 |
| 手动 | ChatGPT、Gemini、通义、豆包 | 把 `SKILL.md` 整篇贴进对话作为系统提示，再让模型调脚本 |

判定依据：本 Skill 用的是 Anthropic 开源的 **Agent Skills 标准**——`SKILL.md`（YAML 头 + 工作流）+ `scripts/`（Python 脚本）+ `references/`（参考文档）。纯文件结构，不绑任何闭源 API。

唯一硬约束：执行端 Python 3.8+，能装 `requests` / `openpyxl`（脚本自动装）。

## 目录布局

```
photos/
  <分类名>/
    01_*.jpg                正式批图片
    _pending.json           正式批元数据
    _pending_sample.json    样本批元数据（合并后可删）
    S01_*.jpg               样本图片（命名空间与正式批隔离）
    review.html             人工核查页副本
photos/_work/
  review.html               人工核查页主份
delete_lists/
  delete_list*.txt          调用方回传的删除清单
采集记录表.xlsx              15 列表（image_id / building_id / function_category / source_type / license / source_url / author / 评分 / 注释）
```

## 硬约束（生产事故沉淀）

- **不自动删**：仅在提供 `delete_list.txt` 或 AI 写 `_ai_results.json` 后删除；其余情况绝不删
- **改动前备份**：Excel 写前 `.bak_before_<step>`；`_pending.json` 写前 `.bak`
- **单实例锁** `.crawl_lock`：防并发；运行前 `Get-Process python` 确认无残留幽灵进程
- **三方对账**：每步校验 `磁盘文件数 == 元数据条数 == Excel 行数`
- **PowerShell**：不用 `&&`（用 `;`）；中文 stdout 加 `sys.stdout.reconfigure(encoding="utf-8")`；复杂逻辑不内联 `python -c`，写脚本执行

## 新增站点

复制 `scripts/sites/template.py` 为 `sites/<name>.py`，实现两个函数：

```python
def search(query, n, page=1) -> [dict]
    # 必含键: src_url, page_url, author, license, meta
def download(url, path, timeout=30) -> (ok: bool, info)
```

新站点常见坑（403/429 限流、bot UA 拦截、缩略图而非原图）见 `references/sites.md`。

## 参考

- `SKILL.md` — 触发词与 Agent 工作流定义
- `references/sites.md` — 站点适配器注意事项
- `references/verification.md` — 核查标准与双模式
- `references/estimation.md` — 估算公式推导与示例
- `references/workflow.md` — 完整工作流与字段映射

## 许可

- Skill 代码：按仓库许可发布（默认 MIT）
- 采集图片版权归各自来源（Pexels 遵循 Pexels License，可免费使用）