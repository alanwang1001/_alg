"""
hanoi.py
包含遞迴法、顯式堆疊模擬法、奇偶方向法，並包含互相驗證與合法性檢查。
"""

def hanoi_recursive(n, src='A', aux='B', dst='C'):
    """1.1 遞迴版"""
    moves = []
    def solve(k, s, a, d):
        if k == 0:
            return
        solve(k - 1, s, d, a)
        moves.append((s, d))
        solve(k - 1, a, s, d)
    solve(n, src, aux, dst)
    return moves


def hanoi_iterative(n, src='A', aux='B', dst='C'):
    """1.2 禁止遞迴版 (一)：顯式堆疊模擬"""
    moves = []
    stack = [(n, src, aux, dst)]
    while stack:
        k, s, a, d = stack.pop()
        if k == 1:
            moves.append((s, d))
        else:
            # LIFO 逆序入棧：先執行的最後 push
            stack.append((k - 1, a, s, d))   # 3. 輔助 -> 目標
            stack.append((1, s, a, d))       # 2. 來源 -> 目標
            stack.append((k - 1, s, d, a))   # 1. 來源 -> 輔助
    return moves


def hanoi_parity(n, src='A', aux='B', dst='C'):
    """1.3 禁止遞迴版 (二)：奇偶方向法"""
    moves = []
    pegs = {src: list(reversed(range(1, n + 1))), aux: [], dst: []}
    
    # 決定最小盤的循環移動方向
    ring = [src, dst, aux] if n % 2 == 1 else [src, aux, dst]
    min_peg = src
    total_moves = (1 << n) - 1

    for step in range(1, total_moves + 1):
        if step % 2 == 1:
            # 奇數步：搬移最小盤（盤 1）
            curr_idx = ring.index(min_peg)
            next_peg = ring[(curr_idx + 1) % 3]
            disk = pegs[min_peg].pop()
            pegs[next_peg].append(disk)
            moves.append((min_peg, next_peg))
            min_peg = next_peg
        else:
            # 偶數步：在另外兩根柱子之間做唯一合法的搬移
            other_pegs = [p for p in [src, aux, dst] if p != min_peg]
            p1, p2 = other_pegs[0], other_pegs[1]
            top1 = pegs[p1][-1] if pegs[p1] else float('inf')
            top2 = pegs[p2][-1] if pegs[p2] else float('inf')
            
            if top1 < top2:
                pegs[p2].append(pegs[p1].pop())
                moves.append((p1, p2))
            else:
                pegs[p1].append(pegs[p2].pop())
                moves.append((p2, p1))
                
    return moves


def is_valid_moves(n, moves, src='A', dst='C'):
    """驗證移動序列合法性：無大壓小，最後全部盤子皆在 dst"""
    pegs = {p: [] for p in ['A', 'B', 'C']}
    pegs[src] = list(reversed(range(1, n + 1)))
    
    for s, d in moves:
        if not pegs[s]:
            return False
        disk = pegs[s].pop()
        if pegs[d] and pegs[d][-1] < disk:
            return False
        pegs[d].append(disk)
        
    return pegs[dst] == list(reversed(range(1, n + 1)))


if __name__ == '__main__':
    print("=" * 60)
    print("河內塔：遞迴 vs 禁止遞迴")
    print("=" * 60)
    
    for n in range(1, 6):
        r_moves = hanoi_recursive(n)
        i_moves = hanoi_iterative(n)
        p_moves = hanoi_parity(n)
        
        expected_len = 2**n - 1
        all_equal = (r_moves == i_moves == p_moves)
        all_valid = all(is_valid_moves(n, m) for m in (r_moves, i_moves, p_moves))
        
        print(f"n={n}: 步數={len(r_moves):2d} (預期 {expected_len:2d})  "
              f"遞迴==堆疊==奇偶: {str(all_equal):<5}  三種皆合法: {all_valid}")

    print("\n" + "-" * 60)
    n = 4
    m4 = hanoi_recursive(n)
    print(f"n={n} 的移動序列 (共 {len(m4)} 步):")
    for i, (s, d) in enumerate(m4, 1):
        print(f"{i:4d}. {s} -> {d}", end="\n" if i % 5 == 0 else "   ")
    print("-" * 60)
