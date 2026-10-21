def diff_myers(a, b):
    n, m = len(a), len(b)
    max_d = n + m
    v = {1: 0} # 記錄每條對角線 k 走到的最遠 x 座標
    trace = [] # 記錄每一步的 v 狀態，用於最後回溯

    # 步驟 1：逐層增加差異數 D，尋找最短路徑
    for d in range(max_d + 1):
        trace.append(v.copy())
        for k in range(-d, d + 1, 2):
            # 決定從哪條對角線來：從上方來(新增) 還是 左方來(刪除)
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
        
        # 判斷前一步是從哪個 k 來的
        if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
            prev_k = k + 1
        else:
            prev_k = k - 1
            
        prev_x = v[prev_k]
        prev_y = prev_x - prev_k

        # 處理免費的對角線步數
        while x > prev_x and y > prev_y:
            result.append(f"  {a[x - 1]}")
            x -= 1
            y -= 1
            
        # 處理消耗差異步數 (D) 的操作
        if d > 0:
            if x == prev_x:
                result.append(f"+ {b[y - 1]}") # 新增
            else:
                result.append(f"- {a[x - 1]}") # 刪除
                
        x, y = prev_x, prev_y

    return '\n'.join(reversed(result))
