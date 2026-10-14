# Lambda Calculus Interpreter (Lambda 微型虛擬機)

這是一個完整的 Lambda Calculus 解譯器，以 Python 實作。本專案不僅支援基本的符號運算與語法解析，更同時實作了「有名稱 (Named)」與「無名稱 (De Bruijn Indices)」兩種變數管理機制，並能動態顯示完整的 Beta 歸約 (Beta-reduction) 過程。

本解譯器適合用於程式語言理論 (Programming Language Theory, PLT) 的學習與教學，可直接展示變數捕捉 (Variable Capture)、Alpha 轉換、以及不同求值策略的影響。

## 核心功能 (Features)

*   **雙重內部表示法 (Dual Representation)**：
    *   **Named Mode**: 使用傳統變數名稱，實作防護機制避免變數捕捉，自動執行 $\alpha$-轉換。
    *   **Nameless Mode**: 自動編譯為 De Bruijn 索引 (De Bruijn Indices)，展示現代編譯器處理作用域的數學方法。
*   **雙軌求值策略 (Reduction Strategies)**：
    *   `normal`：正規序 (最左最外)。保證只要表達式有解 (正規形)，就一定能被計算出來。
    *   `applicative`：應用序 (最左最內)。模擬 Call-by-Value 機制，用以測試如 $\Omega$ 等發散結構。
*   **完整的運算追蹤 (Step-by-step Trace)**：
    *   在命令列中標示出每一次歸約的目標 (Redex)，並加上 `【 】` 括號。
    *   清楚印出替換邏輯與 Shift 過程。
*   **內建巨集環境 (Prelude Environment)**：
    *   內建 Church Booleans (`TRUE`, `FALSE`, `AND`, `IF`)。
    *   內建 Church Numerals (`ADD`, `MUL`, `SUCC`, `PRED`)。
    *   內建 Y Combinator 遞迴。
    *   支援將阿拉伯數字 `3` 自動展開為 Church 數字 `λf x.f (f (f x))`。

## 安裝與執行 (Usage)

本程式僅依賴 Python 3.7+ 的標準函式庫，不需安裝任何外部套件。

```bash
# 1. 執行內建的範例展示
python lambda_calculus.py

# 2. 直接在命令列計算表達式
python lambda_calculus.py -e "ADD 2 3"

# 3. 進入互動模式 (REPL)
python lambda_calculus.py --repl

# 4. 指定求值策略與模式
python lambda_calculus.py -e "SUCC 2" --mode nameless --strategy applicative
