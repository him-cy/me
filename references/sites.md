# 站点适配器（site adapter）

## 接口约定

每个站点在 `scripts/sites/<name>.py` 实现两个函数：

```python
def search(query, n, page=1) -> list[dict]:
    """返回候选列表，每条含：
    {
        "src_url":  "直接图片下载 URL（大图）",
        "page_url": "图片来源页（写采集表 source_url）",
        "author":   "作者/摄影师",
        "license":  "许可协议文字",
        "meta":     {}  # 任意附加信息
    }
    """
    ...

def download(url, path, timeout=30) -> (bool, info):
    """下载单张图到 path；返回 (成功?, 字节数或错误)。
    默认用浏览器 UA + Referer；子类可覆盖。"""
    ...
```

`crawl_sample.py` / `crawl_full.py` 通过 `SITE` 参数动态加载：
```python
import importlib
mod = importlib.import_module("sites." + SITE)
cands = mod.search(QUERY, n, page)
```

## 已验证：Pexels

- API：`https://api.pexels.com/v1/search`
- Key（公开 demo，限流 ~200/h）：`563492ad6f917000010000014107a189a4414daab1f39ceefe900972`
- 搜索词映射：01 景观规划 → `"landscape planning"`；02 广场庭院 → `"courtyard plaza"`；03 水景 → `"fountain water feature"`
- 直链：`photo["src"]["large2x"]`（或 `original`）
- 注意：bot UA 会被 403，必须带浏览器 UA + Referer。

## 模板：Wikimedia Commons

- API：`https://commons.wikimedia.org/w/api.php?action=query&generator=categorymembers&gcmtitle=Category:...&prop=imageinfo&iiprop=url|extmetadata&format=json`
- **坑**：bot 风格 User-Agent 会被 403；需自定义 UA（带联系方式）。分类遍历比搜索 API 准确率高。
- 直链：`imageinfo["url"]`（upload.wikimedia.org）
- license / author 在 `extmetadata` 的 `License` / `Artist` 字段，常含 HTML，需清洗（见旧项目 `clean_and_rewrite.py`）。

## 模板：Unsplash

- 官方 API 需 key；第三方 `*.vercel.app` 壳站曾挖出前端 key，但 HAR 只含缩略图(w=700)、无原图端点 → **不推荐**。
- 若用官方 API：`https://api.unsplash.com/search/photos?query=...&client_id=KEY`，原图在 `urls.raw`。

## 新增站点步骤

1. 拷贝 `scripts/sites/template.py` → `scripts/sites/<name>.py`
2. 实现 `search()`（返回标准 dict 列表）与可选 `download()`
3. 在 `crawl_sample.py` / `crawl_full.py` 顶部的 `SUPPORTED = [...]` 注册 `<name>`
4. 自测小样本（SAMPLE_N=5）确认 URL 可下载、字段齐全
