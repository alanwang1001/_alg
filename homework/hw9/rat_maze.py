def dfs_maze():
    maze = [list("#############"),
            list("#S#       #.#"),
            list("# # ##### # #"),
            list("# # #   # # #"),
            list("#   # #   #E#"),
            list("#############")]
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    start = end = None
    
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            if maze[r][c] == 'S': start = (r, c)
            if maze[r][c] == 'E': end = (r, c)
            
    path = []
    visited = set()
    
    def dfs(r, c):
        if (r, c) == end:
            path.append((r, c))
            return True
        if (r, c) in visited or maze[r][c] == '#':
            return False
        
        visited.add((r, c))
        path.append((r, c))
        
        for dr, dc in dirs:
            if dfs(r + dr, c + dc): 
                return True
                
        path.pop()
        return False
        
    dfs(start[0], start[1])
    print(f"找到路徑！長度 = {len(path)} 格，共嘗試 {len(visited)} 次\n")
    
    for r, c in path:
        if maze[r][c] not in ('S', 'E'):
            maze[r][c] = '*'
            
    for row in maze: 
        print("".join(row))

if __name__ == "__main__":
    dfs_maze()
