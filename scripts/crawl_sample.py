# -*- coding: utf-8 -*-
"""小样本爬取：测试合格率用。改顶部参数后运行。"""
import os, sys, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ===== 参数（改这里） =====
SITE     = "pexels"            # 站点适配器名（见 scripts/sites/）
QUERY    = "landscape planning"
SAMPLE_N = 30                  # 样本量（用户定义）
CATEGORY = "01"                # 采集表分类
PREFIX   = "S01_"              # 样本文件名前缀（区别于正式批）
OUT_DIR  = r"D:\photos\01_景观规划"
# ==========================

mod = importlib.import_module("sites." + SITE)
os.makedirs(OUT_DIR, exist_ok=True)
META = os.path.join(OUT_DIR, "_pending_sample.json")

records, seen, page = [], set(), 0
print("样本爬取: site=%s query=%s n=%d" % (SITE, QUERY, SAMPLE_N))
while len(records) < SAMPLE_N:
    page += 1
    cands = mod.search(QUERY, SAMPLE_N - len(records) + 5, page)
    if not cands:
        print("无更多候选, page", page); break
    for c in cands:
        if c.get("page_url") in seen:
            continue
        seen.add(c.get("page_url"))
        idx = len(records) + 1
        fname = "%s%04d.jpg" % (PREFIX, idx)
        ok, info = mod.download(c["src_url"], os.path.join(OUT_DIR, fname))
        if not ok:
            print("  FAIL", fname, info); continue
        rec = {"image_id": fname[:-4], "file": fname,
               "function_category": CATEGORY, "source_type": SITE,
               "license": c.get("license", ""), "source_url": c.get("page_url", ""),
               "author": c.get("author", ""), "local_path": os.path.join(OUT_DIR, fname),
               "meta": c.get("meta", {})}
        records.append(rec)
        print("  [%d/%d] %s %s %s" % (idx, SAMPLE_N, fname, c.get("author", ""), info if isinstance(info, int) else ""))
        if len(records) >= SAMPLE_N:
            break

json.dump(records, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("样本完成:", len(records), "张 ->", META)
print("下一步: 用人工(gen_review_html.py)或AI(verify_ai.py)核查, 统计合格数后跑 estimate.py")
