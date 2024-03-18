from docplex.mp.model import Model


# Example data
N = 3  # Number of product types
M = 4  # Number of shelves
# Quantity of products on each shelf
Q = [[0, 1, 2, 3, 0], [0, 2, 1, 0, 3], [0, 0, 3, 2, 1]]
d = [[0, 1, 2, 3, 4], [1, 0, 1, 2, 3], [2, 1, 0, 1, 2],
     [3, 2, 1, 0, 1], [4, 3, 2, 1, 0]]  # Distance between shelves
q = [2, 2, 1]  # Quantity of each product to pick


def solve_optimal_transport():
    model = Model('optimal_transport')

    # Biến
    x = {(i, j): model.binary_var(name='x_{0}_{1}'. format(i, j)) for i in range(M + 1) for j in range(M + 1)}

    # Giải
    model.minimize(model.sum(d[i][j] * x[i, j] for i in range(M + 1) for j in range(M + 1)))

    # Chuyến đi luôn đi từ bến và kết thúc ở bến
    model.add_constraint(model.sum_vars(x[0, j] for j in range(1, M + 1)) == 1)
    model.add_constraint(model.sum_vars(x[i, 0] for i in range(1, M + 1)) == 1)

    # không có chuyến đi nào xuất phát và kết thúc ở cùng 1 điểm
    model.add_constraint(model.sum_vars(x[i, i] for i in range(M + 1)) == 0)

    for i in range(M + 1):
        model.add_constraint(model.sum(x[i, j] for j in range(M + 1)) == 1)
    
    for j in range(M + 1):
        model.add_constraint(model.sum(x[i, j] for i in range(M + 1)) == 1)
    

    #không xoay vòng n điểm
    for i in range(M + 1):
        for j in range(M + 1):
            model.add_constraint((x[j, i] + x[i, j] ) <= 1)    # type: ignore

    # tổng số lượng hàng lấy ở các điểm chứa hàng sẽ lớn hơn số hàng yêu cầu lấy
    for k in range(N):
        model.add_constraint(model.sum(Q[k][j] * x[i, j] for i in range(M + 1) for j in range(M + 1)) >= q[k])  # type: ignore

    # giải kết quả
    model.solve()

    if model.solution is not None:
        print("Total distance:", model.objective_value)

    for i in range(M + 1):
        for j in range(M + 1):
            print(int(x[i, j].solution_value), end=" ")
        
        print()


solve_optimal_transport()
