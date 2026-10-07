# HW5：遞迴與反遞迴 — 河內塔、符號微分、自製 map/filter/reduce 泡沫排序

本專案實作三個主題：河內塔求解與反向驗證、AST 符號微分運算，以及純函式無迴圈泡沫排序。

## 檔案架構

* `hanoi.py`：河內塔問題（遞迴版、顯式堆疊模擬版、奇偶方向法），並交叉比對驗證。
* `sym_diff.py`：遞迴下降分析器、AST 遞迴符號微分、化簡與中央差分數值比對。
* `bubble_sort.py`：純遞迴自製 `my_reduce`、`my_map`、`my_filter`，並全程無 `for`/`while` 實作泡沫排序。
* `readme.md`：說明文件。

## 執行方式

本專案僅依賴 Python 3 標準函式庫（`math`, `re`），無須安裝任何第三方套件：

```bash
python3 hanoi.py
python3 sym_diff.py
python3 bubble_sort.py
