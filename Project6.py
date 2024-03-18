from docplex.mp.model import Model

def solve(N, c, a, f, m, A, C):
    # Create optimization model
    model = Model("profit_maximization")

    # Create variables
    x = {i: model.continuous_var(name=f'x{i}') for i in range(N)}

    # Constraint: limited fund
    model.add_constraint(model.sum(x[i] * c[i] for i in range(N)) <= C, ctname='limited_fund')

    # Constraint: limited space
    model.add_constraint(model.sum(x[i] * a[i] for i in range(N)) <= A, ctname='limited_space')

    # Constraint: produce at least m product
    for i in range(N):
        model.add_constraint(x[i] >= m[i], ctname=f'produce_at_least_{i}')

    # Set objective to maximize profit
    model.maximize(model.sum(x[i] * f[i] for i in range(N)))

    # Solve the problem
    sol = model.solve()

    # Print optimal solution
    print("Profit:", sol.get_objective_value()) #type: ignore
    for i in range(N):
        print(f"Product {i+1}: {sol.get_value(x[i])}") #type: ignore

if __name__ == '__main__':
    # Example usage
    N = 10
    c = [20, 30, 15, 25, 10, 50, 40, 45, 35, 60]
    a = [3, 2, 4, 1, 5, 2, 3, 4, 5, 2]
    f = [40, 35, 50, 45, 60, 55, 65, 70, 75, 80] 
    m = [2, 1, 3, 2, 1, 4, 3, 2, 1, 5]  
    A = 100
    C = 1000

    solve(N, c, a, f, m, A, C)
