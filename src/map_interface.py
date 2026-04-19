from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
import webbrowser

import folium

from module.input_model import DataSource, InputModel
from module.stop_point import STOP_TYPE, Stop, Student


DEFAULT_SCHOOL_ID = 33337
DEFAULT_NUMBER_OF_VEHICLES = 2
DEFAULT_CAPACITY_OF_VEHICLE = 2
DEFAULT_MAX_TRAVEL_DISTANCE = 2.0
DEFAULT_ALLOWED_WALKING_DISTANCE = 0.5


def _build_model(allowed_walking_distance: float, school_id: int = DEFAULT_SCHOOL_ID) -> InputModel:
    return InputModel(
        DEFAULT_NUMBER_OF_VEHICLES,
        DEFAULT_CAPACITY_OF_VEHICLE,
        DEFAULT_MAX_TRAVEL_DISTANCE,
        allowed_walking_distance,
        school_id,
        DataSource.REAL,
    )


def _is_original_student(stop: Stop) -> bool:
    return stop.stop_type == STOP_TYPE.STUDENT and stop.second_id == stop.id


def _unique_points(stops: list[Stop]) -> list[Stop]:
    unique: OrderedDict[tuple[float, float, int], Stop] = OrderedDict()
    for stop in stops:
        key = (round(stop.lat, 7), round(stop.lon, 7), stop.stop_type.value)
        if key not in unique:
            unique[key] = stop
    return list(unique.values())


def _collect_visible_stops(students: list[Student]) -> list[Stop]:
    visible: list[Stop] = []
    for student in students:
        visible.extend(student.covering_stops)
    return _unique_points(visible)


def _walking_radius_meters(model: InputModel) -> float:
    # Real-data setup uses haversine distance in kilometers.
    if model.distance_metric.value == "harvesian":
        return model.allowed_walking_dist * 1000.0
    return 0.0


def build_map(model: InputModel) -> folium.Map:
    school = model.school
    students = [student for student in model.students if _is_original_student(student)]
    visible_stops = [stop for stop in _collect_visible_stops(model.students) if not _is_original_student(stop) and stop.stop_type != STOP_TYPE.SCHOOL]
    center_lat = school.lat
    center_lon = school.lon

    if students:
        center_lat = sum(student.lat for student in students) / len(students)
        center_lon = sum(student.lon for student in students) / len(students)

    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=14, control_scale=True)

    folium.Marker(
        location=[school.lat, school.lon],
        tooltip="School",
        popup=f"School ID: {school.id}",
        icon=folium.Icon(color="black", icon="glyphicon-education"),
    ).add_to(fmap)

    walking_radius_m = _walking_radius_meters(model)

    for student in students:
        folium.CircleMarker(
            location=[student.lat, student.lon],
            radius=4,
            color="#7f1d1d",
            fill=True,
            fill_color="#d94f30",
            fill_opacity=0.9,
            tooltip=f"Student {student.id}",
            popup=f"Student ID: {student.id}",
        ).add_to(fmap)

        if walking_radius_m > 0:
            folium.Circle(
                location=[student.lat, student.lon],
                radius=walking_radius_m,
                color="#d94f30",
                weight=1,
                fill=True,
                fill_opacity=0.08,
                popup=f"Allowed walking distance: {model.allowed_walking_dist:.2f} km",
            ).add_to(fmap)

    for stop in visible_stops:
        folium.CircleMarker(
            location=[stop.lat, stop.lon],
            radius=3,
            color="#12467a",
            fill=True,
            fill_color="#1f77b4",
            fill_opacity=0.85,
            tooltip=f"Stop {stop.id}",
            popup=f"Stop ID: {stop.id}",
        ).add_to(fmap)

    title_html = (
        f"<h4 style='position: fixed; top: 10px; left: 50px; z-index: 9999;'>"
        f"School and reachable stops | allowed walking distance = {model.allowed_walking_dist:.2f}"
        f"</h4>"
    )
    fmap.get_root().add_child(folium.Element(title_html))

    return fmap


def launch_map_interface(
    school_id: int = DEFAULT_SCHOOL_ID,
    initial_allowed_walking_distance: float = DEFAULT_ALLOWED_WALKING_DISTANCE,
    output_file: str = "map_interface.html",
    open_browser: bool = True,
) -> Path:
    model = _build_model(initial_allowed_walking_distance, school_id=school_id)
    fmap = build_map(model)

    output_path = Path(output_file)
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path
    fmap.save(str(output_path))

    if open_browser:
        webbrowser.open(output_path.resolve().as_uri())

    return output_path


if __name__ == "__main__":
    launch_map_interface()