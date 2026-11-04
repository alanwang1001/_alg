import heapq

def astar_search():
    grid = [list("#############"),
            list("#N...#......#"),
            list("#*#.#.#.####."),
            list("#*      #...#"),
            list("#*##### #####"),
            list("#*#...#     #"),
            list("#*******#E  #"),
            list("#############")]
            
    start = end = None
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 'N': start = (r, c)
            if grid[r][c] == 'E': end = (r, c)
            
    def h(pos):
        return abs(pos[0] - end[0]) + abs(pos[1] - end[1])
        
    pq = [(h(start), 0, start, [start])]
    visited = set()
    
    while pq:
        f, g, curr, path = heapq.heappop(pq)
        if curr == end:
            for r, c in path:
                if grid[r][c] not in ('N', 'E'): grid[r][c] = '*'
            for row in grid: print("".join(row))
            print(f"\nA* 開展完成，找到 {len(path)} 步最短路")
            return
            
        if curr in visited: continue
        visited.add(curr)
        
        r, c = curr
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != '#':
                if (nr, nc) not in visited:
                    heapq.heappush(pq, (g + 1 + h((nr, nc)), g + 1, (nr, nc), path + [(nr, nc)]))

if __name__ == "__main__":
    astar_search()
