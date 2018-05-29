import networkx as nx
import math

import json


def haversine(origin, destination):
    # https://gist.github.com/rochacbruno/2883505
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d


class Stop(object):
    def __init__(self, start, end, age, id=0):
        self.start = start
        self.end = end
        self.age = age
        self.id = id


class Graph(object):
    def __init__(self):
        self.G = nx.Graph()
        self.coords_to_id = {}

    def add_node(self, node_coordinates):
        if node_coordinates not in self.coords_to_id:
            self.coords_to_id[node_coordinates] = len(self.coords_to_id) + 1
        self.G.add_node(self.coords_to_id[node_coordinates],
                        coord=node_coordinates)

    def add_edge(self, source_coordinates, destination_coordinates):
        if source_coordinates not in self.coords_to_id:
            raise ValueError(
                'The source node has not been added to the graph yet.'
            )

        if destination_coordinates not in self.coords_to_id:
            raise ValueError(
                'The destination node has not been added to the graph yet.'
            )

        source_id = self.coords_to_id[source_coordinates]
        destination_id = self.coords_to_id[destination_coordinates]
        dist = haversine(source_coordinates, destination_coordinates)
        self.G.add_edge(source_id, destination_id, weight=dist)

    def get_paths(self, source_coordinates, destination_coordinates):
        if source_coordinates not in self.coords_to_id:
            raise ValueError(
                'The source node has not been added to the graph yet.'
            )

        if destination_coordinates not in self.coords_to_id:
            raise ValueError(
                'The destination node has not been added to the graph yet.'
            )

        source_id = self.coords_to_id[source_coordinates]
        destination_id = self.coords_to_id[destination_coordinates]


def cost(start, end, path, max_dist):
    if len(path) > 0:
        total_age = sum(x.age for x in set(path))
        visited_stops = {path[0]}
        dist = haversine(start, path[0].start)
        for i in range(1, len(path) - 1):
            if path[i] in visited_stops:
                source = path[i].end
            else:
                source = path[i].start
                visited_stops.add(path[i])

            if path[i + 1] in visited_stops:
                dest = path[i + 1].end
            else:
                dest = path[i + 1].start

            dist += haversine(source, dest)

        dist += haversine(path[-1].end, end)
        if dist > max_dist:
            return (0, total_age, dist)
        else:
            return (len(path), total_age, dist)
    else:
        return (0, 0, float('inf'))


def filter_path(path):
    visited_stops = set()
    filtered_path = []
    for stop in path:
        if stop in visited_stops:
            filtered_path.append(stop.end)
        else:
            filtered_path.append(stop.start)
            visited_stops.add(stop)
    return filtered_path


def brute_force(start, end, stops, max_dist):
    best_path = []
    best_dist = haversine(start, end)
    for d in range(5):
        for stop in stops:
            if stop not in best_path:
                if d == 0:
                    temp_path = [stop, stop]
                    length, age, dist = cost(start, end, temp_path, max_dist)
                    if length > len(best_path) or (length == len(best_path) and dist < best_dist):
                        best_path = temp_path.copy()
                        best_dist = dist
                        continue

                else:
                    best_start_idx = 0
                    best_end_idx = len(best_path)
                    best_temp_path = best_path
                    best_temp_dist = best_dist

                    for start_idx in range(len(best_path) + 1):
                        temp_path = best_path.copy()
                        temp_path.insert(start_idx, stop)
                        for end_idx in range(start_idx, len(best_path) + 2):
                            temp_path.insert(end_idx, stop)

                            length, age, dist = cost(start, end, temp_path, max_dist)
                            #print([x.id for x in temp_path], dist)
                            if length > len(best_temp_path) or (length == len(best_temp_path) and dist < best_temp_dist):
                                best_temp_path = temp_path.copy()
                                best_temp_dist = dist

                            del temp_path[end_idx]

                    best_path = best_temp_path
                    best_dist = best_temp_dist

    return best_path

def get_shortest_paths(input_json):
    max_time = max(x['time'] for x in input_json['locations'])

    # Get all data from the JSON input 
    start_node = (input_json['start']['lat'], input_json['start']['lng'])
    end_node = (input_json['end']['lat'], input_json['end']['lng'])
    stops = []
    for stop_id, loc in enumerate(input_json['locations']):
        stops.append(
            Stop(
                (loc['coordinate'][0]['lat'], loc['coordinate'][0]['lng']),
                (loc['coordinate'][1]['lat'], loc['coordinate'][1]['lng']),
                max_time - loc['time'],
                id=stop_id
            )
        )

    network = Graph()

    # Get the maximum time in order to calculate the age of a package 

    # Add nodes to our graph
    network.add_node(start_node)
    network.add_node(end_node)
    for stop in stops:
        network.add_node((stop.start[0], stop.start[1]))
        network.add_node((stop.end[0], stop.end[1]))

    # Add all edges
    network.add_edge(start_node, end_node)
    for stop in stops:
        network.add_edge(start_node, (stop.start[0], stop.start[1]))
        network.add_edge(start_node, (stop.end[0], stop.end[1]))
        network.add_edge(end_node, (stop.start[0], stop.start[1]))
        network.add_edge(end_node, (stop.end[0], stop.end[1]))
        for stop2 in stops:
            if stop != stop2:
                network.add_edge((stop.start[0], stop.start[1]), (stop2.start[0], stop2.start[1]))
                network.add_edge((stop.start[0], stop.start[1]), (stop2.end[0], stop2.end[1]))
                network.add_edge((stop.end[0], stop.end[1]), (stop2.start[0], stop2.start[1]))
                network.add_edge((stop.end[0], stop.end[1]), (stop2.end[0], stop2.end[1]))

    kappa = input_json['kappa']
    max_dist = (1 + kappa) * haversine(start_node, end_node)

    print(start_node, end_node, stops)
    print(max_dist)

    best_path = filter_path(brute_force(start_node, end_node, stops, max_dist))
    return json.dumps([start_node] + [x for x in best_path] + [end_node])

"""
{'locations': [{'coordinate': [{'lat': 51.108803291433134, 'lng': 3.275556564331055}, {'lat': 51.13099991299968, 'lng': 3.317785263061524}], 'time': 0}, {'coordinate': [{'lat': 51.1335852335762, 'lng': 3.32636833190918}, {'lat': 51.11257531414125, 'lng': 3.2719516754150395}], 'time': 1}, {'coordinate': [{'lat': 51.11117431307491, 'lng': 3.2841396331787114}, {'lat': 51.1347701238018, 'lng': 3.3298015594482426}], 'time': 10}], 'start': {'lat': 51.104956, 'lng': 3.26724}, 'end': {'lat': 51.13886314700496, 'lng': 3.335552215576172}, 'kappa': 0.5}

--> Geeft vreemde oplossing
"""