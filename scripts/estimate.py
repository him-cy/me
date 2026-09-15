# -*- coding: utf-8 -*-
"""根据需求量与样本合格率估算大样本爬取量。改参数后运行。"""
import math, sys
sys.stdout.reconfigure(encoding="utf-8")

# ===== 参数（改这里） =====
DEMAND    = 100      # 最终需要的合格图数量
SAMPLE_N  = 30       # 样本量
QUALIFIED = 21       # 样本中合格数
FAIL_BUF  = 0.15     # 失败/重复缓冲
N_CAP     = 2000     # 上限保护
# ==========================

if QUALIFIED <= 0:
    print("样本合格数=0, 无法估算。建议: 换关键词/站点/放宽标准。")
    sys.exit(1)

p_hat = QUALIFIED / SAMPLE_N
z = 1.96
denom = 1 + z*z/SAMPLE_N
center = (p_hat + z*z/(2*SAMPLE_N)) / denom
margin = z * math.sqrt(p_hat*(1-p_hat)/SAMPLE_N + z*z/(4*SAMPLE_N**2)) / denom
p_lower = max(0.0, center - margin)

N = math.ceil(DEMAND / p_lower * (1 + FAIL_BUF))
N = min(N, N_CAP)

print("样本量 n      =", SAMPLE_N)
print("合格数 q      =", QUALIFIED)
print("点估计 p_hat  = %.3f" % p_hat)
print("Wilson 95%% 下界 p_lower = %.3f" % p_lower)
print("失败缓冲      = %.0f%%" % (FAIL_BUF*100))
print("→ 估算爬取量 N = %d 张" % N)
print("  预期合格 ≈ %.0f 张 (留缓冲后保留 %d)" % (N*p_hat, DEMAND))
if p_lower < 0.3:
    print("⚠ 合格率偏低, 建议换源/放宽标准后再估。")
print("下一步: 把 N 填入 crawl_full.py 的 TARGET 运行。")
