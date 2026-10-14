import numpy as np
import matplotlib.pyplot as plt

# 設定中文字體支援 (依作業系統自動切換常見字體，避免中文亂碼)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'PingFang TC', 'Heiti TC', 'Noto Sans CJK TC', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

# 1. 定義黃金比例理論真值與三種迭代函數
phi = (1.0 + 5.0 ** 0.5) / 2.0  # 理論真值 ≈ 1.618033988749895

f1 = lambda x: (x + 1.0) ** 0.5            # 根號法：單調線性收斂
f2 = lambda x: 1.0 + 1.0 / x               # 倒數法：震盪線性收斂
f3 = lambda x: (x * x + 1.0) / (2.0 * x - 1.0) # 牛頓法：二次極速收斂

# 2. 初始化並記錄迭代歷程 (包含第 0 次初始狀態 x0 = 1.0)
n_iters = 20
x1, x2, x3 = 1.0, 1.0, 1.0

hist_x1, hist_x2, hist_x3 = [x1], [x2], [x3]

for _ in range(n_iters):
    x1, x2, x3 = f1(x1), f2(x2), f3(x3)
    hist_x1.append(x1)
    hist_x2.append(x2)
    hist_x3.append(x3)

# 轉換為 NumPy 陣列以利計算
steps = np.arange(0, n_iters + 1)
hist_x1 = np.array(hist_x1)
hist_x2 = np.array(hist_x2)
hist_x3 = np.array(hist_x3)

# 3. 計算絕對誤差 |x_k - phi|
# 注意：雙精度浮點數極限約為 1e-16，當誤差為 0 時在 log 圖上無法顯示，
# 因此使用 np.maximum 將最小誤差限制在機器精度 eps (約 2.22e-16) 以利繪圖
eps = np.finfo(float).eps
err1 = np.maximum(np.abs(hist_x1 - phi), eps)
err2 = np.maximum(np.abs(hist_x2 - phi), eps)
err3 = np.maximum(np.abs(hist_x3 - phi), eps)

# =====================================================================
# 4. 繪製雙子圖：左圖為「對數誤差收斂圖」，右圖為「數值震盪/單調逼近軌跡」
# =====================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=120)

# --- 左圖：對數誤差收斂曲線 (Log-scale Convergence Plot) ---
ax1.semilogy(steps, err1, 'o-', color='#1f77b4', label=r'$f_1(x) = \sqrt{x+1}$ (根號法：線性收斂)', linewidth=2, markersize=5)
ax1.semilogy(steps, err2, 's--', color='#ff7f0e', label=r'$f_2(x) = 1 + 1/x$ (倒數法：線性收斂)', linewidth=2, markersize=5)
ax1.semilogy(steps, err3, '^-', color='#2ca02c', label=r'$f_3(x) = \frac{x^2+1}{2x-1}$ (牛頓法：二次收斂)', linewidth=2.5, markersize=6)

# 標示機器精度極限線
ax1.axhline(eps, color='gray', linestyle=':', linewidth=1.2, label=f'雙精度浮點數極限 ($\epsilon \\approx 2.22\\times 10^{{-16}}$)')

ax1.set_title('黃金比例迭代法：對數絕對誤差收斂圖 (Log-Scale)', fontsize=13, fontweight='bold', pad=10)
ax1.set_xlabel('迭代次數 $k$ (Iteration)', fontsize=11)
ax1.set_ylabel(r'絕對誤差 $|x_k - \phi|$ (Log Scale)', fontsize=11)
ax1.set_xticks(range(0, n_iters + 1, 2))
ax1.grid(True, which="both", linestyle='--', alpha=0.5)
ax1.legend(loc='upper right', fontsize=9.5)

# --- 右圖：前 10 次迭代的數值逼近軌跡 ---
show_steps = 10
ax2.plot(steps[:show_steps+1], hist_x1[:show_steps+1], 'o-', color='#1f77b4', label=r'$f_1(x)$ 單調遞增逼近', linewidth=2)
ax2.plot(steps[:show_steps+1], hist_x2[:show_steps+1], 's--', color='#ff7f0e', label=r'$f_2(x)$ 上下震盪包夾', linewidth=2)
ax2.plot(steps[:show_steps+1], hist_x3[:show_steps+1], '^-', color='#2ca02c', label=r'$f_3(x)$ 牛頓法極速收斂', linewidth=2)
ax2.axhline(phi, color='red', linestyle='-', alpha=0.6, linewidth=1.5, label=f'理論真值 $\\phi \\approx {phi:.6f}$')

ax2.set_title('前 10 次迭代數值逼近軌跡比較', fontsize=13, fontweight='bold', pad=10)
ax2.set_xlabel('迭代次數 $k$ (Iteration)', fontsize=11)
ax2.set_ylabel('迭代估計值 $x_k$', fontsize=11)
ax2.set_xticks(range(0, show_steps + 1))
ax2.grid(True, linestyle='--', alpha=0.5)
ax2.legend(loc='lower right', fontsize=9.5)

plt.tight_layout()
plt.savefig('golden_ratio_convergence.png', dpi=300) # 自動儲存高解析度圖片供報告使用
plt.show()
