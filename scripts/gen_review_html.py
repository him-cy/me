# -*- coding: utf-8 -*-
"""生成图片核查 HTML 页面（人工模式）。改参数后运行。"""
import os, json, html, sys
sys.stdout.reconfigure(encoding="utf-8")

# ===== 参数（改这里） =====
PHOTO_DIR = r"D:\photos\01_景观规划"
PENDING   = os.path.join(PHOTO_DIR, "_pending.json")   # 或 _pending_sample.json
OUT_HTML  = r"C:\Users\51323\.openclaw\workspace\review.html"
PREFIX    = "01_"        # 仅统计此前缀文件
TITLE     = "01 景观规划 核查"
LIST_NAME = "delete_list.txt"
CRITERIA  = "合格: 真实景观/规划照片, 主体清晰。不合格: 地图/平面图/示意图/截图/低分辨率(<800px)/水印广告/无关内容/重复。"
# ==========================

records = json.load(open(PENDING, encoding="utf-8"))
rec_map = {r.get("file", ""): r for r in records}
files = sorted(
    [f for f in os.listdir(PHOTO_DIR) if f.startswith(PREFIX) and f.endswith((".jpg", ".png"))],
    key=lambda x: int(x.split("_")[1].split(".")[0])
)

L = []
L.append("""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><title>%s</title>
<style>
body{font-family:sans-serif;background:#f5f5f5;margin:0;padding:20px}
.toolbar{position:sticky;top:0;background:#fff;padding:10px;border-bottom:2px solid #1976D2;margin-bottom:14px;z-index:100}
.toolbar span{margin-right:14px;color:#555}
#sc{font-weight:bold;color:#e53935}
.imgs{display:flex;flex-wrap:wrap;gap:10px}
.card{background:#fff;border:2px solid #ddd;border-radius:6px;padding:6px;width:220px;position:relative}
.card.bad{border-color:#e53935;background:#fff3f3}
.card img{width:208px;height:140px;object-fit:cover;border-radius:4px;cursor:pointer;display:block}
.card .nm{font-size:12px;color:#555;margin-top:4px;word-break:break-all;max-height:34px;overflow:hidden}
.card .au{font-size:11px;color:#1976D2;font-weight:bold;margin-top:2px}
.lab{position:absolute;top:6px;right:6px;background:rgba(255,255,255,.85);padding:2px 4px;border-radius:3px;font-size:11px;cursor:pointer;z-index:5}
.ov{position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(229,57,53,.3);border-radius:4px;display:none;pointer-events:none}
.card.bad .ov{display:block}
.btn{padding:6px 14px;border:none;border-radius:4px;cursor:pointer;font-size:14px;margin-right:6px}
.bd{background:#e53935;color:#fff}.br{background:#888;color:#fff}
#info{background:#fff3cd;padding:8px 12px;border-radius:4px;margin-bottom:10px;font-size:13px;color:#856404}
</style></head><body>
<div class="toolbar"><span>%s · 共 <strong>%d</strong> 张</span>
<span>已标记: <strong id="sc">0</strong> 张</span>
<button class="btn bd" onclick="dl()">下载删除列表</button>
<button class="btn br" onclick="resetAll()">重置</button></div>
<div id="info">%s<br>操作: 点图或右上角「删除」勾选; 红框=待删。完成后点「下载删除列表」把 %s 发给 AI 处理(暂不自动删)。</div>
<div class="imgs">""" % (TITLE, TITLE, len(files), CRITERIA, LIST_NAME))

for f in files:
    rec = rec_map.get(f, {})
    author = html.escape(str(rec.get("author", ""))[:30]) if rec else ""
    title = html.escape((f + ("  " + author if author else ""))[:60])
    cid = html.escape(f, quote=True)
    thumb = os.path.join(PHOTO_DIR, f).replace("\\", "/")
    L.append("""<div class="card" id="c-%s"><label class="lab"><input type="checkbox" class="chx" id="x-%s" onclick="tg('%s')"> 删除</label>
<img src="file:///%s" onclick="tg('%s')" title="%s"><div class="ov"></div><div class="au">%s</div><div class="nm" title="%s">%s</div></div>"""
% (cid, cid, cid, thumb, cid, title, author, title, title))

L.append("""</div>
<script>
var bad=[];
function tg(id){var c=document.getElementById('c-'+id);if(!c)return;var x=document.getElementById('x-'+id);x.checked=!x.checked;
if(x.checked){c.classList.add('bad');if(!bad.includes(id))bad.push(id);}else{c.classList.remove('bad');bad=bad.filter(function(y){return y!==id;});}
document.getElementById('sc').textContent=bad.length;}
function resetAll(){bad=[];document.querySelectorAll('.card').forEach(function(c){c.classList.remove('bad');});document.querySelectorAll('.chx').forEach(function(x){x.checked=false;});document.getElementById('sc').textContent='0';}
function dl(){if(!bad.length){alert('未选中');return;}var t=bad.join('\\n');var b=new Blob([t],{type:'text/plain'});var a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='%s';a.click();alert('已下载 %s ('+bad.length+' 张), 发给 AI 处理。');}
</script></body></html>""" % (LIST_NAME, LIST_NAME))

html_content = "\n".join(L)
with open(OUT_HTML, "w", encoding="utf-8") as fp:
    fp.write(html_content)
for dst in [r"C:\Users\51323\Desktop\review.html", os.path.join(PHOTO_DIR, "review.html")]:
    try:
        with open(dst, "w", encoding="utf-8") as fp:
            fp.write(html_content)
    except: pass
print("已生成:", OUT_HTML, "共", len(files), "张")
