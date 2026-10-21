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
