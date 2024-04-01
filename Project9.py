from docplex.mp.model import Model
import numpy



def solve_optimal_transport(N, K, distances, t):
    model = Model('optimal_transport')
    
    # Variables
    x = {(i, j, k): model.binary_var(name='x_{0}_{1}_{2}'.format(i, j, k))
         for i in range(N + 1) for j in range(N + 1) for k in range(K)}    
    
    # Objective function
    model.minimize(model.sum(distances[i][j] * x[i, j, k] + t[i] for i in range(N + 1)
                             for j in range(N + 1) for k in range(K)))
    
    # Constraints
    # Ensure each trip start from 0 and end at 0
    model.add_constraint(model.sum(x[0, j, k] for j in range(1, N + 1) for k in range(K)) == 1)
    model.add_constraint(model.sum(x[i, 0, k] for i in range(1, N + 1) for k in range(K)) == 1)
    # Ensure each point is visited exactly once
    for i in range(1, N+1):
        model.add_constraint(model.sum(x[i, j, k] for j in range(1, N+1) for k in range(K)) == 1)
    for j in range(1, N+1):
        model.add_constraint(model.sum(x[i, j, k] for i in range(1, N+1) for k in range(K)) == 1)
    # Ensure no engineer from i to i
    model.add_constraints(x[i,i,k] == 0 for i in range(N+1) for k in range(K))
    for i in range(N + 1):
        for j in range(N + 1):
            model.add_constraint((x[j, i] + x[i, j] ) <= 1)    # type: ignore

    # Solve the problem
    model.solve()
    
    # Get the solution
    if model.solution is not None:
        total_distance = model.objective_value
        transport_plan = {(i, j, k): x[i, j, k].solution_value
                          for i in range(N + 1) for j in range(N + 1) for k in range(K)}
        return total_distance, transport_plan
    else:
        return None, None
    
def print_transport_result(N, K, transport_plan):
    
    for k in range(K):
        print("Engineer ", k + 1, "moves:")
        current_location = 0
        visited = [0]
        count_starting_point = 0
        while True:
            next_location = None
            for i in range(N + 1):
                for j in range(N + 1):
                    if transport_plan[i, j, k] == 1 and i == current_location and j not in visited:
                        next_location = j
                        break
                if next_location is not None:
                    break
            if next_location is None or (next_location == 0 and count_starting_point > 0):
                break
            print("Move from point", current_location, "to point", next_location)
            if next_location == 0:
                count_starting_point += 1
            current_location = next_location
            visited.append(next_location)
        print("Return to the starting point")
        print()

# Example usage
N = 4  # Number of customers
K = 2  # Number of engineers
distances = [[0, 1, 2, 3, 4],
             [1, 0, 1, 2, 3],
             [2, 1, 0, 1, 2],
             [3, 2, 1, 0, 1],
             [4, 3, 2, 1, 0]]  # Distance matrix
t = [0, 1, 2, 3, 4]  # Time to serve each customer

total_distance, transport_plan = solve_optimal_transport(N, K, distances, t)
print('Total distance:', total_distance)
print('Transport plan:', transport_plan)
print_transport_result(N, K, transport_plan)