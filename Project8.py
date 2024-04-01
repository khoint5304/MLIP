from docplex.mp.model import Model

def xep_lich_thi_hoc_ky(N, M, d, c, trung):
    model = Model('xep_lich_thi_hoc_ky')
    
    # Variables
    x = {(i,j,k): model.binary_var(name='x_{0}_{1}_{2}'.format(i,j,k))
            for i in range(1, N+1) for j in range(1, M+1) for k in range(1, 5)}
    
    # Constraints
    # Each course is assigned to exactly one session
    for i in range(1, N+1):
        model.add_constraint(model.sum(x[i,j,k] for j in range(1, M+1) for k in range(1, 5)) == 1)
        
    # Each session, each room has at most one course
    for k in range(1, 5):
        for j in range(1, M+1):
            model.add_constraint(model.sum(x[i,j,k] for i in range(1, N+1)) <= 1) #type: ignore
    # Conflict courses not take place at the same time
    for mon in trung:
        i,j = mon
        for k in range(1,5):
            model.add_constraint(model.sum(x[i, l, k] for l in range(1, M + 1)) + model.sum(x[j, l, k] for l in range(1, M + 1)) <= 1, ctname=f'conflict_{i}_{j}_{k}') #type: ignore
    # limit students in each room
    for k in range(1,5):
        for j in range(1,M+1):
            model.add_constraint(model.sum(x[i,j,k]*d[i] for i in range(1,N+1)) <= c[j])
    # Objective
    model.minimize(model.sum(x[i, j, k] for i in range(1, N + 1) for j in range(1, M + 1) for k in range(1, 5)))

    # Solve
    model.solve()

    # Print results
    if model.solution:
        print('Exam Schedule:')
        for k in range(1, 5):
            print(f'--- Slot {k} ---')
            for j in range(1, M + 1):
                exams = [i for i in range(1, N + 1) if x[i, j, k].solution_value == 1]
                if exams:
                    print(f'Room {j}: Exams {exams}')
            print()
    else:
        print('No feasible solution found.')

# Example usage
N = 3  # Number of exams
d = {1: 50, 2: 60, 3: 70}  # Number of students for each exam
trung = [(1, 2), (2, 3)]  # Conflicting exam pairs
M = 2  # Number of rooms
c = {1: 100, 2: 120}  # Capacity of each room

xep_lich_thi_hoc_ky(N, M, d, c, trung)