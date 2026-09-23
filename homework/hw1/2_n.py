import sys
import time

# 提高遞迴深度上限以防較大 n 值觸發 RecursionError（Python 預設為 1000）
sys.setrecursionlimit(2000)

# 方法 1：內建次方運算子
def power2n_1(n: int) -> int:
    return 2 ** n

# 方法 2a：雙遞迴加法
def power2n_2a(n: int) -> int:
    if n == 0:
        return 1
    return power2n_2a(n - 1) + power2n_2a(n - 1)

# 方法 2b：單遞迴乘法
def power2n_2b(n: int) -> int:
    if n == 0:
        return 1
    return 2 * power2n_2b(n - 1)

# 方法 3：遞迴 + 查表（Memoization 記憶化）
def power2n_3(n: int, memo: dict = None) -> int:
    if memo is None:
        memo = {}
    if n == 0:
        return 1
    if n in memo:
        return memo[n]
    
    # 透過查表避免重複計算分支
    memo[n] = power2n_3(n - 1, memo) + power2n_3(n - 1, memo)
    return memo[n]


def benchmark_method(name: str, func, n: int, skip_if_too_slow: bool = False):
    """測試函式執行時間與結果"""
    print(f"=== 測試 {name} (n = {n}) ===")
    
    if skip_if_too_slow and n > 30:
        print(f"警告：{name} 的時間複雜度為 O(2^n)。")
        print(f"在 n = {n} 時，計算次數高達約 2^{n} ≈ {2**n:.2e} 次，在常規電腦上無法在合理時間內完成，故跳過執行。\n")
        return None, None

    start_time = time.perf_counter()
    try:
        result = func(n)
        elapsed = time.perf_counter() - start_time
        print(f"執行時間: {elapsed:.8f} 秒")
        # 只印出前 10 位與末 10 位以保持簡潔
        result_str = str(result)
        if len(result_str) > 30:
            preview = f"{result_str[:10]}...{result_str[-10:]} (共 {len(result_str)} 位數)"
        else:
            preview = result_str
        print(f"計算結果: {preview}\n")
        return result, elapsed
    except RecursionError:
        print("錯誤：超過最大遞迴深度（RecursionError）！\n")
        return None, None


if __name__ == "__main__":
    test_n = 100
    print(f"開始評測四種方法計算 2^{test_n}：\n" + "=" * 40 + "\n")

    # 1. 測試方法 1
    benchmark_method("方法 1 (2**n)", power2n_1, test_n)

    # 2. 測試方法 2a
    # 注意：方法 2a 針對 n=100 絕對出不來，這裡先展示較小的 n=25，並說明 n=100 跳過
    print("【方法 2a 特別示範】先以 n = 25 測試其速度：")
    benchmark_method("方法 2a (雙遞迴加法)", power2n_2a, 25)
    print("【方法 2a 正式測試】")
    benchmark_method("方法 2a (雙遞迴加法)", power2n_2a, test_n, skip_if_too_slow=True)

    # 3. 測試方法 2b
    benchmark_method("方法 2b (單遞迴乘法)", power2n_2b, test_n)

    # 4. 測試方法 3
    benchmark_method("方法 3 (遞迴 + 查表)", power2n_3, test_n)
