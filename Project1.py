from docplex.mp.model import Model

def solve_optimal_transport(N, K, d):
    model = Model('optimal_transport')
    
    # Variables
    x = {(i, j, k): model.binary_var(name='x_{0}_{1}_{2}'.format(i, j, k)) for i in range(N + 1) for j in range(N + 1) for k in range(K)}
    
    u = {(i,k): model.continuous_var(name='u_{0}_{1}') for i in range(0, N + 1) for k in range(K)}    
    # Objective function
    model.minimize(model.sum(d[i][j] * x[i, j, k] for i in range(N + 1) for j in range(N + 1) for k in range(K)))
    
    # Constraints
    # Ensure each trip start from 0 and end at 0
    for k in range(K):
        model.add_constraint(model.sum(x[0, j, k] for j in range(1, N + 1)) == 1)
        model.add_constraint(model.sum(x[i, 0, k] for i in range(1, N + 1)) == 1)
    # Ensure each point is visited exactly once by one officer
    for i in range(1, N + 1):
        model.add_constraint(model.sum(x[i, j, k] for j in range(N + 1) for k in range(K)) == 1)
    for j in range(1, N + 1):
        model.add_constraint(model.sum(x[i, j, k] for i in range(N + 1) for k in range(K)) == 1)
    # ensure officer in and out thte same point
    for j in range(1,N+1):
        for k in range(K):
            model.add_constraint(model.sum(x[i,j,k]  - x[j,t,k] for i in range(N+1) for t in range(N+1)) == 0)
    # MTZ constraint
    for k in range(K):
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                M = 1e4
                model.add_constraint(u[j,k] - u[i,k] -1 <= M * (1 - x[i,j,k]))
                model.add_constraint(u[j,k] - u[i,k] -1 >= -M * (1 - x[i,j,k]))
    #solve the problem
    model.solve()
    if model.solution is not None:
        total_distance = model.objective_value
        transport_plan = {(i, j, k): x[i, j, k].solution_value for i in range(N + 1) for j in range(N + 1) for k in range(K)}
        return total_distance, transport_plan
    else:
        return None, None
    
def print_transport_result(N, K, transport_plan):
    """
    In kết quả vận chuyển theo thứ tự di chuyển của từng xe.
    """
    for k in range(K):
        print("Engineer", k + 1, "movement:")
        current_location = 0  # Điểm xuất phát
        visited = [0]  # Danh sách các điểm đã đi qua
        count_starting_point = 0  # Đếm số lần đi qua điểm xuất phát
        while True:
            next_location = None
            for i in range(N + 1):
                for j in range(N + 1):
                    if transport_plan[i, j, k] == 1 and i == current_location and j not in visited:
                        next_location = j
                        break
                if next_location is not None:
                    break
            # Kết thúc di chuyển nếu quay trở lại điểm xuất phát sau lần thứ hai
            if next_location is None or (next_location == 0 and count_starting_point > 0):
                break
            print("Move from point", current_location,
                  "to point", next_location)
            if next_location == 0:
                count_starting_point += 1
            current_location = next_location
            visited.append(next_location)
        print("Return to starting point")
        print()
N = 6
K = 2
d = [
[0, 2, 5, 9, 14, 20, 25],
[2, 0, 3, 7, 12, 18, 23],
[5, 3, 0, 4, 9, 15, 20],
[9, 7, 4, 0, 5, 11, 16],
[14, 12, 9, 5, 0, 6, 11],
[20, 18, 15, 11, 6, 0, 5],
[25, 23, 20, 16, 11, 5, 0]
]

total_distance, transport_plan = solve_optimal_transport(N, K, d)
print('Total distance:', total_distance)
print('Transport plan:', transport_plan)
print_transport_result(N, K, transport_plan)