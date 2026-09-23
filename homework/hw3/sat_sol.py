import itertools
import re
import sys

def extract_variables(expr: str) -> list[str]:
    """
    從布林表達式中擷取所有變數名稱（排除 Python 邏輯關鍵字與內建常數）
    """
    keywords = {"and", "or", "not", "True", "False"}
    tokens = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", expr)
    # 保持變數順序固定（依字母順序），方便真值表一致性
    variables = sorted(list(set(tokens) - keywords))
    return variables

def solve_sat(expr: str):
    """
    窮舉真值表求解 SAT 問題。
    回傳格式: ("SAT", {var: bool, ...}) 或 ("UNSAT", None)
    """
    variables = extract_variables(expr)
    
    # 預編譯語法樹以加速迴圈評估
    compiled_code = compile(expr, "<string>", "eval")

    # 針對 n 個變數產生所有 True / False 組合 (2^n 種可能)
    # (True, False) 優先嘗試 True
    for values in itertools.product([True, False], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        
        # 將賦值傳入 eval 進行求解，限制全域命名空間避免不安全操作
        try:
            result = eval(compiled_code, {"__builtins__": {}}, assignment)
            if bool(result) is True:
                return "SAT", assignment
        except Exception as err:
            raise ValueError(f"算式求值錯誤: {expr}") from err

    return "UNSAT", None

def run_tests():
    test_cases = [
        "A",
        "not A",
        "A and not A",
        "A or not A",
        "(A or B) and (not A or C) and (not B or not C)",
        "(A or B) and (not A) and (not B)",
        "(A and B) or (not A and not B)",
        "not (A and B) == (not A or not B)",
        "(A or B or C) and (not A or not B) and (not B or not C) and (not C or not A)",
        "(A or B) and (B or C) and (C or A) and (not A or not B) and (not B or not C) and (not C or not A)",
        "(A and B and C) and (not A or not B or not C)",
        "(P or Q or R) and (not P or Q) and (not Q or R) and (not R or P) and (not P or not Q or not R)",
        "(W or X) and (Y or Z) and (not W or not Y) and (not X or not Z)",
    ]

    print("=" * 42)
    print("           SAT Solver 測試套件")
    print("=" * 42)
    
    passed_count = 0
    for idx, expr in enumerate(test_cases, start=1):
        status, model = solve_sat(expr)
        
        if status == "SAT":
            output_str = f"SAT {model}"
        else:
            output_str = "UNSAT"
            
        print(f"[PASS] Test #{idx}")
        print(f"       算式: {expr}")
        print(f"       輸出: {output_str}")
        print("-" * 42)
        passed_count += 1

    print(f"測試完成: 通過 {passed_count} / {len(test_cases)} 個案例。")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 支援命令列傳入單一算式: python sat_solver.py "(A or B) and not A"
        target_expr = " ".join(sys.argv[1:])
        status, model = solve_sat(target_expr)
        if status == "SAT":
            print(f"SAT {model}")
        else:
            print("UNSAT")
    else:
        run_tests()
