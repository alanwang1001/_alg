# 黃金比例不動點迭代法：收斂分析與 Matplotlib 視覺化說明

本文件旨在探討求解非線性方程式 $x^2 - x - 1 = 0$（其正根即為黃金比例 $\phi = \frac{1+\sqrt{5}}{2} \approx 1.618033988749895$）的三種不同迭代格式，並透過 Python 的 `matplotlib` 套件繪製**半對數絕對誤差收斂曲線圖（Log-scale Convergence Plot）**與**數值逼近軌跡圖**，以視覺化方式驗證數值分析中的收斂階數（Order of Convergence）理論。

---

## 一、 三種迭代格式與收斂速率理論推導

將原方程式 $x^2 - x - 1 = 0$ 改寫為 $x = g(x)$ 的不動點迭代形式 $x_{k+1} = g(x_k)$。根據不動點收斂定理，當在真值 $\phi$ 附近滿足 $\vert{}g'(\phi)\vert{} < 1$ 時，迭代序列必局部收斂，且導數絕對值 $\vert{}g'(\phi)\vert{}$ 決定了漸近誤差常數（Asymptotic Error Constant）：

| 迭代函數代號 | 數學表達式 $g(x)$ | 導函數 $g'(x)$ | 於真值處之導數值 $\vert{}g'(\phi)\vert{}$ | 收斂階數與行為特徵 |
| :--- | :--- | :--- | :--- | :--- |
| **`f1` (根號法)** | $f_1(x) = \sqrt{x + 1}$ | $f_1'(x) = \frac{1}{2\sqrt{x+1}}$ | $\frac{1}{2\phi} \approx 0.3090$ | **一階線性收斂**（斜率為正，單調遞增逼近） |
| **`f2` (倒數法)** | $f_2(x) = 1 + \frac{1}{x}$ | $f_2'(x) = -\frac{1}{x^2}$ | $\left\vert{}-\frac{1}{\phi^2}\right\vert{} \approx 0.3820$ | **一階線性收斂**（斜率為負，上下交替震盪包夾） |
| **`f3` (牛頓法)** | $f_3(x) = \frac{x^2 + 1}{2x - 1}$ | $f_3'(x) = \frac{2x(x-1)-2}{(2x-1)^2}$ | $0$ | **二階（二次）收斂**（有效位數每步翻倍，極速收斂） |

---

## 二、 Matplotlib 視覺化程式碼與設計架構

### 1. 完整實作程式碼

```python
import numpy as np
import matplotlib.pyplot as plt

# 設定中文字體支援 (依作業系統自動切換常見字體，避免中文亂碼)
plt.rcParams['font.sans-serif'] = [
    'Microsoft JhengHei', 'PingFang TC', 'Heiti TC', 
    'Noto Sans CJK TC', 'SimHei', 'Arial Unicode MS'
]
plt.rcParams['axes.unicode_minus'] = False  # 解決座標軸負號顯示問題

# 1. 定義黃金比例理論真值與三種迭代函數
phi = (1.0 + 5.0 ** 0.5) / 2.0  # 理論真值 ≈ 1.618033988749895

f1 = lambda x: (x + 1.0) ** 0.5                 # 根號法：單調線性收斂
f2 = lambda x: 1.0 + 1.0 / x                    # 倒數法：震盪線性收斂
f3 = lambda x: (x * x + 1.0) / (2.0 * x - 1.0)  # 牛頓法：二次極速收斂

# 2. 初始化並記錄迭代歷程 (包含第 0 次初始狀態 x0 = 1.0)
n_iters = 20
x1, x2, x3 = 1.0, 1.0, 1.0

hist_x1, hist_x2, hist_x3 = [x1], [x2], [x3]

for _ in range(n_iters):
    x1, x2, x3 = f1(x1), f2(x2), f3(x3)
    hist_x1.append(x1)
    hist_x2.append(x2)
    hist_x3.append(x3)

# 轉換為 NumPy 陣列以利向量化誤差計算
steps = np.arange(0, n_iters + 1)
hist_x1 = np.array(hist_x1)
hist_x2 = np.array(hist_x2)
hist_x3 = np.array(hist_x3)

# 3. 計算絕對誤差 |x_k - phi| 並進行機器精度下限保護
eps = np.finfo(float).eps  # IEEE 754 雙精度浮點數機器極限 (約 2.22e-16)
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
ax1.axhline(eps, color='gray', linestyle=':', linewidth=1.2, label=f'雙精度浮點數極限 ($\\epsilon \\approx 2.22\\times 10^{{-16}}$)')

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
plt.savefig('golden_ratio_convergence.png', dpi=300)  # 自動輸出 300 DPI 高解析度圖檔
plt.show()
```

### 2. 關鍵繪圖技術細節說明

* **半對數座標軸 (`ax1.semilogy`)**：
  由於迭代誤差會從 $10^{-1}$ 跨越至 $10^{-16}$（相差達 15 個數量級），若使用一般線性 Y 軸，第 3 次迭代後的誤差都會貼平在 0 軸上而無法分辨。使用 `semilogy` 將 Y 軸轉為以 10 為底的對數尺度（$\log_{10}|e_k|$），能清楚展現每個數量級的衰減過程。
* **浮點數機器精度截斷保護 (`np.maximum(..., eps)`)**：
  當牛頓法（`f3`）在第 5 次迭代時，計算出的浮點數與理論真值 `phi` 在 64-bit 雙精度浮點數下已完全相等，此時相減的絕對誤差 $|x_k - \phi| = 0$。由於 $\log_{10}(0) = -\infty$ 會導致對數圖斷線或報錯，程式利用 `np.finfo(float).eps`（約 $2.22 \times 10^{-16}$）作為誤差地板值，讓圖表能完整呈現「抵達機器精度極限」的水平高原期。
* **雙視角子圖對照 (`plt.subplots(1, 2)`)**：
  左圖取絕對值後取對數，雖然能看清收斂階數，但會丟失誤差的「正負號資訊」；因此右圖保留原始數值 $x_k$ 的前 10 步軌跡，直觀呈現單調逼近與正負交替震盪的物理意義。

---

## 三、 圖表結果與數值分析重點

### 1. 左圖解析：對數絕對誤差收斂曲線 (Log-Scale Convergence Plot)
1. **斜直線代表一階線性收斂（`f1` 藍線與 `f2` 橘線）**：
   * 線性收斂滿足 $|e_{k+1}| \approx C |e_k|$，故在第 $k$ 步的誤差為 $|e_k| \approx C^k |e_0|$。
   * 兩邊取對數後得到線性方程式：
     $$\log_{10}|e_k| \approx \log_{10}|e_0| + k \cdot \log_{10}C$$
   * 這解釋了為何 `f1` 與 `f2` 在半對數圖上呈現**兩條筆直向下的斜直線**，且直線的斜率即為 $\log_{10}|g'(\phi)|$。
   * 因為 $|f_1'(\phi)| \approx 0.309 < |f_2'(\phi)| \approx 0.382$，所以 $\log_{10}(0.309) \approx -0.51$ 比 $\log_{10}(0.382) \approx -0.42$ 更負，反應在圖上就是**藍線比橘線更為陡峭**，到第 20 次迭代時，藍線誤差（約 $10^{-11}$）比橘線誤差（約 $10^{-9}$）小了約兩個數量級。
2. **拋物線驟降代表二階二次收斂（`f3` 綠線）**：
   * 牛頓法滿足 $|e_{k+1}| \approx M |e_k|^2$，取對數後呈指數倍增下降：
     $$\log_{10}|e_{k+1}| \approx \log_{10}M + 2 \log_{10}|e_k|$$
   * 每多迭代一次，對數誤差的負值直接翻倍（即有效小數位數翻倍：$10^{-1} \rightarrow 10^{-2} \rightarrow 10^{-4} \rightarrow 10^{-8} \rightarrow 10^{-16}$），因此在對數圖上呈現**向下急遽彎曲的瀑布曲線**。
3. **機器精度地板現象（Machine Epsilon Plateau）**：
   * 綠線在第 **5 次迭代**即撞上灰色虛線（$\epsilon \approx 2.22 \times 10^{-16}$）並轉為水平線，證明牛頓法僅需 5 步即耗盡 64 位元浮點數的所有有效位數，後續迭代不再改變數值。

### 2. 右圖解析：數值逼近軌跡圖 (Trajectory Plot)
1. **`f1` 的單調性**：由於 $f_1'(x) > 0$，當初始值 $x_0 = 1.0 < \phi$ 時，後續所有迭代值皆維持在真值紅線下方，由下往上穩定單調遞增。
2. **`f2` 的費氏數列包夾震盪**：由於 $f_2'(x) < 0$，誤差正負號每步反轉。從 $x_0 = 1$ 開始，序列依序為 $1, \frac{2}{1}, \frac{3}{2}, \frac{5}{3}, \frac{8}{5}, \frac{13}{8}\dots$（恰為相鄰費氏數列之比值），在紅線上下形成阻尼震盪（Damped Oscillation）並逐漸收窄包夾真值。
