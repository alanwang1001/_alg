def T1(n: int) -> int:
    """T(n) = T(n-1) + 8, T(1) = 1"""
    t = 1
    for _ in range(2, n + 1):
        t += 8
    return t

def formula1(n: int) -> int:
    return 8 * n - 7


def T2(n: int) -> int:
    """T(n) = 2 T(n-1) + 9, T(1) = 1"""
    t = 1
    for _ in range(2, n + 1):
        t = 2 * t + 9
    return t

def formula2(n: int) -> int:
    return 10 * 2 ** (n - 1) - 9


def T3(n: int) -> int:
    """T(n) = 2 T(n/2) + 1, T(1) = 1 (n 為 2 的冪)"""
    t = 1
    m = 1
    while m < n:
        t = 2 * t + 1
        m *= 2
    return t

def formula3(n: int) -> int:
    return 2 * n - 1


def T4(n: int) -> int:
    """T(n) = T(n/2) + 1, T(1) = 1 (n 為 2 的冪)"""
    t = 1
    m = 1
    while m < n:
        t += 1
        m *= 2
    return t

def formula4(n: int) -> int:
    return n.bit_length()  # 當 n 為 2 的冪時，等同於 log2(n) + 1


if __name__ == "__main__":
    print("=== 驗證線性遞迴 (T1, T2) ===")
    for n in [1, 2, 4, 8, 16, 100]:
        ok1 = T1(n) == formula1(n)
        ok2 = T2(n) == formula2(n)
        print(f"n={n:<4d} | T1: {T1(n):<5d} (吻合: {str(ok1):<5}) | T2: {T2(n):<32d} (吻合: {str(ok2):<5})")

    print("\n=== 驗證分治遞迴 (T3, T4，n 為 2 的冪) ===")
    for n in [1, 2, 4, 8, 16, 1024]:
        ok3 = T3(n) == formula3(n)
        ok4 = T4(n) == formula4(n)
        print(f"n={n:<4d} | T3: {T3(n):<5d} (吻合: {str(ok3):<5}) | T4: {T4(n):<4d} (吻合: {str(ok4):<5})")

    print("\n" + "="*50)
    print("複雜度總結：")
    print("1. T(n) = T(n-1) + 8   => T(n) = 8n - 7          => O(n)")
    print("2. T(n) = 2T(n-1) + 9  => T(n) = 10*2^(n-1) - 9  => O(2^n)")
    print("3. T(n) = 2T(n/2) + 1  => T(n) = 2n - 1          => O(n)")
    print("4. T(n) = T(n/2) + 1   => T(n) = log2(n) + 1     => O(log n)")
