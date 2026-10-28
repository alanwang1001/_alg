import numpy as np
import random
import math

# ==========================================
# 0. 環境設定與共用函數
# ==========================================
def create_distance_matrix(num_cities=10):
    """隨機生成城市座標，並計算兩兩之間的距離矩陣"""
    np.random.seed(42) # 固定隨機種子以便重現結果
    cities = np.random.rand(num_cities, 2) * 100
    dist_matrix = np.zeros((num_cities, num_cities))
    for i in range(num_cities):
        for j in range(num_cities):
            dist_matrix[i][j] = np.linalg.norm(cities[i] - cities[j])
    return dist_matrix

def calc_total_distance(route, dist_matrix):
    """計算一條路徑的總長度 (包含回到起點)"""
    if len(set(route)) != len(dist_matrix): 
        return float('inf') # 確保是合法路徑
    dist = 0
    n = len(route)
    for i in range(n):
        dist += dist_matrix[route[i]][route[(i + 1) % n]]
    return dist

# ==========================================
# 1. 改良法 (2-opt 演算法)
# ==========================================
def two_opt(route, dist_matrix):
    """透過反轉交叉路徑來進行局部改良"""
    n = len(route)
    best_route = route.copy()
    best_dist = calc_total_distance(best_route, dist_matrix)
    improved = True
    
    while improved:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n):
                if j - i == 1: continue # 相鄰節點不需反轉
                
                # 執行 2-opt 交換：反轉 i 到 j 之間的路徑
                new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                new_dist = calc_total_distance(new_route, dist_matrix)
                
                if new_dist < best_dist:
                    best_dist = new_dist
                    best_route = new_route
                    improved = True
    return best_route

# ==========================================
# 2. 爬山演算法 (Hill Climbing)
# ==========================================
def hill_climbing(route, dist_matrix):
    """每次尋找最佳的鄰近狀態(交換兩城市)，只往更好的方向走"""
    n = len(route)
    current_route = route.copy()
    current_dist = calc_total_distance(current_route, dist_matrix)
    
    while True:
        best_neighbor_route = None
        best_neighbor_dist = current_dist
        
        # 窮舉所有可能的交換作為鄰近解
        for i in range(n):
            for j in range(i + 1, n):
                neighbor = current_route.copy()
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i] # 交換
                dist = calc_total_distance(neighbor, dist_matrix)
                
                if dist < best_neighbor_dist:
                    best_neighbor_dist = dist
                    best_neighbor_route = neighbor
                    
        # 若找到更好的鄰近解，則移動；否則(卡在局部最佳解)結束
        if best_neighbor_route is not None:
            current_route = best_neighbor_route
            current_dist = best_neighbor_dist
        else:
            break
            
    return current_route

# ==========================================
# 3. 模擬退火法 (Simulated Annealing)
# ==========================================
def simulated_annealing(route, dist_matrix, initial_temp=1000, cooling_rate=0.99):
    """允許以一定機率接受較差的解，以跳脫局部最佳解"""
    n = len(route)
    current_route = route.copy()
    current_dist = calc_total_distance(current_route, dist_matrix)
    
    best_route = current_route.copy()
    best_dist = current_dist
    temp = initial_temp
    
    while temp > 1:
        # 隨機產生一個鄰近解 (隨機交換兩城市)
        i, j = random.sample(range(n), 2)
        neighbor = current_route.copy()
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        neighbor_dist = calc_total_distance(neighbor, dist_matrix)
        
        delta = neighbor_dist - current_dist
        
        # Metropolis 準則：若變好則接受，若變差則依溫度機率接受
        if delta < 0 or random.random() < math.exp(-delta / temp):
            current_route = neighbor
            current_dist = neighbor_dist
            
            if current_dist < best_dist:
                best_dist = current_dist
                best_route = current_route.copy()
                
        temp *= cooling_rate # 降溫
        
    return best_route

# ==========================================
# 4. 梯度下降法 (連續空間神經網路概念 - Hopfield Network 簡化版)
# ==========================================
def gradient_descent_hopfield(dist_matrix, iterations=500, lr=0.01):
    """
    傳統梯度下降無法直接用於離散的 TSP。
    此處展示將 TSP 轉換為連續狀態空間的能量函數，並用梯度下降更新狀態的經典做法。
    (註：此方法難以調參且易產生不合法路徑，此為概念展示)
    """
    n = len(dist_matrix)
    # U 代表每個神經元的內部狀態 (n x n 矩陣，表示城市在特定位置的機率)
    U = np.random.randn(n, n) * 0.1
    # 懲罰權重參數
    A, B, C, D = 500, 500, 200, 500 

    for _ in range(iterations):
        V = 0.5 * (1 + np.tanh(U)) # 連續輸出，範圍 (0, 1)
        dU = np.zeros((n, n))
        
        for x in range(n):
            for i in range(n):
                # 能量函數的偏微分 (梯度)
                row_sum = np.sum(V[x, :]) - V[x, i]             # 條件 1: 同一城市不能佔用兩個位置
                col_sum = np.sum(V[:, i]) - V[x, i]             # 條件 2: 同一位置不能有兩個城市
                total_sum = np.sum(V) - n                       # 條件 3: 總和必須為 n
                
                prev_i, next_i = (i - 1) % n, (i + 1) % n
                dist_penalty = sum(dist_matrix[x, y] * (V[y, prev_i] + V[y, next_i]) for y in range(n) if y != x) # 條件 4: 距離懲罰
                
                dU[x, i] = -A * row_sum - B * col_sum - C * total_sum - D * dist_penalty
        
        U += lr * dU # 梯度下降更新狀態
        
    # 將連續狀態解析回離散路徑 (Greedy Decoding)
    V = 0.5 * (1 + np.tanh(U))
    route = []
    used = set()
    for i in range(n):
        city = np.argmax(V[:, i])
        # 處理非法衝突 (強制修復以利測試)
        while city in used:
            V[city, i] = -1 # 排除已用城市
            city = np.argmax(V[:, i])
        route.append(city)
        used.add(city)
        
    return route

# ==========================================
# 5. 貪婪演算法 (Nearest Neighbor)
# ==========================================
def greedy_tsp(dist_matrix, start_city=0):
    """每次都選擇距離目前城市最近且尚未訪問過的城市"""
    n = len(dist_matrix)
    unvisited = set(range(n))
    route = [start_city]
    unvisited.remove(start_city)
    current = start_city
    
    while unvisited:
        # 找尋距離 current 最近的下一個城市
        next_city = min(unvisited, key=lambda city: dist_matrix[current][city])
        route.append(next_city)
        unvisited.remove(next_city)
        current = next_city
        
    return route

# ==========================================
# 執行與比較測試
# ==========================================
if __name__ == "__main__":
    NUM_CITIES = 10
    dist_matrix = create_distance_matrix(NUM_CITIES)
    
    # 建立一個隨機初始路徑供需要初始解的演算法使用
    random_initial_route = list(range(NUM_CITIES))
    random.shuffle(random_initial_route)
    print(f"隨機初始路徑距離: {calc_total_distance(random_initial_route, dist_matrix):.2f}\n")
    
    # 1. 改良法 (以隨機路徑作為初始)
    route_2opt = two_opt(random_initial_route, dist_matrix)
    print(f"[1] 改良法 (2-opt) 距離: {calc_total_distance(route_2opt, dist_matrix):.2f}")
    
    # 2. 爬山演算法 (以隨機路徑作為初始)
    route_hc = hill_climbing(random_initial_route, dist_matrix)
    print(f"[2] 爬山演算法距離: {calc_total_distance(route_hc, dist_matrix):.2f}")
    
    # 3. 模擬退火法 (以隨機路徑作為初始)
    route_sa = simulated_annealing(random_initial_route, dist_matrix)
    print(f"[3] 模擬退火法距離: {calc_total_distance(route_sa, dist_matrix):.2f}")
    
    # 4. 梯度下降法 (Hopfield Network)
    route_grad = gradient_descent_hopfield(dist_matrix)
    print(f"[4] 梯度下降法(神經網路) 距離: {calc_total_distance(route_grad, dist_matrix):.2f}")
    
    # 5. 貪婪演算法
    route_greedy = greedy_tsp(dist_matrix)
    print(f"[5] 貪婪演算法距離: {calc_total_distance(route_greedy, dist_matrix):.2f}")
    
    # 常見實戰組合：用貪婪演算法產生初始解，再餵給 2-opt 改良
    combined_route = two_opt(route_greedy, dist_matrix)
    print(f"\n[*] 實戰組合 (貪婪 + 改良法) 距離: {calc_total_distance(combined_route, dist_matrix):.2f}")
