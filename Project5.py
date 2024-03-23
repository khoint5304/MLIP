from docplex.mp.model import Model
import numpy


def solve_optimal_transport(N, M,  K, distances, q):
    model = Model('optimal_transport')
    
    # Variables
    x = {(i, j, k): model.binary_var(name='x_{0}_{1}_{2}'.format(i, j, k))
         for i in range(2 * N + 2 * M + 1) for j in range(2 * N + 2 * M + 1) for k in range(K)}
    c = [[] for _ in range(K)]
    p = [[] for _ in range(K)]
        
    # Objective function
    model.minimize(model.sum(distances[i][j] * x[i, j, k] for i in range(2 * N + 2 * M + 1)
                             for j in range(2 * N + 2 * M + 1) for k in range(K)))
    
    # Constraints
    # Ensure each trip start from 0 and end at 0
    model.add_constraint(model.sum(x[0, j, k] for j in range(1, N + M + 1) for k in range(K)) == 1)
    model.add_constraint(model.sum(x[i, 0, k] for i in range(N + M + 1, 2 * N + 2 * M + 1) for k in range(K)) == 1)
    model.add_constraint(model.sum(x[0, j, k] for j in range(N + M + 1, 2 * N + 2 * M + 1) for k in range(K)) == 0)
    model.add_constraint(model.sum(x[i, 0, k] for i in range(1, N + M + 1) for k in range(K)) == 0)
    # Ensure each point is visited exactly once
    for i in range(1, 2 * N + 2 * M + 1):
        model.add_constraint(model.sum(x[i, j, k] for j in range(2 * N + 2 * M + 1) for k in range(K)) == 1)
    for j in range(1, 2 * N + 2 * M + 1):
        model.add_constraint(model.sum(x[i, j, k] for i in range(2 * N + 2 * M + 1) for k in range(K)) == 1)
    
    # Ensure no bus go from i to i
    model.add_constraints(x[i,i,k] == 0 for i in range(2 * N + 2 * M + 1) for k in range(K))
    
    # Add customers when go through point from 1 to N, remove customers when go through point from N + M + 1 to 2 * N + M + 1
    for k in range(K):
        for i in range(1, 2 * N + 2 * M + 1):
            for j in range(1,N+1):
                if x[i,j,k].equals(1): 
                    c[k].append(j)
    for k in range(K):
        for i in range(1,2*N+1):
            for j in range(N + M + 1,2 * N + M + 1):                
                if x[i,j,k].equals(1):
                    c[k].remove(j - N - M)
                    
    # Add packages when go through point from N + 1 to N + M, remove packages when go through point from 2 * N + M + 1 to 2 * N + 2 * M
    for k in range(K):
        for i in range(1,2 * N + 2 * M + 1):
            for j in range(N + 1,N + M + 1):
                if x[i,j,k].equals(1):
                    p[k].append(j)
    for k in range(K):
        for i in range(1,2 * N + 2 * M + 1):
            for j in range(2 * N + M + 1,2 * N + 2 * M + 1):
                if x[i,j,k].equals(1):
                    p[k].remove(j - N - M)
    # Ensure each bus has no more than 1 customers
    for k in range(K):
        len(c[k]) <= 1 #type: ignore
    # Ensure each bus has no more packages than its weight capacity
    for k in range(K):
        len(p[k]) <= q[k] #type: ignore
    # Solve the problem
    model.solve()
    
    # Get the solution
    if model.solution is not None:
        total_distance = model.objective_value
        transport_plan = {(i, j, k): x[i, j, k].solution_value
                          for i in range(2 * N + 2 * M + 1) for j in range(2 * N + 2 * M + 1) for k in range(K)}
        return total_distance, transport_plan
    else:
        return None, None

def print_transport_result(N, M, K, transport_plan):
    """
    In kết quả vận chuyển theo thứ tự di chuyển của từng xe.
    """
    for k in range(K):
        print("Bus", k + 1, "movement:")
        current_location = 0  # Điểm xuất phát
        visited = [0]  # Danh sách các điểm đã đi qua
        count_starting_point = 0  # Đếm số lần đi qua điểm xuất phát
        while True:
            next_location = None
            for i in range(2 * N + 2 * M + 1):
                for j in range(2 * N + 2 * M + 1):
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
    
# Example usage
N = 1  # Number of passengers
K = 1  # Number of taxis
M = 1  # Number of packages
distances = [[0, 1, 2, 3, 4],
             [1, 0, 1, 2, 3],
             [2, 1, 0, 1, 2],
             [3, 2, 1, 0, 1],
             [4, 3, 2, 1, 0]]  # Example distances matrix
q = [1]  # Capacity of each bus

total_distance, transport_plan = solve_optimal_transport(N, M, K, distances, q)
print('Total distance:', total_distance)
print('Transport plan:', transport_plan)
print_transport_result(N, M, K, transport_plan)
