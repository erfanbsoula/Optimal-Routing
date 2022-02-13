import json
import numpy as np
import pulp as lp

node_count = 10
nodes = range(0, node_count)

edges = np.zeros((node_count, node_count))
weights = np.zeros((node_count, node_count))

data_file = open("data.json")
data = json.load(data_file)
data_file.close()

for i in nodes:
    itc = 0
    for j in data[i]["neighbors_indices"]:
        edges[i][j] = 1
        weights[i][j] = data[i]["neighbors_weights"][itc]
        itc += 1

def extract_path(start, target, solution):
    path = [data[start]["place_name"] + f"({start})"]
    temp = start
    while True:
        for i in nodes:
            if solution[temp][i] == 1:
                path.append(data[i]["place_name"] + f"({i})")
                temp = i
                break

        if temp == target:
            break

    return path


def calc_rhs(i, start, target):
    if i == start:
        return 1
    if i == target:
        return -1
    return 0

def find_shortest_path(start_point, destination):
    problem = lp.LpProblem("shortest-path", lp.LpMinimize)
    x = lp.LpVariable.dicts("variables", (nodes, nodes), cat='Binary')
    for i in nodes:
        for j in nodes:
            if edges[i][j] == 0:
                problem.addConstraint(
                    lp.LpConstraint(e=x[i][j], sense=lp.LpConstraintEQ, rhs=0)
                )
    for i in nodes:
        rhs = calc_rhs(i, start_point, destination)
        problem.addConstraint(
            lp.LpConstraint(
                e=lp.lpSum([
                    x[i][j] for j in nodes])-lp.lpSum([x[j][i] for j in nodes
                ]),
                sense=lp.LpConstraintEQ, rhs=rhs
            )
        )
    objective = lp.lpSum([x[i][j]*weights[i][j] for i in nodes for j in nodes])
    problem.setObjective(objective)
    problem.solve(lp.PULP_CBC_CMD(msg=0))
    print(f'\nSolution Status = {lp.LpStatus[problem.status]}')
    print(f"Optimal Cost to Go: {int(problem.objective.value())}")

    solution = np.zeros((node_count, node_count))
    for i in nodes:
        for j in nodes:
            solution[i][j] = lp.value(x[i][j])
    return extract_path(start_point, destination, solution)


def print_node_info(index, description):
    print(description + ":", data[index]["place_name"], end='')
    print(f" (Index = {index} | ", end='')
    print(f"Latitude = {data[index]['Latitude']} ", end='')
    print(f"| Longitude = {data[index]['Longitude']})")

while True:
    console = input("$ ")
    args = console.split()

    if console == "--help":
        with open("help.txt") as hf:
            print()
            print(hf.read(), '\n')

    elif console == "exit":
        break

    elif args[0] == "direction":
        start_point = int(args[1])
        destination = int(args[2])
        print()
        print_node_info(start_point, "Start-Point")
        print_node_info(destination, "Destination")
        path = find_shortest_path(start_point, destination)
        print(path[0], end='')
        for i in range(1, len(path)):
            print(" ->", path[i], end='')
        print("\n")

    else:
        print("command not recognized! (type '--help' for help)\n")