from collections import deque

def lee_algorithm():
    grid = [['.' for _ in range(10)] for _ in range(8)]
    for r in range(2, 6): grid[r][4] = '#'
    start, end = (0, 0), (5, 7)
    
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        curr, path = queue.popleft()
        if curr == end:
            for r, c in path:
                if grid[r][c] == '.': grid[r][c] = '1'
            grid[start[0]][start[1]] = 'A'
            grid[end[0]][end[1]] = 'B'
            for row in grid: print(" ".join(row))
            print(f"\nLee 演算法 (BFS) 找到長度 {len(path)-1} 的最短線路")
            return
            
        r, c = curr
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 10 and grid[nr][nc] != '#' and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))

if __name__ == "__main__":
    lee_algorithm()
