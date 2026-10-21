if __name__ == "__main__":
    text_a = "ABCABBA"
    text_b = "CBABAC"
    
    print("=== DP (LCS) 執行結果 ===")
    print(diff_dp(text_a, text_b))
    
    print("\n=== Myers 執行結果 ===")
    print(diff_myers(text_a, text_b))
