import json

from docplex.mp.model import Model

def solve(N, K, d):
    model = Model()

    x = model.binary_var_cube(N + 2, N + 2, K, name = 'x_name')

    model.get_var_by_name('x_name')

    # Constraint: Each point is visited by exactly one vehicle
    for j in range(1, N + 1):
        incoming = model.sum_vars([x[(i, j, k)] for i in range(N + 1) for k in range(K)])
        model.add_constraint(incoming <= 1.1)
        model.add_constraint(incoming >= 0.9)
    
    # Constraint: Each point is gone out by exactly one vehicle
    for i in range(1, N + 1):
        outgoing = model.sum_vars([x[(i, j, k)] for j in range(1, N + 2) for k in range(K)])
        model.add_constraint(outgoing <= 1.1)
        model.add_constraint(outgoing >= 0.9)
    '''
    # Constraint: Vehicle follow continuos trip
    for j in range(1, N + 2):
        for k in range(K):
            checkpoint = model.sum_vars([x[(i, j, k)] for i in range(1, N + 1)])
            nextpoint = model.sum_vars([x[(j, t, k)] for t in range(1, N + 1)])
            if checkpoint >= 0.9:
                model.add_constraint(nextpoint <= 1.1)
                model.add_constraint(nextpoint >= 0.9)
    '''
    # Constraint: Each vehicle starts and ends at point 0
    for k in range(K):
        start = model.sum_vars([x[(0, j, k)] for j in range(1, N + 1)])
        end = model.sum_vars([x[(i, N + 1, k)] for i in range(1, N + 1)])
        model.add_constraint(start == 1)
        model.add_constraint(end == 1)

    # Constraint: Vehicle cannot travel from point i to itself
    for i in range(N + 2):
        itself = model.sum_vars([x[(i, i, k)] for k in range(K)])
        model.add_constraint(itself == 0)

    # Set objective to minimize total distance
    total_distance = model.sum(d[i][j] * x[(i, j, k)] for i in range(N + 2) for j in range(N + 2) for k in range(K))
    model.minimize(total_distance)

    # Solve 
    model.solve()

    # Print optimal solution
    print("Total distance:",model.objective_value)
    for k in range(K):
        print('Vehicle', k+1, ':')
        current_city = 0
        route = [0]
        while current_city != N + 1:
            for i in range(N + 2):
                if x[(current_city, i, k)].solution_value >= 0.9:
                    route.append(i)
                    current_city = i
                    break
        print(', '.join(map(str, route)))

if __name__ == '__main__':
    # Example usage
    N = 3
    K = 2
    d = [
        [0, 10, 20, 30, 0],
        [10, 0, 25, 35, 10],
        [20, 25, 0, 15, 20],
        [30, 35, 15, 0, 30],
        [0, 10, 20, 30, 0]
    ]

    solve(N, K, d)
