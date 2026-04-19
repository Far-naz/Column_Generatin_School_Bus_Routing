from module.input_model import InputModel, DataSource
from helper.logger_setup import setup_logger
from math_modelling.mip_model import main_problem
from module.sucess_result import ModelSuccess
from branch_and_price.column_generation import main_column_generation
from module.route import Route
from branch_and_price.models import create_initial_route, solve_final_model
from heuristic.helper import drop_duplicate_students

import logging
from datetime import datetime


def main() -> None:
    mip_model = False
    problem_model = InputModel(
        number_of_vehicles=2,
        capacity_of_vehicle=10,
        max_travel_distance=41.0,
        data_source=DataSource.REAL,
        allowed_walking_distance=0.5,
        school_id=42539,
    )
    model_info = (
        f"[S={len(problem_model.students)}"
        f",B={problem_model.number_of_vehicles}"
        f",Cap={problem_model.capacity_of_vehicle}"
        f",D={problem_model.max_travel_distance}"
        f",W={problem_model.allowed_walking_dist}]"
    )

    print(f"total number of stops: {len(problem_model.all_stops)}")

    if mip_model:
        logger = setup_logger(f"milp_model_{model_info}")

        result, route = main_problem(problem_model, logger)
        if result == ModelSuccess.SUCCESS:
            print(
                f'total route distance: {sum(r.total_distance for r in route) if route else "N/A"}'
            )
            print(
                f'total walking distance: {sum(r.total_walking_distance for r in route) if route else "N/A"}'
            )
        else:
            print("Model did not find a successful solution.")
    else:
        logger: logging.Logger = setup_logger(f"column_generation_{model_info}")

        logger.info(f"Model info: {model_info}")
        logger.info(
            f"Number of stops in the problem model: {len(problem_model.all_stops)}"
        )

        start_time = datetime.now()
        initial_route: Route = create_initial_route(
            problem_model.students, problem_model.distance_matrix, problem_model
        )
        initial_routes = [initial_route]
        logger.info(
            f"Initial routes: {[f'Route {i}: {[s.second_id for s in r.stops]}' for i, r in enumerate(initial_routes)]}"
        )

        routes = main_column_generation(problem_model, initial_routes, logger)
        # ------------------------------
        # FINAL RMP SOLVE (LP)  Heuristic Solution
        logger.info("--- Final RMP Solve ---")
        final_routes = solve_final_model(routes, problem_model, logger)

        end_time = datetime.now()
        logger.info(f"Total time taken: {end_time - start_time}")

        if final_routes is not None:
            polished_routes = drop_duplicate_students(
                final_routes, problem_model, logger
            )
            logger.info("Final routes:")
            for r, route in enumerate(polished_routes):
                logger.info(
                    f"Route {r}: {[s.second_id for s in route.stops]}- Distance: {route.total_distance}, Served students: {route.served_students}, walking distance: {route.total_walking_distance}"
                )
            logger.info(
                f'total route distance: {sum(r.total_distance for r in polished_routes) if polished_routes else "N/A"}, total walking distance: {sum(r.total_walking_distance for r in polished_routes) if polished_routes else "N/A"}'
            )


if __name__ == "__main__":
    main()


# 25: 42539, 75: 33231, 89: 42373, 120: 33243,10: 33337
