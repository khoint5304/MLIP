from docplex.mp.model import Model


def solve_optimal_transport(N, K, distances, q):
    model = Model('optimal_transport')

    # Variables
    x = {(i, j, k): model.binary_var(name='x_{0}_{1}_{2}'.format(i, j, k))
         for i in range(2 * N + 1) for j in range(2 * N + 1) for k in range(K)}

    # Objective function
    model.minimize(model.sum(distances[i][j] * x[i, j, k] for i in range(2 * N + 1)
                             for j in range(2 * N + 1) for k in range(K)))

    # Constraints
    for i in range(1, N + 1):
        model.add_constraint(model.sum(x[i, j, k] for j in range(N + 1, 2 * N + 1) for k in range(K)) == 1,
                             ctname='from_{0}_to_{1}'.format(i, i + N))
        model.add_constraint(model.sum(x[j, i + N, k] for j in range(N + 1) for k in range(K)) == 1,
                             ctname='from_{0}_to_{1}'.format(i, i + N))

    for k in range(K):
        model.add_constraint(model.sum(x[0, i, k]
                             for i in range(1, N + 1)) == 1)

    # Solve the model
    model.solve()

    # Get the solution
    if True:
        total_distance = model.objective_value
        transport_plan = {(i, j, k): x[i, j, k].solution_value
                          for i in range(2 * N + 1) for j in range(2 * N + 1) for k in range(K)}
        return total_distance, transport_plan
    else:
        return None, None


# Example usage
N = 2  # Number of passengers
K = 1  # Number of buses
distances = [[0, 1, 2, 3, 4],
             [1, 0, 1, 2, 3],
             [2, 1, 0, 1, 2],
             [3, 2, 1, 0, 1],
             [4, 3, 2, 1, 0]]  # Example distances matrix
q = [2, 2]  # Capacity of each bus

total_distance, transport_plan = solve_optimal_transport(N, K, distances, q)
print('Total distance:', total_distance)
print('Transport plan:', transport_plan)
print("filtered:", [k for k, v in transport_plan.items() if v == 1])
