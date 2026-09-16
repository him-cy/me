# pexels-image-crawl

图片采集流水线：批量爬取真实照片 → 小样本测合格率 → 估算大批量 → 核查筛选 → 写入采集表。
默认站点 Pexels；提供 Wikimedia / Unsplash 适配器模板。

可由 AI Agent 通过触发词驱动（`爬取图片` / `采集图片`），也可直接调用脚本。

A pipeline that crawls real photos in batch → samples for pass-rate → estimates batch size via Wilson 95% lower bound → reviews/cleans → writes to a collection spreadsheet. Pexels adapter is production-tested; Wikimedia/Unsplash are templated.

## 特性

- **闭环估算**：小样本 → Wilson 95% 置信下界 + 失败缓冲 → 大批量爬取量（避免按平均率爬完发现不够）
- **健壮性**：断点续传、内容 MD5 去重、单实例锁（防幽灵爬虫并发污染，曾因此丢失数百张图）
- **核查双模式**：AI 视觉（`image` 工具）或人工 HTML 页（本地双击打开）
- **三方对账**：每步结束校验 `磁盘文件数 == 元数据条数 == Excel 行数`
- **跨平台**：路径与 Python 解释器运行时自动探测；Win / Mac / Linux 开箱即用，无需改任何配置

## 安装

放入 Agent 的 skills 路径：

```
~/.qclaw/skills/pexels-image-crawl/         # QClaw / OpenClaw
~/.claude/skills/pexels-image-crawl/        # Claude（按对应工具约定）
```

依赖：

```bash
pip install requests openpyxl
# 缺则脚本首次运行会自动 pip install（见配置）
```

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

## 小项目示例：Pexels 爬「01 景观规划」48 张入库

下面以一个最小闭环走完 5 步流水线：需求量 30、样本 30、全量 ~55、删除 7、最终入库 48 行。

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