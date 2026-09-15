# -*- coding: utf-8 -*-
"""AI 核查准备：生成核查清单 + 标准 prompt，供代理用 image 工具逐张判断。
代理判完后把结果写回 _ai_results.json，再跑 apply_results.py。"""
import os, json, sys
sys.stdout.reconfigure(encoding="utf-8")

# ===== 参数（改这里） =====
PHOTO_DIR = r"D:\photos\01_景观规划"
PENDING   = os.path.join(PHOTO_DIR, "_pending.json")
OUT_MANIFEST = os.path.join(PHOTO_DIR, "_verify_manifest.json")
OUT_RESULTS  = os.path.join(PHOTO_DIR, "_ai_results.json")
PREFIX    = "01_"
CRITERIA  = ("合格: 真实拍摄的景观/规划照片, 主体清晰、构图完整。\n"
             "不合格(任一即淘汰): 1)地图/平面图/卫星图/示意图/CAD线稿 "
             "2)纯文字或数据截图、带大段水印或广告 3)短边<800px或明显模糊 "
             "4)与主题无关(人物特写/室内商品) 5)重复/几乎相同")
# ==========================

records = json.load(open(PENDING, encoding="utf-8"))
files = sorted([r["file"] for r in records if r["file"].startswith(PREFIX)],
               key=lambda x: int(x.split("_")[1].split(".")[0]))
manifest = [{"id": f, "path": os.path.join(PHOTO_DIR, f)} for f in files]
json.dump(manifest, open(OUT_MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("待核查:", len(files), "张 ->", OUT_MANIFEST)
print("\n===== 复制以下 prompt 逐张调用 image 工具 =====\n")
print("核查标准:\n" + CRITERIA)
print("\n对每张图调用 image 工具, 判断 pass/fail, 最终把结果写成 JSON 存到:")
print(OUT_RESULTS)
print("格式示例:")
print(json.dumps({"01_0001.jpg": {"decision": "pass", "reason": ""},
                   "01_0002.jpg": {"decision": "fail", "reason": "地图截图"}}, ensure_ascii=False, indent=2))
print("\n图片路径清单(前10):")
for m in manifest[:10]:
    print(" ", m["path"])
print("  ... 共", len(manifest), "张")
