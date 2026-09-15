# Pexels 图片采集 · 工作流参考

## 关键发现

### Pexels API Key
`pexels.vercel.app` 是纯前端 SPA，API key 硬编码在前端 JS 里，直接复用即可：

```
Authorization: 563492ad6f917000010000014107a189a4414daab1f39ceefe900972
```

**限流**：约 200 次/小时，爬 50 张轻松有余。

### 发现步骤（如果将来 Vercel 部署变了）
1. 访问目标 URL，用浏览器 DevTools → Network 抓 JS 文件
2. 在大 JS 包（通常是 `*.chunk.js`）中搜索 `Authorization` 或 `api.pexels.com`
3. 找到 key 后直接用 requests 调官方 API，无需再逆向

### 官方 API 用法
```python
import requests
KEY = "563492ad6f917000010000014107a189a4414daab1f39ceefe900972"
r = requests.get("https://api.pexels.com/v1/search",
    params={"query": "landscape planning", "per_page": 40, "page": 1},
    headers={"Authorization": KEY})
photos = r.json()["photos"]
# photo["src"] 含多个尺寸: original/large2x/large/medium/small/portrait/landscape/tiny
# 下载用原图: photo["src"]["large2x"] 或 ["original"]
```

### Pexels 返回字段参考
```json
{
  "id": 3061224,
  "width": 6016,
  "height": 4016,
  "url": "https://www.pexels.com/photo/...",
  "photographer": "K",
  "photographer_url": "https://www.pexels.com/@...",
  "src": {
    "original": "https://images.pexels.com/photos/3061224/pexels-photo-3061224.jpeg",
    "large2x": "https://images.pexels.com/photos/3061224/pexels-photo-3061224.jpeg?auto=compress",
    "large": "...",
    "medium": "...",
    "small": "..."
  },
  "alt": "description"
}
```

## 采集表字段映射（Wikimedia vs Pexels）

| 列 | Wikimedia 取值 | Pexels 取值 |
|----|--------------|-------------|
| image_id | `01_0001.jpg` | 同左 |
| function_category | `01` 等 | 同左 |
| source_type | `Wikimedia Commons` | `Pexels` |
| license | CC0 / CC BY-SA 4.0 | `Pexels License (free to use)` |
| source_url | Wikimedia File:URL 或 API 直链 | `photo["url"]`（Pexels 图页） |
| author | 清理后的 user 名或 `Author unidentified` | `photo["photographer"]` |

## 常见问题

**Q: Pexels key 被拦截？**
> demo key 限流宽松。如果被 429，减少请求频率（每张间隔加到 2~3s）或换关键词分批爬。

**Q: 核查页图片不显示？**
> `file:///` 路径需本地双击打开，浏览器网页预览会因 CORS 被拦截。把 HTML 复制到桌面或照片目录再打开。

**Q: 删除列表文件路径？**
> 默认 `F:\APP\delete_list.txt` 或用户指定路径。读内容确认要删的文件再处理，不要直接执行用户没确认的列表。

**Q: 合并时编号冲突？**
> 用两阶段重命名（old -> tmp_pex_xxxx -> new）避免同编号碰撞。确认第二批前缀与第一批不同（P01_ vs 01_）。

## 脚本参数速查

| 脚本 | 必改参数 |
|------|---------|
| `crawl_pexels.py` | OUT_DIR / QUERY / TARGET / PREFIX / CATEGORY |
| `gen_review_html.py` | PHOTO_DIR / PENDING / OUT_HTML / PREFIX / TITLE / LIST_NAME |
| `apply_delete.py` | PHOTO_DIR / META_FILE / DELETE_LIST / EXCEL_PATH / PREFIX / CATEGORY / SOURCE_TYPE |
| `integrate.py` | PHOTO_DIR / META1 / META2 / PREFIX1 / PREFIX2 / PREFIX2_START / EXCEL_PATH / CATEGORY |
