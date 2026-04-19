'''from module.route import Route
from module.stop import Label
from module.input_model import InputModel
from module.stop_point import Stop, STOP_TYPE, Student


class LabelSettingAlgorithmPulling:
    def __init__(
        self, route: Route, model: InputModel, pi: dict[int, float], mu: float, find_new_stop=True
    ):
        self.route = route
        self.max_route_distance: float = model.max_travel_distance
        #self.covering_stops = model.covering_stops
        self.walking_distance: list[float] = model.walking_distance_list
        self.distance: dict[tuple[int, int], float] = model.distance_matrix
        self.pi = pi  # dual values
        self.mu = mu  # vehicle dual
        self.find_new_stop = find_new_stop

    def run(self) -> Route | None:
        try:
            stops: list[Stop] = self.route.stops
            n = len(stops)

            #print covering stops for each stop
            #for s in stops:
            #    print(f"Stop {s.second_idx} covers {[st.second_idx for st in self.covering_stops[s.second_idx]]}")

            # ---------- initialization ----------
            first_stop: Stop = stops[0]
            initial_rc = 0.0
            label = Label(
                route_dist=0.0, walk_dist=initial_rc, stop=first_stop, parent=None
            )
            first_stop.labels = [label]

            # ---------- main DP loop ----------
            for i in range(1, n):
                curr_stop: Stop = stops[i]
                curr_stop_id = curr_stop.std_id if curr_stop.is_student else curr_stop.second_idx
                current_cluster = self.covering_stops[curr_stop_id]

                prev_stop: Stop = stops[i - 1]
                prev_cluster = self.covering_stops[
                    prev_stop.std_id if prev_stop.is_student else prev_stop.second_idx
                ]
                for covered in current_cluster:
                    new_labels: list[Label] = []
                    for prev_stop in prev_cluster:
                        for prev_label in prev_stop.labels:
                            if prev_label.route_dist > self.max_route_distance:
                                continue

                            # ---------- compute reduced cost increment ----------
                            d = self.distance[
                                (prev_label.stop.second_idx, covered.second_idx)
                            ]
                                                
                            new_route_dist = prev_label.route_dist + d
                            new_rc = prev_label.walk_dist + self.walking_distance[covered.second_idx]

                            # feasibility check
                            if new_route_dist <= self.max_route_distance:
                                new_label: Label = Label(
                                    route_dist=new_route_dist,
                                    walk_dist=new_rc,
                                    stop=covered,
                                    parent=prev_label,
                                )
                                new_labels.append(new_label)
                                #print(f"Created new label to stop {covered.second_idx} with route dist {new_route_dist} and reduced cost {new_rc}")

                    # ---------- dominance pruning ----------
                    if new_labels:
                        new_labels.sort(key=lambda l: l.route_dist)
                        covered.labels = [new_labels[0]]
                        last = 0
                        for j in range(1, len(new_labels)):
                            if new_labels[j].walk_dist < new_labels[last].walk_dist:
                                covered.labels.append(new_labels[j])
                                last = j
                    else:
                        covered.labels = []

            # ---------- extract best solution ----------
            final_labels: list[Label] = stops[-1].labels
            if not final_labels:
                raise Exception("No feasible route found")
            
            # check final_labels are feasible
            if self.find_new_stop:
                feasible_labels = [
                    l for l in final_labels if l.route_dist <= self.max_route_distance
                ]
                
                # calculate the reduced cost for each final label
                for label in feasible_labels:
                    served_students = [s.std_id for s in stops if s.is_student]
                    label.cost = label.walk_dist - sum(
                        self.pi[s] for s in served_students
                    ) - self.mu

                # is there any negative reduced cost label?
                negative_labels = [l for l in feasible_labels if l.cost < 0]
                if not negative_labels:
                    raise Exception("No negative reduced cost route found") 
                
                best_label: Label = min(negative_labels, key=lambda l: l.cost)
            else:
                best_label: Label = min(final_labels, key=lambda l: l.walk_dist)
            # sort final labels by reduced cost
            
            
            #if self.find_new_stop:
            #    best_label = min(final_labels, key=lambda l: l.route_dist)
            #else:
            #    best_label = min(final_labels, key=lambda l: l.walk_dist)
            
            # ---------- reconstruct route ----------
            selected_stops = []
            curr = best_label
            while curr:
                selected_stops.append(curr.stop)
                curr = curr.parent
            selected_stops.reverse()

            # ---------- build final Route ----------
            served_students = [s.std_id for s in selected_stops if not s.is_depot]
            # subtract vehicle dual mu
            total_rc = best_label.walk_dist -sum(
                self.pi[s] for s in served_students
            ) - self.mu
            #print(f'sum of pi for served students: {[self.pi[s] for s in served_students]}, served students: {served_students}, mu: {self.mu}')
            print(f"Best label found with route dist {best_label.route_dist} and walking cost {best_label.walk_dist} and cost {total_rc}")

            result = Route(
                stops=selected_stops,
                total_distance=best_label.route_dist,
                cost=total_rc,  # reduced cost
                served_students=served_students,
                total_walking_distance=best_label.walk_dist,
            )
        except Exception as e:
            print(f"Label setting algorithm failed: {e}")
            return None

        return result

    def run_without_duals(self) -> Route:
        stops: list[Stop] = self.route.stops
        n = len(stops)

        # ---------- initialization ----------
        first_stop: Stop = stops[0]
        label = Label(route_dist=0.0, walk_dist=0.0, stop=first_stop, parent=None)
        first_stop.labels = []
        first_stop.labels.append(label)

        # ---------- main DP loop ----------
        for i in range(1, n):
            curr_stop: Stop = stops[i]
            curr_stop_id = curr_stop.std_id if curr_stop.is_student else curr_stop.second_idx
            current_cluster = self.covering_stops[curr_stop_id]

            prev_stop: Stop = stops[i - 1]
            prev_cluster = self.covering_stops[
                prev_stop.std_id if prev_stop.is_student else prev_stop.second_idx
            ]

            for covered in current_cluster:
                new_labels = []
                for prev_stop in prev_cluster:
                    for prev_label in prev_stop.labels:
                        if prev_label.route_dist > self.max_route_distance:
                            break

                        d = self.distance[
                            (prev_label.stop.second_idx, covered.second_idx)
                        ]
                        new_route_dist = prev_label.route_dist + d

                        if new_route_dist <= self.max_route_distance:
                            new_label = Label(
                                route_dist=new_route_dist,
                                walk_dist=prev_label.walk_dist
                                + self.walking_distance[covered.second_idx],
                                stop=covered,
                                parent=prev_label,
                            )
                            new_labels.append(new_label)

                # ---------- dominance pruning ----------
                if new_labels:
                    new_labels.sort(key=lambda l: l.route_dist)
                    covered.labels = [new_labels[0]]

                    last = 0
                    for i in range(1, len(new_labels)):
                        if new_labels[i].walk_dist < new_labels[last].walk_dist:
                            covered.labels.append(new_labels[i])
                            last = i
                else:
                    covered.labels = []

        # ---------- extract best solution ----------
        final_labels = stops[-1].labels
        if not final_labels:
            raise Exception("No feasible route found")

        best_label = min(final_labels, key=lambda l: l.walk_dist)

        # ---------- reconstruct route ----------
        selected_stops = []
        curr = best_label
        while curr:
            selected_stops.append(curr.stop)
            curr = curr.parent

        selected_stops.reverse()

        # ---------- build final Route ----------
        served_students = [s.std_id for s in selected_stops if not s.is_depot]
        cost = (
            best_label.walk_dist
            - sum(self.pi.get(s.std_id, 0) for s in selected_stops if s.is_student)
            - self.mu
        )
        result = Route(
            stops=selected_stops,
            total_distance=best_label.route_dist,
            total_walking_distance=best_label.walk_dist,
            served_students=served_students,
            cost=cost,
        )

        return result'''
