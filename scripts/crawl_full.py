# -*- coding: utf-8 -*-
"""大批量爬取：断点续传 + 单实例锁 + 内容去重。
改顶部参数后运行。中断后重跑会自动从断点继续。"""
import os, sys, json, importlib, hashlib, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import cat_dir

# ===== 参数（只改任务相关；路径自动解析，不用手写） =====
SITE     = "pexels"
QUERY    = "landscape planning"
TARGET   = 206                 # = estimate.py 算出的 N
CATEGORY = "01"
PREFIX   = "01_"               # 正式批前缀
CAT_FOLDER = "01_景观规划"     # 照片子目录名（对应上面 CATEGORY）
OUT_DIR  = cat_dir(CAT_FOLDER)
LOCK_FILE = os.path.join(OUT_DIR, ".crawl_lock")
DL_SLEEP  = 1.0                # 每张间隔(秒)，防限流
# ==========================

mod = importlib.import_module("sites." + SITE)
os.makedirs(OUT_DIR, exist_ok=True)
META = os.path.join(OUT_DIR, "_pending.json")

# 单实例锁（防止幽灵爬虫并发污染）
if os.path.exists(LOCK_FILE):
    print("!! 锁文件存在, 已有实例在跑。若确认无进程, 删除:", LOCK_FILE, "后重试。退出。")
    sys.exit(1)
open(LOCK_FILE, "w").write(str(os.getpid()))

def cleanup():
    try: os.remove(LOCK_FILE)
    except: pass

try:
    # 断点续传：读已有记录
    records = json.load(open(META, encoding="utf-8")) if os.path.exists(META) else []
    have_files = set(r["file"] for r in records)
    have_hashes = set()
    for r in records:
        p = r.get("local_path") or os.path.join(OUT_DIR, r["file"])
        if os.path.exists(p):
            have_hashes.add(hashlib.md5(open(p, "rb").read()).hexdigest())
    print("续传: 已有", len(records), "条记录")

    seen_urls, page, fails = set(), 0, 0
    while len(records) < TARGET:
        page += 1
        try:
            cands = mod.search(QUERY, 40, page)
        except Exception as e:
            print("  search err:", e); time.sleep(5); continue
        if not cands:
            print("无更多候选, page", page); break
        for c in cands:
            if len(records) >= TARGET:
                break
            if c.get("page_url") in seen_urls:
                continue
            seen_urls.add(c.get("page_url"))
            # 内容去重
            tmp = os.path.join(OUT_DIR, "tmp_dl.jpg")
            ok, info = mod.download(c["src_url"], tmp)
            if not ok:
                fails += 1; print("  FAIL", info); continue
            h = hashlib.md5(open(tmp, "rb").read()).hexdigest()
            if h in have_hashes:
                os.remove(tmp); continue   # 重复图跳过
            idx = len(records) + 1
            fname = "%s%04d.jpg" % (PREFIX, idx)
            os.rename(tmp, os.path.join(OUT_DIR, fname))
            have_hashes.add(h)
            records.append({"image_id": fname[:-4], "file": fname,
                            "function_category": CATEGORY, "source_type": SITE,
                            "license": c.get("license", ""), "source_url": c.get("page_url", ""),
                            "author": c.get("author", ""), "local_path": os.path.join(OUT_DIR, fname),
                            "meta": c.get("meta", {})})
            print("  [%d/%d] %s %s" % (idx, TARGET, fname, c.get("author", "")))
            time.sleep(DL_SLEEP)
            if len(records) % 20 == 0:
                json.dump(records, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(records, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("完成: 共", len(records), "张 ->", META, " 失败/跳过:", fails)
finally:
    cleanup()
