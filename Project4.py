from docplex.mp.model import Model


def solve_optimal_transport(N, M, Q, d, q):
    model = Model('optimal_transport')

    # Biến
    x = {(i, j): model.binary_var(name='x_{0}_{1}'. format(i, j))
         for i in range(M) for j in range(M)}

    # Giải
    model.minimize(model.sum(d[i][j] * x[i, j]
                   for i in range(M+1) for j in range(M+1)))

    # Chuyến đi luôn đi từ bến và kết thúc ở bến
    model.add_constraint(model.sum_vars(x[0, j] for j in range(M + 1)) == 1)
    model.add_constraint(model.sum_vars(x[i, 0] for i in range(M + 1)) == 1)

    # không có chuyến đi nào xuất phát và kết thúc ở cùng 1 điểm
    model.add_constraint(model.sum_vars(x[i, i] for i in range(M)) == 0)

    # mỗi điểm đi qua 1 lần
    model.add_constraint(model.sum_vars(
        x[i, j] + x[j, k] for i in range(M + 1)for j in range(M + 1)for k in range(M + 1)) == 2)

    # tổng số lượng hàng lấy ở các điểm chứa hàng sẽ lớn hơn số hàng yêu cầu lấy
    model.add_constraint(model.sum_vars(
        Q[j] * x[i, j] for i in range(M) for j in range(M)) <= q[k] for k in range(N))

    # giải kết quả
    model.solve()

    if model.solution is not None:
        print("Total distance:", model.objective_value)


# Example data
N = 3  # Number of product types
M = 4  # Number of shelves
# Quantity of products on each shelf
Q = [[1, 2, 3, 0], [2, 1, 0, 3], [0, 3, 2, 1]]
d = [[0, 1, 2, 3], [1, 0, 1, 2], [2, 1, 0, 1],
     [3, 2, 1, 0]]  # Distance between shelves
q = [2, 2, 1]  # Quantity of each product to pick

solve_optimal_transport(N, M, Q, d, q)
