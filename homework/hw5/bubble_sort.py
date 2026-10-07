"""
bubble_sort.py
自製 my_reduce, my_map, my_filter（全程遞迴無 for/while），
並以純遞迴實現泡沫排序與排序檢查。
"""

_MISSING = object()

def my_reduce(func, seq, init=_MISSING):
    """自製 reduce：以輔助遞迴函式取代迴圈"""
    data = list(seq)
    if init is _MISSING:
        if not data:
            raise TypeError("my_reduce() of empty sequence with no initial value")
        acc, rest = data[0], data[1:]
    else:
        acc, rest = init, data

    def go(accumulator, remaining):
        if not remaining:
            return accumulator
        return go(func(accumulator, remaining[0]), remaining[1:])

    return go(acc, rest)


def my_map(func, seq):
    """以 my_reduce 疊合建構 map"""
    return my_reduce(lambda acc, x: acc + [func(x)], list(seq), [])


def my_filter(pred, seq):
    """以 my_reduce 疊合建構 filter"""
    return my_reduce(lambda acc, x: acc + [x] if pred(x) else acc, list(seq), [])


def bubble_pass(lst):
    """
    使用 my_reduce 完成單趟泡沫冒泡。
    accumulator = (out_list, carry, swapped)
    """
    if len(lst) <= 1:
        return list(lst), False

    def step(acc, x):
        out, carry, swapped = acc
        if carry <= x:
            return (out + [carry], x, swapped)
        return (out + [x], carry, True)

    out, carry, swapped = my_reduce(step, lst[1:], ([], lst[0], False))
    return out + [carry], swapped


def bubble_sort(lst):
    """純遞迴外層取代 while 迴圈"""
    def loop(arr):
        arr2, swapped = bubble_pass(arr)
        return arr2 if not swapped else loop(arr2)
    return loop(list(lst))


def is_sorted(lst):
    """無迴圈判斷列表是否已升序排列"""
    pairs = list(zip(lst, lst[1:]))
    return my_reduce(lambda ok, p: ok and (p[0] <= p[1]), pairs, True)


if __name__ == '__main__':
    print("=" * 60)
    print("自製 my_map / my_filter / my_reduce 示範")
    print("=" * 60)
    raw = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"原始資料           : {raw}")
    print(f"my_map(x^2)        : {my_map(lambda x: x**2, raw)}")
    print(f"my_filter(偶數)    : {my_filter(lambda x: x % 2 == 0, raw)}")
    print(f"my_reduce(+)       : {my_reduce(lambda a, b: a + b, raw)}")
    print(f"my_reduce(*, init=1): {my_reduce(lambda a, b: a * b, raw, 1)}")

    print("\n" + "=" * 60)
    print("泡沫排序 (禁止迴圈)")
    print("=" * 60)
    tests = [
        [5, 2, 9, 1, 5, 6],
        [3, 1, 2],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [42],
        [],
        [7, 7, 7, 2, 2, 9, 0, -1, 15, -3]
    ]

    for t in tests:
        sorted_arr = bubble_sort(t)
        ok = is_sorted(sorted_arr)
        print(f"  {str(t):<35} -> {str(sorted_arr):<35} (升序: {ok})")

    print("\n補充：把三個自製工具串起來")
    print("  (先篩出偶數 -> 平方 -> 泡沫排序)")
    pipe_test = [9, 2, 7, 4, 6, 1, 8, 3]
    evens = my_filter(lambda x: x % 2 == 0, pipe_test)
    squares = my_map(lambda x: x**2, evens)
    final_res = bubble_sort(squares)
    print(f"  {pipe_test} -> {final_res}")
