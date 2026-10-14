# ==========================================
# 1. 邱奇布林值 (Church Booleans)
# ==========================================
# TRUE: 接收兩個參數，永遠回傳第一個
TRUE  = lambda x: lambda y: x

# FALSE: 接收兩個參數，永遠回傳第二個
FALSE = lambda x: lambda y: y

# 輔助函數：將邱奇布林值轉為 Python 布林值，方便印出結果
def to_bool(church_bool):
    return church_bool(True)(False)

# ==========================================
# 2. 邏輯閘 (Logic Gates)
# ==========================================
# NOT p = p FALSE TRUE
NOT = lambda p: p(FALSE)(TRUE)

# AND p q = p q p
AND = lambda p: lambda q: p(q)(p)

# OR p q = p p q
OR  = lambda p: lambda q: p(p)(q)

# IF 判斷式：因為 Python 是積極求值，a 和 b 必須是延遲計算的函數 (thunks)
# 最後的 () 負責把被選中的分支執行出來
IF = lambda p: lambda a: lambda b: p(a)(b)()

# ==========================================
# 3. Z 組合子 (適用於積極求值語言的 Y 組合子)
# ==========================================
# 標準 Y: lambda f: (lambda x: f(x(x)))(lambda x: f(x(x))) <- 在 Python 會爆炸
# Z 組合子透過 lambda v: x(x)(v) 來延遲 x(x) 的無限展開
Z = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))

# ==========================================
# 4. 實作遞迴：階乘函數 (Factorial)
# ==========================================
# 這是一個「非遞迴」的高階函數，r 代表未來的自己
# 為了專注展示 Z 組合子，這裡數字運算 n == 0, n * r(n-1) 使用 Python 內建語法
G = lambda r: lambda n: IF(
    # 判斷式：將 Python 判斷轉為邱奇布林值
    TRUE if n == 0 else FALSE
)(
    # IF TRUE 執行：回傳 1 (包裝成 lambda 延遲計算)
    lambda: 1
)(
    # IF FALSE 執行：回傳 n * r(n-1) (包裝成 lambda 延遲計算)
    lambda: n * r(n - 1)
)

# 透過 Z 組合子賦予 G 遞迴能力！
factorial = Z(G)

# ==========================================
# 5. 測試與驗證
# ==========================================
if __name__ == "__main__":
    print("--- 測試邏輯閘 ---")
    print(f"NOT TRUE        -> {to_bool( NOT(TRUE) )}")
    print(f"NOT FALSE       -> {to_bool( NOT(FALSE) )}")
    print(f"AND TRUE FALSE  -> {to_bool( AND(TRUE)(FALSE) )}")
    print(f"AND TRUE TRUE   -> {to_bool( AND(TRUE)(TRUE) )}")
    print(f"OR FALSE TRUE   -> {to_bool( OR(FALSE)(TRUE) )}")
    print(f"OR FALSE FALSE  -> {to_bool( OR(FALSE)(FALSE) )}")
    
    print("\n--- 測試無名函數遞迴 (Z Combinator) ---")
    print("計算 5 的階乘 (5!):")
    result = factorial(5)
    print(f"結果: {result} (預期 120)")
    
    print("\n計算 10 的階乘 (10!):")
    print(f"結果: {factorial(10)} (預期 3628800)")
