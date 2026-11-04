def solve_nqueens(n=8):
    ans = []
    
    def dfs(queens):
        if len(queens) == n:
            ans.append(queens)
            return
        row = len(queens)
        for col in range(n):
            if all(c != col and abs(r - row) != abs(c - col) for r, c in enumerate(queens)):
                dfs(queens + [col])
                
    dfs([])
    print(f"共找到 {len(ans)} 組解（理論值 {len(ans)}）\n")
    if ans:
        print(f"解 1：行號序列 = {ans[0]}")
        for col in ans[0]:
            print(". " * col + "Q " + ". " * (n - col - 1))

if __name__ == "__main__":
    solve_nqueens()
