from docplex.mp.model import Model
import numpy


def solve_optimal_transport(N, K, distances, q):
    model = Model('optimal_transport')

    # Variables
    x = {(i, j, k): model.binary_var(name='x_{0}_{1}_{2}'.format(i, j, k))
         for i in range(2 * N + 1) for j in range(2 * N + 1) for k in range(K)}

    # New variables to track passenger count in each bus
    khach_tren_xe = [[] for _ in range(K)]
    for k in range(K):
        sub = []
        khach_tren_xe.append(sub)

        so_khach_tren_xe = []

        for i, sublist in enumerate(khach_tren_xe, start=0):
            khach_tren_xe[i] = sublist
            so_khach_tren_xe.append(len(khach_tren_xe[i]))

    diem_don_khach = []
    for i in range(1, N+1):
        diem_don_khach.append(i)

    # Objective function
    model.minimize(model.sum(distances[i][j] * x[i, j, k] for i in range(2 * N + 1)
                             for j in range(2 * N + 1) for k in range(K)))

    # Constraints
    # Ensure each point is visited exactly once
    for point in range(1, 2 * N + 1):
        # Mỗi điểm chỉ đi ra và đi vào một lần
        # Constraints
        # Ensure each point is visited exactly once
        for point in range(1, 2 * N + 1):
            model.add_constraint(model.sum_vars(x[i, point, k] for i in range(
                2 * N + 1) if i != point for k in range(K)) == 1)
            model.add_constraint(model.sum_vars(x[point, j, k] for j in range(
                2 * N + 1) if j != point for k in range(K)) == 1)

    for k in range(K):
        # Mỗi chuyến bắt đầu từ bến
        model.add_constraint(model.sum_vars(
            x[0, i, k] for i in range(1, N + 1)) == 1)
        # Mỗi chuyến kết thúc ở bến
        model.add_constraint(model.sum_vars(
            x[i, 0, k] for i in range(N+2, 2*N+1)) == 1)

        # Điều kiện số lượng khách trên xe
        model.add_constraint(so_khach_tren_xe[k] <= q[k])

        # Cập nhật danh sách hành khách trên xe khi đón trả khách
        for i in range(2 * N + 1):
            for j in range(N+1):
                for k in range(K):
                    khach_tren_xe[k].append(j)

        for i in range(2 * N + 1):
            for j in range(N+2, 2*N+1):
                for k in range(K):
                    khach_tren_xe[k].remove(j-N)

        if so_khach_tren_xe[k] == q[k] or diem_don_khach == []:
            i = max(khach_tren_xe[k])
            j = min(khach_tren_xe[k])
            model.add_constraint(x[i, j, k] == 1)

    # Solve the model
    model.solve()

    # Get the solution
    if model.solution:
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
N = 2  # Number of passengers
K = 2  # Number of buses
distances = [[0, 1, 2, 3, 4],
             [1, 0, 1, 2, 3],
             [2, 1, 0, 1, 2],
             [3, 2, 1, 0, 1],
             [4, 3, 2, 1, 0]]  # Example distances matrix
q = [2, 2]  # Capacity of each bus

total_distance, transport_plan = solve_optimal_transport(N, K, distances, q)
print('Total distance:', total_distance)
print('Transport plan:', transport_plan)
print_transport_result(N, K, transport_plan)
