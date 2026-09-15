# -*- coding: utf-8 -*-
"""Pexels 适配器（已验证可用）。"""
import os, requests

# 默认用从 pexels.vercel.app 公开 SPA 提取的 demo key（共享、限流 200/小时）。
# 自用/发布请到 https://www.pexels.com/api/ 申请自己的 key，并设环境变量 PEXELS_API_KEY。
DEMO_KEY = "563492ad6f917000010000014107a189a4414daab1f39ceefe900972"
KEY = os.environ.get("PEXELS_API_KEY", DEMO_KEY)
API = "https://api.pexels.com/v1/search"
HEADERS = {"Authorization": KEY, "User-Agent": "Mozilla/5.0"}


def search(query, n, page=1):
    """返回标准候选 dict 列表。n 为本次请求数量(≤80)。"""
    r = requests.get(API, params={"query": query, "per_page": min(n, 80), "page": page},
                     headers=HEADERS, timeout=25)
    if r.status_code != 200:
        raise RuntimeError("Pexels search %d: %s" % (r.status_code, r.text[:120]))
    photos = r.json().get("photos", [])
    out = []
    for p in photos:
        src = p.get("src", {})
        url = src.get("large2x") or src.get("original") or src.get("large")
        if not url:
            continue
        out.append({
            "src_url": url,
            "page_url": p.get("url", ""),
            "author": p.get("photographer", ""),
            "license": "Pexels License (free to use)",
            "meta": {"pexels_id": p.get("id"), "alt": p.get("alt", "")},
        })
    return out


def download(url, path, timeout=30):
    """浏览器 UA 下载；返回 (成功?, 字节数或错误)。"""
    h = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.pexels.com/"}
    try:
        r = requests.get(url, headers=h, timeout=timeout)
        if r.status_code == 200 and len(r.content) > 8000:
            with open(path, "wb") as f:
                f.write(r.content)
            return True, len(r.content)
        return False, "status=%d len=%d" % (r.status_code, len(r.content))
    except Exception as e:
        return False, str(e)[:80]
