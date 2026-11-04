from collections import deque

def bfs_river_crossing():
    start = (0, 0, 0, 0)
    goal = (1, 1, 1, 1)
    
    def is_valid(state):
        f, w, s, c = state
        if f != s and (w == s or s == c): return False
        return True
        
    queue = deque([(start, [])])
    visited = {start}
    names = ["狼", "羊", "菜"]
    
    while queue:
        curr, path = queue.popleft()
        if curr == goal:
            for step in path: 
                print(step)
            return
            
        f, w, s, c = curr
        moves = [
            (1-f, w, s, c),
            (1-f, 1-w, s, c) if f == w else None,
            (1-f, w, 1-s, c) if f == s else None,
            (1-f, w, s, 1-c) if f == c else None
        ]
        
        for i, nxt in enumerate(moves):
            if nxt and nxt not in visited and is_valid(nxt):
                visited.add(nxt)
                action = "農夫單獨過河" if i == 0 else f"農夫帶著{names[i-1]}過河"
                dir_str = "右岸" if nxt[0] == 1 else "左岸"
                queue.append((nxt, path + [f"{action}到{dir_str}   狀態 = {nxt}"]))

if __name__ == "__main__":
    bfs_river_crossing()
