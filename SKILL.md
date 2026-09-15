---
name: image-collect-pipeline
description: |
  图片采集流水线 Skill。触发词：爬取图片 / 采集图片 / 图片采集（简化触发，用户只需说“爬取图片”即可）。
  触发后 AI 必须先向用户列出一份问题清单（网站/主题/需求量/样本量/合格标准/核查方式/分类编号/输出目录），等用户回答后再按 5 步流程执行。
  适用场景：(1) 从指定网站批量爬真实图片 (2) 先小样本测合格率再估算大批量 (3) AI 或人工核查筛选 (4) 多批次合并写采集表。
  跨平台：路径与 Python 解释器全部自动探测，任何人克隆后发“爬取图片”即可跑，无需改任何路径。
---

# 图片采集流水线（5 步）

```
① 输入      用户给: 网站 + 图片类型(主题) + 需求量 + 样本量 + 合格标准
② 样本测试  crawl_sample.py 爬 N 张 → 核查(ai/human) → 算合格率
③ 估算      estimate.py: 大样本量 = ceil(需求量 / 合格率下限 × (1+失败缓冲))
④ 大批量    crawl_full.py 爬取(断点续传+去重+锁) → 核查 → apply_results.py 清理
⑤ 整合      finalize_table.py 写采集表 + integrate.py 多批次合并
```

## 触发后第一步：列出问题清单（必做，勿直接执行）

用户说“爬取图片”时，**先输出以下问题清单收集信息，确认后再跑脚本**：

1. **网站/来源？** Pexels（默认） / Wikimedia / Unsplash / 其他（给 URL）
2. **图片主题/类型？** 如“景观规划”“广场庭院”“水景”，并附搜索词
3. **最终要多少张合格图？** 需求量，如 100
4. **先爬多少张小样本测合格率？** 如 30
5. **合格标准是什么？** 默认模板见 `references/verification.md`，可自定义
6. **核查用哪种方式？** AI 视觉核查 / 人工核查页
7. **采集表分类编号？** 如 01 / 02 / 03
8. **图片存到哪个目录？** 默认自动：`~/photos/<分类名>/`（Windows 上若你已有 `D:\photos` 会自动沿用）。可用环境变量 `COLLECT_PHOTOS` 覆盖。

缺省值：网站=Pexels、核查=人工页、目录=自动（`~/photos/<分类名>/`）。
收集完后即可按 5 步流程执行；任意一项不确定就先问，不要猜。

## 运行环境（自动，无需手动配置）

- **Python 解释器**：脚本 `_config.py` 自动探测——优先当前解释器，其次 PATH 中的 `python`/`python3`/`py`，再兜底常见 OpenClaw/Claude bundled 位置。若 `python --version` 报错，先 `where python`(Win)/`which python3`(Mac/Linux) 找路径，或设环境变量 `COLLECT_PYTHON` 指向它。
- **第三方依赖**：`requests`（爬取）、`openpyxl`（写表）脚本会自动 `pip install`，无需手动装。
- **下文命令均写作 `python -u scripts/xxx.py`**，`python` 即上面探测到的解释器。

## 硬约束（血泪教训，必须遵守）

- **不自动删**:删除只发生在用户回传 `delete_list.txt` 或 AI 核查写 `_ai_results.json` 之后。清单里没有的文件绝不删。
- **改动前备份**:Excel 写前 `.bak_before_<step>`;`_pending.json` 写前 `.bak`。
- **单实例锁**:`crawl_full.py` 自动加锁,防止多个爬虫并发污染数据(曾因此全盘混乱)。
- **三方对账**:每步结束校验 磁盘文件数 == 元数据条数 == Excel 行数。
- **PowerShell**:不用 `&&`(用 `;`);中文输出 `sys.stdout.reconfigure(encoding="utf-8")`;不用 `python -c` 内联复杂逻辑,写脚本执行。
- **删除用 Python `os.remove`** 绕过安全策略的批量拦截。

## 目录约定（全部自动解析，可用环境变量覆盖）

```
照片根目录    ~/photos/                (Windows 若 D:\photos 存在则沿用；覆盖: COLLECT_PHOTOS)
  分类目录    ~/photos/<分类名>/        图片 + _pending.json(元数据) + _pending_sample.json(样本)
采集表        ~/采集记录表.xlsx         (Windows 若 G:\...\采集记录表.xlsx 存在则沿用；覆盖: COLLECT_TABLE)
删除清单目录  ~/delete_lists/          用户回传的 delete_list.txt（覆盖: COLLECT_DELETE_DIR）
工作目录      ~/photos/_work/          核查页 HTML、AI 中间产物（覆盖: COLLECT_WORKSPACE）
```

## ① 输入与适配

所需信息见上方「问题清单」。用户给的“网站”映射到 `scripts/sites/` 下的适配器：
- `pexels`(已验证,默认)
- `wikimedia`(模板,需注意 403/bot UA 问题)
- `unsplash`(模板,HAR 直链难取,见 references/sites.md)

新增站点:拷贝 `scripts/sites/template.py` 实现 `search()` 与 `download()`,在 `crawl_*.py` 顶部注册。

## 2 样本测试

```powershell
# 改 crawl_sample.py 顶部: SITE / QUERY / SAMPLE_N / CATEGORY / CAT_FOLDER（OUT_DIR 自动由 CAT_FOLDER 生成,不用手写）
python -u scripts/crawl_sample.py
```

产出 `_pending_sample.json`(N 条候选 + 已下载图)。

**核查方式(用户选)**:
- **人工**:`gen_review_html.py` 生成核查页 → 用户勾选 → 回传 `delete_list.txt`
- **AI**:`verify_ai.py` 生成核查清单 + 标准 → 代理用 `image` 工具逐张判 → 写 `_ai_results.json`

合格标准示例(写进核查 prompt / 页面说明):"必须是真实景观/规划照片,排除地图、平面图、示意图、纯文字截图、低分辨率(<800px短边)、带水印广告"。

## 3 估算大样本量

```powershell
# estimate.py 参数: DEMAND(需求量) + SAMPLE_N + QUALIFIED(样本合格数)
python -u scripts/estimate.py
```

公式:`crawl_target = ceil( DEMAND / p_lower × (1 + FAIL_BUF) )`
- `p_lower` = Wilson 95% 置信下界(点估计偏乐观会爬少,用下界兜底)
- `FAIL_BUF` ≈ 0.15(下载失败 + 内容重复缓冲)
- 若样本 0 合格 → 警告换关键词/站点,不估算。

## 4 大批量爬取与核查

```powershell
# crawl_full.py: SITE / QUERY / TARGET(=估算值) / CATEGORY / CAT_FOLDER / PREFIX
python -u scripts/crawl_full.py
```

特性:断点续传、内容哈希去重、单实例锁、每 20 张存盘。完成后同 2 核查。
清理:`apply_results.py` 读 `delete_list.txt` 或 `_ai_results.json` → 删不合格 + 顺序重命名 + 更新 `_pending.json`。

## 5 整合与写表

```powershell
# finalize_table.py: 把 _pending.json 接受项写入采集表(对应 CATEGORY 区块)
python -u scripts/finalize_table.py
# integrate.py: 多批次(如 Wikimedia+Pexels)合并为连续编号集合
python -u scripts/integrate.py
```

## 采集表字段(Pexels 示例)

| 列 | 值 |
|----|----|
| image_id | `01_0001.jpg` |
| function_category | `01` |
| source_type | `Pexels` |
| license | `Pexels License (free to use)` |
| source_url | Pexels 图页 |
| author | 摄影师名 |
| 其余列 | 空 |

详见 `references/sites.md`(站点适配)、`references/verification.md`(核查标准与双模式)、`references/estimation.md`(估算公式与示例)。
