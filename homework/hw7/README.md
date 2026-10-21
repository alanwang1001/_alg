# 演算法實作解析：Diff (差異比對)

本文件探討如何找出兩個字串或檔案間的「最長共同子序列」(Longest Common Subsequence, LCS) 與「最短編輯腳本」(Shortest Edit Script, SES)。我們將比較兩種經典解法：傳統的**動態規劃 (LCS)**，以及現代版本控制系統廣泛使用的 **Myers O(ND) 演算法**。

---

## 1. 動態規劃解法：LCS 矩陣填表

動態規劃（Dynamic Programming）解決 diff 問題的核心思想是將大問題拆解為子問題，並記錄已知結果以避免重複計算。

### 原理
給定字串 A（長度 $M$）與字串 B（長度 $N$），建立一個大小為 $(M+1) \times (N+1)$ 的二維陣列 `dp`。
`dp[i][j]` 代表 A 的前 $i$ 個字元與 B 的前 $j$ 個字元的最長共同子序列長度。

狀態轉移方程式為：
* 若 $A[i-1] == B[j-1]$：`dp[i][j] = dp[i-1][j-1] + 1` （字元相同，長度加 1）
* 若 $A[i-1] \neq B[j-1]$：`dp[i][j] = \max(dp[i-1][j], dp[i][j-1])` （字元不同，繼承左方或上方較大的值）

填表完成後，再從矩陣右下角往回推導（Backtracking），即可找出兩檔案的差異與相同處。

### 複雜度
* **時間複雜度**：$O(M \times N)$。必須完整填寫整個二維矩陣。
* **空間複雜度**：$O(M \times N)$。需要儲存完整的狀態矩陣以供回溯。

### Python 實作
```python
def diff_dp(a, b):
    m, n = len(a), len(b)
    # 步驟 1：建立 DP 表格 (初始值皆為 0)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # 步驟 2：填表 (計算 LCS 長度)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # 步驟 3：回溯找差異路徑 (從右下角開始)
    i, j = m, n
    result = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            result.append(f"  {a[i - 1]}") # 字元相同，保留
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
            result.append(f"+ {b[j - 1]}") # 新增
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j - 1] < dp[i - 1][j]):
            result.append(f"- {a[i - 1]}") # 刪除
            i -= 1

    return '\n'.join(reversed(result))
```

---

## 2. 非動態規劃解法：Eugene Myers' O(ND) 演算法

目前主流的版本控制系統（如 Git）與 diff 工具，底層使用的主要是 Myers 演算法。它將問題轉化為**圖論中的最短路徑搜尋**，並採用貪婪（Greedy）策略。

### 原理
將字串 A 與 B 畫成一個網格圖，A 在 X 軸，B 在 Y 軸。
* 向右走一步代表從 A「刪除」一個字元（Cost = 1）。
* 向下走一步代表向 B「新增」一個字元（Cost = 1）。
* 若 $A[x] == B[y]$，可以走對角線，代表「保留」該字元（Cost = 0）。

目標是找到從 $(0,0)$ 走到 $(M,N)$ 且 Cost（即差異數 $D$）最小的路徑。Myers 演算法不預先展開整個矩陣，而是按照差異數量 $D = 0, 1, 2...$ 逐層向外探索對角線。

### 複雜度
* **時間複雜度**：$O((M+N) \times D)$。其中 $D$ 是兩個檔案的差異點數量。
* **空間複雜度**：$O(M+N)$。只需記錄每一條對角線目前走到的最遠 X 座標。

### Python 實作
```python
def diff_myers(a, b):
    n, m = len(a), len(b)
    max_d = n + m
    v = {1: 0} # 記錄每條對角線 k 走到的最遠 x 座標
    trace = [] # 記錄每一步的 v 狀態，用於最後回溯

    # 步驟 1：逐層增加差異數 D，尋找最短路徑
    for d in range(max_d + 1):
        trace.append(v.copy())
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[k - 1] < v[k + 1]):
                x = v[k + 1]     # 向下走一步 (在 B 新增)
            else:
                x = v[k - 1] + 1 # 向右走一步 (在 A 刪除)
            y = x - k

            # 遇到相同字元，免費走對角線 (不增加 D)
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            v[k] = x

            # 抵達終點 (右下角)
            if x >= n and y >= m:
                return backtrack_myers(a, b, trace)
    return ""

def backtrack_myers(a, b, trace):
    x, y = len(a), len(b)
    result = []
    
    # 步驟 2：根據 trace 記錄，由終點逆推回起點
    for d in range(len(trace) - 1, -1, -1):
        v = trace[d]
        k = x - y
        
        if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
            prev_k = k + 1
        else:
            prev_k = k - 1
            
        prev_x = v[prev_k]
        prev_y = prev_x - prev_k

        while x > prev_x and y > prev_y:
            result.append(f"  {a[x - 1]}")
            x -= 1
            y -= 1
            
        if d > 0:
            if x == prev_x:
                result.append(f"+ {b[y - 1]}")
            else:
                result.append(f"- {a[x - 1]}")
                
        x, y = prev_x, prev_y

    return '\n'.join(reversed(result))
```

---

## 3. 綜合比較與總結

| 比較項目 | 動態規劃 (LCS DP) | Myers 演算法 (O(ND) 貪婪搜尋) |
| :--- | :--- | :--- |
| **運作核心** | 窮舉所有子問題，建立完整二維矩陣 | 以圖論廣度優先/貪婪探索，優先走對角線（相同字元） |
| **適用場景** | 兩檔案差異極大、或長度較短的學術性比對 | 兩檔案**高度相似**（如程式碼版本控管）的實際工程應用 |
| **時間複雜度** | 穩定為 $O(M \times N)$ | 最佳 $O(M+N)$，最差 $O(M \times N)$ |
| **空間消耗** | 較大 $O(M \times N)$，容易造成記憶體溢出 | 極小 $O(M+N)$ |
| **效能盲點** | 即便兩個檔案完全一模一樣，依然會浪費時間建立完整矩陣 | 當兩檔案完全不相干（$D$ 接近 $M+N$）時，效能會退化至與 DP 相當 |

> **工程實踐的抉擇**：在程式碼或文字檔的比較中，通常修改的行數（$D$）遠小於檔案的總行數（$M, N$）。Myers 演算法巧妙利用了「檔案大部份內容是相同的」這個先驗假設，將運算資源集中在探索差異上，這也是為何它能成為 Git `diff` 標準實作的原因。
