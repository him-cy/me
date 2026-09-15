# -*- coding: utf-8 -*-
"""新增站点模板：拷贝本文件为 sites/<name>.py 并实现 search()。
路径/解释器由 scripts/_config.py 自动解析，无需在此处理。"""
try:
    import requests
except ImportError:
    import subprocess, sys as _sys
    subprocess.check_call([_sys.executable, "-m", "pip", "install", "--quiet", "requests"])
    import requests


def search(query, n, page=1):
    """返回标准候选 dict 列表：
    {"src_url": 直链, "page_url": 来源页, "author": 作者, "license": 许可, "meta": {...}}
    """
    raise NotImplementedError("实现 search()：调用站点 API，归一化为标准 dict")
    # 示例骨架：
    # r = requests.get(API, params={"q": query, "page": page}, headers=UA, timeout=25)
    # return [{"src_url":..., "page_url":..., "author":..., "license":..., "meta":{}} for item in r.json()["items"]]


def download(url, path, timeout=30):
    """默认浏览器 UA 下载；子类可覆盖（如 Wikimedia 需自定义 UA）。"""
    h = {"User-Agent": "Mozilla/5.0 (research; contact@example.com)"}
    try:
        r = requests.get(url, headers=h, timeout=timeout)
        if r.status_code == 200 and len(r.content) > 8000:
            with open(path, "wb") as f:
                f.write(r.content)
            return True, len(r.content)
        return False, "status=%d" % r.status_code
    except Exception as e:
        return False, str(e)[:80]
