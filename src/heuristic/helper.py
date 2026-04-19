from module.route import Route
from module.stop_point import Stop, Student
from module.input_model import InputModel
import logging



def find_pickup_point(student: Student, route: Route) -> Stop | None:
    for stop in route.stops:
        Cs = student.covering_stops
        if any(c.second_id == stop.second_id for c in Cs):
            return stop
    return None


def get_students_pickup_points(
    route: Route, problem_model: InputModel
) -> dict[int, int]:
    pickup_points = {}
    for s in problem_model.students:
        stop_point = find_pickup_point(s, route)
        if stop_point is not None:
            pickup_points[s.second_id] = stop_point.second_id
    return pickup_points



def duplicate_students_in_routes(final_routes: list[Route]) -> dict[int, list[int]]:
    """Check that each student is served by at most one route."""
    repeated_stds_in_route = {}
    final_result = {}
    for r, route in enumerate(final_routes):
        for std in route.served_students:
            if std not in repeated_stds_in_route:
                repeated_stds_in_route[std] = [r]
            else:
                repeated_stds_in_route[std].append(r)

    for std, routes in repeated_stds_in_route.items():
        if len(routes) > 1:
            final_result[std] = routes
    return final_result


def remove_student(
    student: Student,
    route: Route,
    problem_model: InputModel,
) -> Route|None:
    if student.second_id not in route.served_students:
        print(f"Route does not serve student {student.second_id}. Cannot remove.")
        return None

    selected_stop = find_pickup_point(student, route)
    if selected_stop is not None:
        selected_stop_to_remove = selected_stop

    remove_index = route.stops.index(selected_stop_to_remove)

    if remove_index == 0 or remove_index == len(route.stops) - 1:
        print("Cannot remove depot stops.")
        return None

    new_distance = (
        route.total_distance
        - problem_model.distance_matrix[
            (
                route.stops[remove_index - 1].second_id,
                selected_stop_to_remove.second_id,
            )
        ]
        - problem_model.distance_matrix[
            (
                selected_stop_to_remove.second_id,
                route.stops[remove_index + 1].second_id,
            )
        ]
        + problem_model.distance_matrix[
            (
                route.stops[remove_index - 1].second_id,
                route.stops[remove_index + 1].second_id,
            )
        ]
    )

    new_walking_distance = (
        route.total_walking_distance
        - problem_model.walking_distance_list[selected_stop_to_remove.second_id]
    )

    new_route_stops: list[Stop] = route.stops.copy()
    new_route_stops.pop(remove_index)

    cover_students = route.served_students.copy()
    cover_students.remove(student.second_id)

    route.stops = new_route_stops
    route.total_distance = new_distance
    route.total_walking_distance = new_walking_distance
    route.served_students = cover_students

    return route


def drop_duplicate_students(
    final_routes: list[Route],
    problem_model: InputModel,
    logger: logging.Logger,
) -> list[Route]:
    """Drop students that are served by multiple routes from the most expensive route."""
    repeated_stds_in_route = duplicate_students_in_routes(final_routes)
    if not repeated_stds_in_route:
        logger.info("No duplicate students found in routes.")
        return final_routes
    else:
        logger.info(
            f"Duplicate students found in routes: {repeated_stds_in_route}. Removing duplicates from the most expensive route."
        )
    for std, routes in repeated_stds_in_route.items():
        if len(routes) > 1:
            logger.info(f"Student {std} is served by multiple routes: {routes}")
            route_distances = [final_routes[r].total_distance for r in routes]
            min_distance = min(route_distances)
            for r in routes:
                if final_routes[r].total_distance > min_distance:
                    logger.info(
                        f"Removing student {std} from route {r} with distance {final_routes[r].total_distance}"
                    )
                    r_std = next(s for s in problem_model.students if s.second_id == std)
                    new_route = remove_student(
                        r_std,
                        final_routes[r],
                        problem_model,
                    )
                    if new_route is not None:
                        final_routes[r] = new_route
    return final_routes
