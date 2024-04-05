from docplex.mp.model import Model
import numpy


def solve_optimal_transport(N, K, distances, q):
    model = Model('optimal_transport')
    
    # Variables
    x = {(i, j, k): model.binary_var(name='x_{0}_{1}_{2}'.format(i, j, k))
         for i in range(2 * N + 1) for j in range(2 * N + 1) for k in range(K)}
    c = [[] for _ in range(K)]
    u = {(i, k): model.continuous_var(name='u_{0}_{1}'.format(i, k)) for i in range(1, 2 * N + 1) for k in range(K)}
            
    # Objective function
    model.minimize(model.sum(distances[i][j] * x[i, j, k] for i in range(2 * N + 1)
                             for j in range(2 * N + 1) for k in range(K)))
    
    # Constraints
    # Ensure each trip start from 0 and end at 0
    model.add_constraint(model.sum(x[0, j, k] for j in range(1, N + 1) for k in range(K)) == 1)
    model.add_constraint(model.sum(x[i, 0, k] for i in range(N + 1, 2 * N + 1) for k in range(K)) == 1)
    model.add_constraint(model.sum(x[0, j, k] for j in range(N + 1, 2 * N + 1) for k in range(K)) == 0)
    model.add_constraint(model.sum(x[i, 0, k] for i in range(1, N + 1) for k in range(K)) == 0)
    # Ensure each point is visited exactly once
    for i in range(1, 2*N+1):
        model.add_constraint(model.sum(x[i, j, k] for j in range(2*N+1) for k in range(K)) == 1)
    for j in range(1, 2*N+1):
        model.add_constraint(model.sum(x[i, j, k] for i in range(2*N+1) for k in range(K)) == 1)
    
    # MTZ constraint
    for k in range(K):
        for i in range(1,2 * N + 1):
            for j in range(1,2 * N + 1):
                M = 1e4
                model.add_constraint(u[j,k] - u[i,k] -1 <= M * (1 - x[i,j,k]))
                model.add_constraint(u[j,k] - u[i,k] -1 >= -M * (1 - x[i,j,k]))

    # ensure officer in and out thte same point
    for j in range(1,2 * N + 1):
        for k in range(K):
            model.add_constraint(model.sum(x[i,j,k]  - x[j,t,k] for i in range(2 * N + 1) for t in range(2 * N + 1)) == 0)

    
    # Add customers when go through point from 1 to N, remove customers when go through point from N+1 to 2N
    for k in range(K):
        for i in range(1,2*N+1):
            for j in range(1,N+1):
                if x[i,j,k].equals(1): 
                    c[k].append(j)
    for k in range(K):
        for i in range(1,2*N+1):
            for j in range(N+1,2*N+1):                
                if x[i,j,k].equals(1):
                    c[k].remove(j-N)
    # Ensure each bus has no more than q customers
    for k in range(K):
        len(c[k]) <= q[k] #type: ignore

    # Solve the problem
    model.solve()
    
    # Get the solution
    if model.solution is not None:
        total_distance = model.objective_value
        transport_plan = {(i, j, k): x[i, j, k].solution_value
                          for i in range(2 * N + 1) for j in range(2 * N + 1) for k in range(K)}
        return total_distance, transport_plan
    else:
        return None, None

def print_transport_result(N, K, transport_plan):
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
            for i in range(2 * N + 1):
                for j in range(2 * N + 1):
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
N = 6  # Number of passengers
K = 2  # Number of buses
distances = [   [0, 3, 5, 7, 10, 12, 15, 17, 20, 22, 25, 27, 30],   # Điểm 0 (điểm xuất phát)
                [3, 0, 2, 5, 8, 10, 13, 15, 18, 20, 23, 25, 28],    # Điểm 1
                [5, 2, 0, 3, 6, 8, 11, 13, 16, 18, 21, 23, 26],     # Điểm 2
                [7, 5, 3, 0, 3, 5, 8, 10, 13, 15, 18, 20, 23],      # Điểm 3
                [10, 8, 6, 3, 0, 2, 5, 7, 10, 12, 15, 17, 20],      # Điểm 4
                [12, 10, 8, 5, 2, 0, 3, 5, 8, 10, 13, 15, 18],      # Điểm 5
                [15, 13, 11, 8, 5, 3, 0, 2, 5, 7, 10, 12, 15],      # Điểm 6
                [17, 15, 13, 10, 7, 5, 2, 0, 3, 5, 8, 10, 13],      # Điểm 7
                [20, 18, 16, 13, 10, 8, 5, 3, 0, 2, 5, 7, 10],      # Điểm 8
                [22, 20, 18, 15, 12, 10, 7, 5, 2, 0, 3, 5, 8],      # Điểm 9
                [25, 23, 21, 18, 15, 13, 10, 8, 5, 3, 0, 2, 5],     # Điểm 10
                [27, 25, 23, 20, 17, 15, 12, 10, 7, 5, 2, 0, 3],    # Điểm 11
                [30, 28, 26, 23, 20, 18, 15, 13, 10, 8, 5, 3, 0]    # Điểm 12
]  # Example distances matrix
q = [30,30]  # Capacity of each bus

total_distance, transport_plan = solve_optimal_transport(N, K, distances, q)
print('Total distance:', total_distance)
print('Transport plan:', transport_plan)
print_transport_result(N, K, transport_plan)
