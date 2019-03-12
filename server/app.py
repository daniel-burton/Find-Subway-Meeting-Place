from flask import Flask, jsonify
import json
from fuzzywuzzy import process, fuzz
from urllib import parse

app = Flask(__name__)

with open('../graph/station_names.json', 'r') as names_file:
    station_names = json.load(names_file)
    all_names = list(station_names.keys())

with open('../graph/costs.json', 'r') as costs_file:
    weekday_edges = json.load(costs_file)

with open('../graph/graph_network.json', 'r') as network_file:
    node_children = json.load(network_file)

with open('../graph/stations.json', 'r') as station_file:
    stations = json.load(station_file)


def get_full_name(station_number):
    return stations[station_number[:3]]['full_name']

def get_name(station_number):
    return stations[station_number[:3]]['name']

def get_line(name):
    return name.split('#')[1]

def get_line_name(station):
    station = get_line(station)
    if station =='GS':
        return 'GC_Shuttle'
    elif station == 'FS':
        return 'FA_Shuttle'
    elif station == 'AR' or station == 'AL':
       return 'A'
    elif station == 'H':
       return 'R_Shuttle'
    else:
        return station

infinity = float('inf')

def dijkstra(start):
    def make_costs(start):
        costs = {}
        for item in node_children:
            costs[item] = infinity
        for neighbor in node_children[start]:
            if get_name(neighbor) == get_name(start):
                costs[neighbor] = 1
            else:
                costs[neighbor] = weekday_edges[start][neighbor]
        return costs
    
    def make_parents(start):
        parents = {}
        for item in node_children:
            parents[item] = None
        for neighbor in node_children[start]:
            parents[neighbor] = start
        return parents

    def find_lowest_cost_node(costs):
        lowest_cost = float('inf')
        lowest_cost_node = None
        for node in costs:
            cost = costs[node]
            if cost < lowest_cost and node not in processed:
                lowest_cost = cost
                lowest_cost_node = node
        return lowest_cost_node

    processed = []
    parents = make_parents(start)
    costs = make_costs(start)
    node = find_lowest_cost_node(costs)
    while node is not None:
        cost = costs[node]
        neighbors = weekday_edges[node]
        for n in neighbors:
            new_cost = cost + neighbors[n]
            if costs[n] > new_cost:
                costs[n] = new_cost
                parents[n] = node
        processed.append(node)
        node = find_lowest_cost_node(costs)
    return [parents, costs]

def find_station(name, do_fuzz=False):
    name = parse.unquote_plus(name)
    if do_fuzz == False:
        return station_names[name][0]
    else:
        options = process.extract(name, all_names)
        score = 0
        pick = ''
        for i in options:
            option, _ = i
            current = fuzz.ratio(name, option)
            if current > score:
                score = current
                pick = option
        return station_names[pick][0]

def parse_results(parents, costs, started, ended):
    trip = []
    now = ended
    previous = ' # '
    while now != started:
        trip.append(now)
        now = parents[now]
    trip.append(now)

    trip_dets = []

    previous = ' # '
    for stop in trip[::-1]:
        new_line = get_line(stop)
        if previous == ' # ':
            transfer = 2
        elif new_line == previous:
            transfer = 0
        else:
            transfer = 1
        full = {'line':get_line(stop), 'name':get_name(stop), 'transfer':transfer}
        trip_dets.append(full)
        previous = new_line
    return trip_dets

def simplify_costs(costs):
    new = {}
    for stop, cost in costs.items():
        cost = cost//60
        full = get_full_name(stop)
        if full not in new:
            new[full] = cost
        elif cost < new[full]:
            new[full] = cost
    return new

def find_meeting_place(cos1, cos2):
    def recur_try(blur):
        for stop, time in cos1.items():
            if time + blur > cos2[stop] > time - blur:
                potential.append((time, stop))
        # for i in potential:
        #     print(i)
        return potential
    cos1 = simplify_costs(cos1)
    cos2 = simplify_costs(cos2)
    blur_factor = 1
    potential = []
    while len(potential) < 1:
        potential = recur_try(blur_factor)
        blur_factor += 1
    return potential

def print_results(trip):
    previous = ' # '
    for stop in trip:
        if get_line(stop) != get_line(previous):
            print("Transfer to...")
        else:
            print('Next stop:')
            print('\t', get_name(stop) + " " + stop.split("#")[1])
        previous = stop 

@app.route('/api/route/<string:do_fuzz>/<string:start>/<string:end>/', methods=['GET'])
def return_route(start, end, do_fuzz):
    do_fuzz = bool(do_fuzz)
    start = find_station(start, do_fuzz)
    end = find_station(end, do_fuzz)
    par, cos = dijkstra(start)
    route = parse_results(par, cos, start, end)
    time = cos[end] // 60
    return jsonify({'time':time, 'route':route, 'start':get_name(start), 'end':get_name(end)})

@app.route('/api/meeting/<string:do_fuzz>/<string:start1>/<string:start2>/', methods=['Get'])
def return_meeting_place(start1, start2, do_fuzz):
    do_fuzz = bool(do_fuzz)
    start1 = find_station(start1, do_fuzz)
    start2 = find_station(start2, do_fuzz)
    par1, cos1 = dijkstra(start1)
    par2, cos2 = dijkstra(start2)
    potentials = find_meeting_place(cos1, cos2)
    return jsonify({'potentials':potentials})

if __name__ == '__main__':
    app.run(debug=True)
