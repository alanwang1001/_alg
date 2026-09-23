# SAT 布林滿足問題求解

用 gemini, 對話 -- [gemini](https://share.gemini.google/1kU6sEA8yWfy)


## 執行結果

```sh
(.venv) ccc@teacherdeiMac week3 % ./test.sh
==========================================
          SAT Solver 測試套件
==========================================
[PASS] Test #1
       算式: A
       輸出: SAT {'A': True}
------------------------------------------
[PASS] Test #2
       算式: not A
       輸出: SAT {'A': False}
------------------------------------------
[PASS] Test #3
       算式: A and not A
       輸出: UNSAT
------------------------------------------
[PASS] Test #4
       算式: A or not A
       輸出: SAT {'A': True}
------------------------------------------
[PASS] Test #5
       算式: (A or B) and (not A or C) and (not B or not C)
       輸出: SAT {'A': True, 'B': False, 'C': True}
------------------------------------------
[PASS] Test #6
       算式: (A or B) and (not A) and (not B)
       輸出: UNSAT
------------------------------------------
[PASS] Test #7
       算式: (A and B) or (not A and not B)
       輸出: SAT {'A': True, 'B': True}
------------------------------------------
[PASS] Test #8
       算式: not (A and B) == (not A or not B)
       輸出: SAT {'A': True, 'B': True}
------------------------------------------
[PASS] Test #9
       算式: (A or B or C) and (not A or not B) and (not B or not C) and (not C or not A)
       輸出: SAT {'A': True, 'B': False, 'C': False}
------------------------------------------
[PASS] Test #10
       算式: (A or B) and (B or C) and (C or A) and (not A or not B) and (not B or not C) and (not C or not A)
       輸出: UNSAT
------------------------------------------
[PASS] Test #11
       算式: (A and B and C) and (not A or not B or not C)
       輸出: UNSAT
------------------------------------------
[PASS] Test #12
       算式: (P or Q or R) and (not P or Q) and (not Q or R) and (not R or P) and (not P or not Q or not R)
       輸出: UNSAT
------------------------------------------
[PASS] Test #13
       算式: (W or X) and (Y or Z) and (not W or not Y) and (not X or not Z)
       輸出: SAT {'W': True, 'X': False, 'Y': False, 'Z': True}
------------------------------------------
測試完成: 通過 13 / 13 個案例。
```

---

## 自我理解與程式運作原理說明

### 1. 什麼是 SAT 問題？
SAT（Boolean Satisfiability Problem，布林可滿足性問題）是計算機科學中著名的經典問題。核心目標很單純：給定一個布林邏輯算式，判斷**是否存在至少一組變數的真假賦值（True / False），使得整個邏輯算式的結果為 True**。
- **SAT（可滿足）**：能找到至少一種指派方法讓式子為真。例如 `A or not A`，不管 $A$ 是 True 還是 False，結果都是真。
- **UNSAT（不可滿足）**：無論變數怎麼設定，算式結果永遠為假（矛盾）。例如 `A and not A`。

在計算複雜度理論中，SAT 是歷史上第一個被證明的 NP-Complete（NP 完全）問題。這意味著目前尚未發現可在多項式時間內保證解出任意 SAT 的演算法，在最壞情況下，最直覺也最具確定性的解法就是**暴力枚舉（Brute-force）**真值表的所有組合。

---

### 2. 程式架構與執行機制

本作業實作的 `sat_solver.py` 主要透過「**辨識變數 $\rightarrow$ 列舉賦值 $\rightarrow$ 代入求值**」三部曲來完成求解：

#### (1) 自動擷取命題變數 (`extract_variables`)
算式是以字串形式傳入（例如 `"(A or B) and not C"`），程式首先需要知道算式裡到底有哪些未知數：
- 使用正規表達式 `\b[a-zA-Z_][a-zA-Z0-9_]*\b` 找出所有英文單詞。
- 排除 Python 的邏輯保留字（`and`、`or`、`not`、`True`、`False`）。
- 使用 `set()` 去除重複變數，並透過 `sorted()` 固定順序，保證真值表枚舉時的一致性。

#### (2) 系統性真值表枚舉 (`solve_sat`)
假設式子中共有 $n$ 個相異變數，真值表就會有 $2^n$ 種可能的狀態組合：
- 使用 Python 內建的 `itertools.product([True, False], repeat=n)`，依序生成笛卡爾積。
- 透過 `dict(zip(variables, values))` 將變數名稱與布林值綁定成鍵值對（例如 `{'A': True, 'B': False}`）。

#### (3) 動態評估與早停機制（Early Exit）
- **效能加速**：在進入迴圈前，先以 `compile(expr, "<string>", "eval")` 將字串預編譯為 Bytecode，避免每次迴圈重新解析語法。
- **安全隔離**：利用 `eval(compiled_code, {"__builtins__": {}}, assignment)` 求值，限制只有傳入的變數生效，防止執行未授權的內建函式。
- **早停機制**：只要發現某組賦值能讓算式為 True，立刻回傳 `("SAT", assignment)`；若全部 $2^n$ 種可能性都檢查過依然為 False，才回傳 `("UNSAT", None)`。

---

### 3. 演算法複雜度分析

| 項目 | 複雜度 | 說明 |
| :--- | :--- | :--- |
| **時間複雜度** | $O(2^n \cdot L)$ | $n$ 為相異變數數量，$L$ 為算式長度。每次驗證需花費與算式長度成正比的評估時間，在最壞情況（UNSAT）下必須驗證完所有 $2^n$ 種賦值。 |
| **空間複雜度** | $O(n + L)$ | `itertools.product` 是產生器（Generator），不會一口氣將所有排列塞入記憶體；主要空間開銷僅為儲存變數集合與編譯後的語法樹。 |

---

### 4. 心得與討論
暴力搜尋真值表在變數較少（例如本作業測資中的 $1 \sim 4$ 個變數，$2^4 = 16$ 種）時運算速度極快且能保證正確性。然而，當變數數量增加到數十個時（如 $2^{30}$），暴力法會面臨「組合爆炸」，在運算時間上難以承受。現代工業級的 SAT Solver（如 Z3、MiniSat）會透過 CNF 標準形式、DPLL 演算法（回溯與單一文字傳播）或 CDCL（衝突驅動子句學習）進行大規模剪枝，這也是後續演算法深入值得探索的方向。
