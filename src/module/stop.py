from dataclasses import dataclass
from typing import Optional

class Label:
    def __init__(self, route_dist, walk_dist, stop, parent=None, cost=0.0):
        self.route_dist = route_dist
        self.walk_dist = walk_dist
        self.stop = stop
        self.parent = parent  
        self.cost = cost

@dataclass
class Stop:
    id: int
    second_idx: int = -1
    is_depot: bool = False
    is_student: bool = False
    lat: float = 0.0
    lon: float = 0.0
    is_covered: bool = False
    std_id: Optional[int] = None
    name : Optional[str] = None
    labels: Optional[list[Label]] = None

    # constructor
    def __init__(self, Id, is_depot=False, is_student=False, lat=0.0, lon=0.0, second_idx=-1, is_covered=False, name=None, std_id = None):
        self.id = Id
        self.is_depot = is_depot
        self.is_student = is_student
        self.lat = lat
        self.lon = lon
        self.second_idx = second_idx
        self.is_covered = is_covered
        self.name = name
        self.std_id = std_id

    def copy(self):
        return Stop(
            Id=self.id,
            is_depot=self.is_depot,
            is_student=self.is_student,
            lat=self.lat,
            lon=self.lon,
            second_idx=self.second_idx,
            is_covered=self.is_covered,
            name=self.name,
            std_id=self.std_id
        )
    
    def get_student_id(self):
        if self.is_student and self.is_covered == False:
            return self.second_idx
        else:
            return self.std_id
    


        

