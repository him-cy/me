# -*- coding: utf-8 -*-
"""应用核查结果：删除不合格 + 顺序重命名 + 更新元数据。
支持两种输入(二选一): 人工 delete_list.txt 或 AI _ai_results.json。"""
import os, json, sys, shutil
sys.stdout.reconfigure(encoding="utf-8")

# ===== 参数（改这里） =====
PHOTO_DIR = r"D:\photos\01_景观规划"
META_FILE = os.path.join(PHOTO_DIR, "_pending.json")
PREFIX    = "01_"
# 二选一输入（另一个留空 ""）
DELETE_LIST = r"F:\APP\delete_list.txt"     # 人工清单(文件名列表)
AI_RESULTS  = os.path.join(PHOTO_DIR, "_ai_results.json")  # AI 结果
# ==========================

recs = json.load(open(META_FILE, encoding="utf-8"))
meta_by_file = {r["file"]: r for r in recs}
shutil.copyfile(META_FILE, META_FILE + ".bak")

# 解析待删集合
delset = set()
src = ""
if DELETE_LIST and os.path.exists(DELETE_LIST):
    src = "delete_list.txt"
    with open(DELETE_LIST, encoding="utf-8") as f:
        delset = set(l.strip() for l in f if l.strip())
elif AI_RESULTS and os.path.exists(AI_RESULTS):
    src = "_ai_results.json"
    data = json.load(open(AI_RESULTS, encoding="utf-8"))
    for fn, v in data.items():
        if isinstance(v, dict) and v.get("decision") == "fail":
            delset.add(fn)
        elif v == "fail":
            delset.add(fn)
else:
    print("!! 未找到删除清单/AI结果, 退出"); sys.exit(1)

print("输入来源:", src, "| 待删:", len(delset), "张")

deleted = 0
for fn in delset:
    p = os.path.join(PHOTO_DIR, fn)
    if os.path.exists(p):
        os.remove(p); deleted += 1; print("  已删:", fn)
    else:
        print("  不存在:", fn)
print("实际删除:", deleted)

# 剩余顺序重命名
remaining = sorted([f for f in os.listdir(PHOTO_DIR) if f.startswith(PREFIX) and f.endswith(".jpg")],
                   key=lambda x: int(x.split("_")[1].split(".")[0]))
tmp_of = {}
for fn in remaining:
    t = "tmp_ap_%05d.jpg" % int(fn.split("_")[1].split(".")[0])
    os.rename(os.path.join(PHOTO_DIR, fn), os.path.join(PHOTO_DIR, t))
    tmp_of[fn] = t
renames = {}
for i, fn in enumerate(remaining, 1):
    new = "%s%04d.jpg" % (PREFIX, i)
    os.rename(os.path.join(PHOTO_DIR, tmp_of[fn]), os.path.join(PHOTO_DIR, new))
    renames[fn] = new

new_recs = []
for old, new in renames.items():
    rec = meta_by_file.get(old)
    if not rec:
        print("  警告: 无元数据", old); continue
    rec["file"] = new; rec["image_id"] = new[:-4]
    rec["local_path"] = os.path.join(PHOTO_DIR, new)
    new_recs.append(rec)
new_recs.sort(key=lambda r: int(r["file"].split("_")[1].split(".")[0]))
json.dump(new_recs, open(META_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("重命名完成:", remaining[0], "~", remaining[-1] if remaining else "-")
print("元数据更新:", len(new_recs), "条 ->", META_FILE)
print("下一步: finalize_table.py 写入采集表 (或 integrate.py 先合并批次)")
