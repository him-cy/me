# 核查双模式（AI / 人工）

## 合格标准定义（关键）

"合格率"取决于标准。开始前务必与用户确认标准，AI 与人工用同一把尺子。
默认标准模板（可按主题改）：

> 合格：真实拍摄的景观/规划照片，主体清晰、构图完整。
> 不合格（任一即淘汰）：
> 1. 地图、平面图、卫星图、示意图、CAD 线稿
> 2. 纯文字/数据截图、带大段水印或广告
> 3. 短边分辨率 < 800px 或明显模糊/压缩伪影
> 4. 内容与主题无关（如人物特写、室内商品）
> 5. 重复/几乎相同的图

把标准写进：人工核查页顶部说明 + AI 核查 prompt。

## 模式 A：人工核查页

1. `gen_review_html.py` 读 `_pending.json` / `_pending_sample.json` 生成 `review_<tag>.html`
2. 三副本（workspace / 桌面 / 照片目录），用户本地双击打开（网页预览因 CORS 打不开 `file://`）
3. 用户点图/勾选框标记删除 → 导出 `delete_list.txt`
4. 回传给 AI → `apply_results.py` 处理
5. **HTML 转义必做**：title/author 含 `&`、引号、`<>` 会冲垮标签导致勾选框丢失 → 用 `html.escape()`

## 模式 B：AI 视觉核查

1. `verify_ai.py` 读候选 → 输出 `_verify_manifest.json`（每张：`{id, path}`）+ 打印核查 prompt（含标准）
2. 代理对每张调用 `image` 工具，按标准判 pass/fail，写 `_ai_results.json`：
   ```json
   {"01_0001.jpg": {"decision": "pass", "reason": ""},
    "01_0002.jpg": {"decision": "fail", "reason": "地图截图"}}
   ```
3. `apply_results.py` 同时支持 `delete_list.txt`（human）与 `_ai_results.json`（ai）

## 何时用哪种

- **AI 模式**：量大、标准清晰、需快速过筛；token 成本随张数线性增长，建议先小样本验证标准表述。
- **人工模式**：标准主观、需最终质量把关、或用户要亲自看。
- **混合**：AI 先全量初筛，标记"borderline"的留给人工复核（进阶用法）。

## 结果文件统一

`apply_results.py` 输入二选一：
- `delete_list.txt`：纯文件名列表，每行一个（人工导出）
- `_ai_results.json`：`{filename: {decision, reason}}`（AI 产出，仅 fail 参与删除）

两者都只删清单内文件，绝不碰清单外文件。
