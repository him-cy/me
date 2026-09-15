# -*- coding: utf-8 -*-
"""自动配置层：按运行环境解析路径与解释器，用户无需改任何路径。
可通过环境变量覆盖（见每项说明）。本文件不依赖第三方库。"""
import os, sys, shutil

def detect_python():
    """返回可用的 python 解释器。优先当前解释器, 其次 PATH 中的 python/python3/py, 再试常见 bundled 位置。"""
    cands = []
    if getattr(sys, "executable", None):
        cands.append(sys.executable)
    for cmd in ("python", "python3", "py"):
        p = shutil.which(cmd)
        if p:
            cands.append(p)
    # 常见 OpenClaw / QClaw / Claude bundled python（环境而异, 仅作兜底）
    extra = [
        os.path.join(os.environ.get("OPENCLAW_HOME", ""), "resources", "python", "python.exe"),
        r"D:\skill\QClaw\v0.2.36.628\resources\python\python.exe",
    ]
    for e in extra:
        if e and os.path.isfile(e):
            cands.append(e)
    seen, out = set(), []
    for c in cands:
        if c and c not in seen:
            seen.add(c); out.append(c)
    return out[0] if out else "python"

PYTHON = detect_python()

def first_existing(cands):
    for c in cands:
        if c and os.path.exists(c):
            return c
    return cands[-1]

# 照片根目录：默认 ~/photos；若作者机器 D:\photos 已存在则沿用；可设 COLLECT_PHOTOS 覆盖
PHOTOS_DIR = os.environ.get("COLLECT_PHOTOS") or first_existing([
    r"D:\photos",
    os.path.expanduser("~/photos"),
])

# 采集表：默认 ~/采集记录表.xlsx；若作者机器 G 盘表已存在则沿用；可设 COLLECT_TABLE 覆盖
TABLE_PATH = os.environ.get("COLLECT_TABLE") or first_existing([
    r"G:\数据采集项目需求文档\数据采集项目需求文档\采集记录表.xlsx",
    os.path.expanduser("~/采集记录表.xlsx"),
])

# 用户回传的删除清单目录
DELETE_DIR = os.environ.get("COLLECT_DELETE_DIR") or os.path.expanduser("~/delete_lists")

# 工作/临时目录（核查页 HTML、AI 中间产物等）
WORKSPACE = os.environ.get("COLLECT_WORKSPACE") or os.path.join(PHOTOS_DIR, "_work")

for _d in (WORKSPACE, DELETE_DIR):
    try: os.makedirs(_d, exist_ok=True)
    except: pass

def cat_dir(category_folder):
    """分类照片目录：PHOTOS_DIR / <category_folder>，自动创建并返回。"""
    d = os.path.join(PHOTOS_DIR, category_folder)
    try: os.makedirs(d, exist_ok=True)
    except: pass
    return d

def ensure(pkg):
    """缺第三方库时自动 pip 安装（用当前解释器）。"""
    try:
        __import__(pkg)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", pkg])
