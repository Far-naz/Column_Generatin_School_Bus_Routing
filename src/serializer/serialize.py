from module.stop import Stop
import pandas as pd


def read_all_stops():
    stops_2 = [
        Stop(Id=1, is_depot=True, is_student=False, lat=5, lon=7),
        Stop(Id=2, is_student=True, lat=3, lon=7),
        Stop(Id=3, is_student=True, lat=2, lon=8),
        Stop(Id=4, is_student=True, lat=7, lon=11),
        Stop(Id=5, is_student=True, lat=8, lon=10),
        Stop(Id=6, is_student=True, lat=10, lon=12),
        Stop(Id=7, is_student=True, lat=8, lon=17),
        Stop(Id=8, is_student=True, lat=15, lon=10),
        Stop(Id=9, is_student=False, lat=2, lon=12),
        Stop(Id=10, is_student=False, lat=4, lon=16),
        Stop(Id=11, is_student=False, lat=7, lon=13),
        Stop(Id=12, is_student=False, lat=11, lon=13),
        Stop(Id=13, is_student=False, lat=12, lon=7),
        Stop(Id=14, is_student=False, lat=14, lon=10),
        Stop(Id=15, is_depot=True, is_student=False, lat=5, lon=7),
    ]
    stops2 = [
        Stop(Id=1, is_depot=True, is_student=False, lat=1, lon=4),
        Stop(Id=2, is_depot=False, is_student=True, lat=3, lon=7),
        Stop(Id=3, is_depot=False, is_student=True, lat=5, lon=2),
        Stop(Id=4, is_depot=False, is_student=False, lat=7, lon=6),
        Stop(Id=5, is_depot=False, is_student=True, lat=8, lon=7),
        Stop(Id=6, is_depot=False, is_student=True, lat=7, lon=9),
        Stop(Id=7, is_depot=False, is_student=False, lat=11, lon=4),
        Stop(Id=8, is_depot=False, is_student=True, lat=12, lon=5),
        Stop(Id=9, is_depot=False, is_student=True, lat=14, lon=4),
        Stop(Id=10, is_depot=False, is_student=True, lat=9, lon=7),
        Stop(Id=11, is_depot=False, is_student=True, lat=8, lon=8),
        Stop(Id=12, is_depot=True, is_student=False, lat=1, lon=4),
    ]
    stops = [
        Stop(Id=0, is_depot=True, is_student=False, lon=8, lat=8),
        Stop(Id=1, is_depot=False, is_student=True, lon=11, lat=2.5),
        Stop(Id=2, is_depot=False, is_student=True, lon=5, lat=0),
        Stop(Id=3, is_depot=False, is_student=True, lon=2.5, lat=7),
        Stop(Id=4, is_depot=False, is_student=True, lon=3, lat=8),
        Stop(Id=5, is_depot=False, is_student=True, lon=3.5, lat=8.5),
        Stop(Id=6, is_depot=False, is_student=False, lon=10, lat=2),
        Stop(Id=7, is_depot=False, is_student=False, lon=9, lat=2.5),
        Stop(Id=8, is_depot=False, is_student=False, lon=5.5, lat=1),
        Stop(Id=9, is_depot=False, is_student=False, lon=4, lat=0),
        Stop(Id=10, is_depot=False, is_student=False, lon=2, lat=6),
        Stop(Id=11, is_depot=False, is_student=False, lon=2, lat=7),
        Stop(Id=12, is_depot=False, is_student=False, lon=2, lat=9),
        Stop(Id=13, is_depot=False, is_student=False, lon=4, lat=9),
    ]
    return stops


def read_bus_stops(data_file: str, lst_index: int) -> list[Stop]:
    stops = []
    # csv file with header: StopId,StopAbbr,StopName,Lat,Lon
    df = pd.read_csv(data_file)
    idx = lst_index + 1
    for _, row in df.iterrows():
        stop_id = idx
        idx += 1
        name = row["StopId"]
        lat = float(row["Lat"]) / 1e6
        lon = float(row["Lon"]) / 1e6
        stop = Stop(Id=stop_id, is_depot=False, is_student=False, lat=lat, lon=lon, name=name)
        stops.append(stop)

    return stops


def get_schools(data_file: str, school_id: int ) -> list[Stop]:
    schools = []
    # csv file with header: LocId,LocName,Lon,Lat,OnStreet,City,ZipCode
    df = pd.read_csv(data_file)
    if school_id is not None:
        df = df[df["LocId"] == school_id]
    for _, row in df.iterrows():
        school_id = 0
        name = row["LocId"]
        lat = float(row["Lat"]) / 1e6
        lon = float(row["Lon"]) / 1e6
        school = Stop(
            Id=school_id, is_depot=True, is_student=False, lat=lat, lon=lon, name=name
        )
        schools.append(school)

    return schools


def read_students_locations(data_file: str, school_id: int) -> list[Stop]:
    students = []
    # csv file with header ClientId,AddrId,SubscriptionTemplateId,LocName,schooltype,LocId,schoollat,schoollon,FromAddrType,ToAddrType,adresslat,adresslon,grade,requestedtimeinbound,requestedtimeoutbound
    df = pd.read_csv(data_file)
    df_school = df[df["LocId"] == school_id]
    idx = 1
    for _, row in df_school.iterrows():
        student_id = idx
        name = row["ClientId"]
        lat = float(row["adresslat"]) / 1e6
        lon = float(row["adresslon"]) / 1e6
        student = Stop(
            Id=student_id, is_depot=False, is_student=True, lat=lat, lon=lon, name=name
        )
        students.append(student)
        idx += 1

    return students
