# pexels-image-crawl · 图片采集流水线 Skill

> 一个给 AI Agent（OpenClaw / QClaw）用的图片批量采集 Skill：从图片网站爬真实照片 → 小样本测合格率 → 估算大批量 → 核查筛选 → 写入采集记录表。默认站点 Pexels，可扩展 Wikimedia / Unsplash。

English: An AI-agent skill that runs a 5-step image-collection pipeline (crawl → sample-test pass-rate → estimate batch size → full crawl + review → write to a collection spreadsheet). Defaults to Pexels; adapters for Wikimedia/Unsplash are templated.

## 它能做什么

1. **输入**：你要的网站 + 图片主题 + 需求量 + 样本量 + 合格标准
2. **样本测试**：先爬 N 张小样本，人工或 AI 核查，算合格率
3. **估算**：用 Wilson 95% 置信下界 + 失败缓冲，算出该爬多少张大批量（避免"按平均率爬完发现不够"）
4. **大批量爬取**：断点续传 + 内容哈希去重 + 单实例锁（防幽灵爬虫污染），再核查清理
5. **整合写表**：把合格图写入采集记录表（Excel），支持多批次合并

## 安装（OpenClaw / QClaw）

把整个目录复制到 Agent 的 skills 目录：

```
~/.qclaw/skills/pexels-image-crawl/      # 本仓库内容
```

重启 Agent 后，对 Agent 说"爬取图片"即可触发。

## 快速开始

触发后 AI 会先问你 8 个问题（网站/主题/需求量/样本量/合格标准/核查方式/分类编号/目录），确认后按 5 步跑。核心脚本（改顶部常量即可用）：

| 脚本 | 作用 |
|------|------|
| `scripts/crawl_sample.py` | 爬小样本（默认 30 张） |
| `scripts/estimate.py` | 按合格率估算大批量目标数 |
| `scripts/crawl_full.py` | 大批量爬取（断点/去重/锁） |
| `scripts/gen_review_html.py` | 生成人工核查页（本地双击打开） |
| `scripts/verify_ai.py` | 生成 AI 核查清单 |
| `scripts/apply_results.py` | 按删除清单清理 + 重命名 + 更新元数据 |
| `scripts/finalize_table.py` | 把合格项写入采集表 |
| `scripts/integrate.py` | 多批次（如 Pexels+Wikimedia）合并 |

站点适配器在 `scripts/sites/`：`pexels.py`（已验证）、`template.py`（照抄实现 `search()`/`download()` 即可加新站）。

## 配置

- **路径与解释器自动解析**：所有机器相关路径（照片目录、采集表、删除清单目录、工作目录）和 Python 解释器由 `scripts/_config.py` 在运行时解析。默认值见下表，可用环境变量覆盖。
- **环境变量覆盖默认位置**：
  ```powershell
  $env:COLLECT_PHOTOS     = "D:\photos"             # 照片根目录
  $env:COLLECT_TABLE      = "C:\path\采集记录表.xlsx" # 采集表
  $env:COLLECT_DELETE_DIR = "C:\path\lists"         # 删除清单目录
  $env:COLLECT_WORKSPACE  = "C:\path\work"          # 工作/临时目录
  $env:COLLECT_PYTHON     = "C:\path\python.exe"    # Python 解释器
  ```
  默认值：`~/photos`、`~/采集记录表.xlsx`、`~/delete_lists`、`~/photos/_work`；`COLLECT_PYTHON` 留空时按 `当前解释器 → PATH → 常见 bundled 位置` 自动探测。Windows 下若 `D:\photos` 或 G 盘那份采集表已存在则沿用，避免硬迁移现有数据。
- **Pexels API Key**：默认使用从 `pexels.vercel.app` 公开 SPA 提取的 demo key（共享、限流 200/小时）。生产环境请到 https://www.pexels.com/api/ 申请自己的 key，设环境变量：
  ```powershell
  $env:PEXELS_API_KEY = "你的key"
  ```
- **第三方依赖**：`requests`、`openpyxl`。脚本首次运行若检测到缺失会自动 `pip install`。

## 目录约定（自动解析，可用环境变量覆盖）

```
照片根目录    ~/photos/                (Windows 若 D:\photos 存在则沿用；覆盖: COLLECT_PHOTOS)
  分类目录    ~/photos/<分类名>/        图片 + _pending.json(元数据)
采集表        ~/采集记录表.xlsx         (Windows 若 G:\...\采集记录表.xlsx 存在则沿用；覆盖: COLLECT_TABLE)
删除清单目录  ~/delete_lists/          用户回传的 delete_list.txt（覆盖: COLLECT_DELETE_DIR）
工作目录      ~/photos/_work/          核查页 HTML、AI 中间产物（覆盖: COLLECT_WORKSPACE）
```

## 血泪教训（写进 SKILL.md 的硬约束）

- 不自动删文件，只在用户回传删除清单或 AI 核查结果后删
- 改动 Excel / 元数据前先备份
- 大批量爬虫必须单实例锁，防并发污染
- 每步结束三方对账：磁盘文件数 == 元数据条数 == Excel 行数

## 许可

- 本 Skill 代码：按你的仓库许可发布（如 MIT）。
- 采集到的图片版权归各自来源（Pexels 图片遵循 Pexels License，可免费使用）。
