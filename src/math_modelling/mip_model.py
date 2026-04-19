from datetime import datetime

from module.input_model import InputModel
from module.sucess_result import ModelSuccess
from module.route import Route

import logging
import gurobipy as gp
from gurobipy import GRB


def main_problem(problem_model: InputModel, logger: logging.Logger):
    K = problem_model.number_of_vehicles
    Q = problem_model.capacity_of_vehicle
    max_route_distance = problem_model.max_travel_distance
    d = problem_model.distance_matrix
    S = problem_model.students
    S_ids = problem_model.all_student_ids
    N_H = problem_model.all_stop_ids[:-1]
    W = problem_model.walking_distance_list

    logger.info(f"number of nodes: {len(N_H)}")

    sp = gp.Model("main_problem")

    x = {}
    for k in range(K):
        for i in N_H:
            for j in N_H:
                if i != j:
                    x[i, j, k] = sp.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}")

    S_depot = [0] + S_ids
    x_hat = {}
    for s1 in S_depot:
        for s2 in S_depot:
            if s1 != s2:
                for k in range(K):
                    x_hat[s1, s2, k] = sp.addVar(
                        vtype=GRB.BINARY, name=f"x_hat_{s1}_{s2}_{k}"
                    )

    u = {}
    for s in S_ids:
        for k in range(K):
            u[s, k] = sp.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=Q - 1)

    z = {}
    for i in N_H:
        for k in range(K):
            z[i, k] = sp.addVar(vtype=GRB.BINARY, name=f"z_{i}_{k}")

    # ---- Constraints ----

    sp.addConstrs(
        gp.quicksum(z[i.second_id, k] for i in s.covering_stops for k in range(K)) == 1
        for s in S
    )

    sp.addConstr(gp.quicksum(z[0, k] for k in range(K)) <= K)

    sp.addConstrs(
        gp.quicksum(x[i, j, k] for j in N_H if j != i) == z[i, k]
        for i in N_H
        for k in range(K)
    )

    for k in range(K):
        for i in N_H:
            if i == 0:
                continue
            sp.addConstr(
                gp.quicksum(x[i, j, k] for j in N_H if j != i)
                == gp.quicksum(x[j, i, k] for j in N_H if j != i)
            )

    sp.addConstrs(gp.quicksum(z[i, k] for i in N_H) <= Q for k in range(K))

    sp.addConstrs(
        gp.quicksum(d[i, j] * x[i, j, k] for i in N_H for j in N_H if i != j)
        <= max_route_distance
        for k in range(K)
    )

    sp.addConstrs(
        x_hat[s1.second_id, s2.second_id, k]
        == gp.quicksum(
            x[i.second_id, j.second_id, k]
            for i in s1.covering_stops
            for j in s2.covering_stops
            if i.second_id != j.second_id
        )
        for s1 in S
        for s2 in S
        if s1 != s2
        for k in range(K)
    )

    # Subtour elimination (MTZ)
    for k in range(K):
        for i in S_ids:
            for j in S_ids:
                if i != j:  # and i != 0 and j != 0:
                    sp.addConstr(
                        u[i, k]
                        - u[j, k]
                        + Q * x_hat[i, j, k]
                        + (Q - 2) * x_hat[j, i, k]
                        <= Q - 1
                    )
    sp.addConstrs(
        u[i, k] >= x_hat[i, 0, k] + (Q - 1) * x_hat[0, i, k]
        for i in S_ids
        # if i != 0
        for k in range(K)
    )

    # Set initial objective
    obj = gp.quicksum(W[i] * z[i, k] for i in N_H for k in range(K))
    sp.setObjective(obj, GRB.MINIMIZE)

    sp.params.TimeLimit = 1800
    sp.params.OutputFlag = 0

    # start timer
    start_time = datetime.now()

    # ---- Solve ----
    sp.optimize()

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    logger.info(f"Main problem solved in {elapsed_time.total_seconds():.2f} seconds")

    if sp.status == GRB.OPTIMAL:
        logger.info(f"Main problem objective : {sp.objVal}")
        final_route = []
        routes = {}
        for k in range(K):
            new_nodes = [0]
            current = 0
            while True:
                found = False
                for j in N_H:
                    if (
                        j != current
                        and x.get((current, j, k)) is not None
                        and x[current, j, k].X > 0.5
                    ):
                        next_node = j
                        found = True
                        break
                if not found or next_node == 0:
                    break
                new_nodes.append(next_node)
                current = next_node
            new_nodes.append(problem_model.last_depot.second_id)  # 0)
            routes[k] = new_nodes

        for k in range(K):
            pickup_stop_students = {}
            for i in N_H:
                if z[i, k].X > 0.5 and i != 0:
                    for s in S:
                        Cs = s.covering_stops
                        if any(c.second_id == i for c in Cs):
                            pickup_stop_students[s] = i
            covered_students = [
                s for s in S if any(z[i.second_id, k].X > 0.5 for i in s.covering_stops)
            ]
            route_cost = sum(W[i] for i in N_H if z[i, k].X > 0.5)
            total_distance = sum(
                d[i, j] * x[i, j, k].X
                for i in N_H
                for j in N_H
                if i != j
                if x[i, j, k].X > 0.5
            )

            logger.info(
                f"New route nodes:{routes[k]} covered_students: {[s.second_id for s in covered_students]}- total walking distance:{route_cost}- total distance:{total_distance}"
            )
            result_route = Route(
                stops=routes[k],
                served_students=[s.second_id for s in covered_students],
                total_distance=total_distance,
                total_walking_distance=route_cost,
            )

            final_route.append(result_route)

            

        return ModelSuccess.SUCCESS, final_route
    else:
        logger.warning(f"Subproblem not optimal or infeasible; status: {sp.status}")
        return ModelSuccess.INFEASIBLE, None
