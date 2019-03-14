from flask import Flask, jsonify
import json
from fuzzywuzzy import process, fuzz
from urllib import parse

app = Flask(__name__)

with open('../graph/station_names.json', 'r') as names_file:
    '''all_names is for fuzzy matching, station_names finds MTA id from english name'''
    station_names = json.load(names_file)
    all_names = list(station_names.keys())

with open('../graph/costs.json', 'r') as costs_file:
    '''dictionary of [start][end]: mode, cost'''
    weekday_edges = json.load(costs_file)

with open('../graph/graph_network.json', 'r') as network_file:
    '''dictionary of [start]: list of child nodes'''
    node_children = json.load(network_file)

with open('../graph/stations.json', 'r') as station_file:
    '''for each station (including super and sub stations), dictionary of name, full_name, lat, lon, parent'''
    # i can remove sub stations? i might only need super stations. Don't need lat or long for now... but could need later?
    stations = json.load(station_file)

def get_full_name(station_number):
    '''get full name (including line names: like "Franklin Ave 2-3-4-5"'''
    return stations[station_number[:3]]['full_name']

def get_name(station_number):
    '''get short name like "Franklin Ave"'''
    return stations[station_number[:3]]['name']

def get_line(name):
    '''get line name, like "L" '''
    return name.split('#')[1]

def get_line_name(station):
    '''prettify the line name for some weird trains'''
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
    '''goes through the full graph, starting at starting point, and returns costs and parents'''
    def make_costs(start):
        '''create new costs dictionary of cost to get to every other station from start
           initialized as infinite, unless a direct neighbor of the starting station'''
        costs = {}
        for item in node_children:
            costs[item] = infinity
        for neighbor in node_children[start]:
            if get_name(neighbor) == get_name(start):
                costs[neighbor] = 1
            else:
                costs[neighbor] = weekday_edges[start][neighbor][1]
        return costs

    def make_parents(start):
        '''make blank dictionary of parents (the best station to get to a given station from'''
        parents = {}
        for item in node_children:
            parents[item] = None
        for neighbor in node_children[start]:
            move_type = weekday_edges[start][neighbor][0]
            parents[neighbor] = (start, move_type)
        return parents

    def find_lowest_cost_node(costs):
        '''finds the current lowest cost node'''
        lowest_cost = float('inf')
        lowest_cost_node = None
        for node in costs:
            cost = costs[node]
            if cost < lowest_cost and node not in processed:
                lowest_cost = cost
                lowest_cost_node = node
        return lowest_cost_node

    processed = set() 
    parents = make_parents(start)
    costs = make_costs(start)
    node = find_lowest_cost_node(costs)
    while node is not None:
        cost = costs[node]
        neighbors = weekday_edges[node]
        for n in neighbors:
            #if neighbors[n][0] != 'w': #ignore walk edges?
            new_cost = cost + neighbors[n][1]
            if costs[n] > new_cost:
                costs[n] = new_cost
                parents[n] = (node, neighbors[n][0])
        processed.add(node)
        node = find_lowest_cost_node(costs)
    return [parents, costs]

def find_station(name, do_fuzz=False):
    '''return the MTA ID of the start station
        do_fuzz determines whether fuzzy matching is needed.
        I plan on there being autocomplete on the front end,
        so normally do_fuzz should be false.
        Room for improvement: currently it just returns the
        first option out of possible sub-stations... resulting
        in "start at Atlantic on the 4, then transfer to the 2
        at Atlantic..." situations'''
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
    '''takes the parents, costs, start and end point and
       returns the actual route, derived from parents.
       Goes backwards: find parent of endpoint, then parent
       of that station, etc.

    type:  s     | w    | t        | r    | e
    means: start | walk | transfer | rail | end'''

    trip = []
    now = (ended, 'e')
    while now[0] != started:
        trip.append(now)
        try:
            now = parents[now[0]]
        except:
            print('error: ',now)
    trip.append(now)
    #first_type = now[1]
    trip_dets = []
    started = 0
    trip_type = 's'
    for stop in trip[::-1]:
        full = {'line':get_line(stop[0]), 'name':get_name(stop[0]), 'trip_type':trip_type}
        # if started == 0:
        #     trip_type = first_type
        trip_dets.append(full)
        trip_type = stop[1]
        started = 1
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
    '''find meeting place by calculating dijkstra from both start points'''
    def recur_try(blur):
        for stop, time in cos1.items():
            if time + blur > cos2[stop] > time - blur:
                potential.append((time, stop))
        return potential
    cos1 = simplify_costs(cos1)
    cos2 = simplify_costs(cos2)
    blur_factor = 1
    potential = []
    while len(potential) < 1:
        potential = recur_try(blur_factor)
        blur_factor += 1
    return sorted(potential, key=lambda x: x[0])

# def print_results(trip):
#     previous = ' # '
#     for stop in trip:
#         if get_line(stop) != get_line(previous):
#             print("Transfer to...")
#         else:
#             print('Next stop:')
#             print('\t', get_name(stop) + " " + stop.split("#")[1])
#         previous = stop

def find_meeting_place(start1, start2):
    par1, cos1 = dijkstra(start1)
    par2, cos2 = dijkstra(start2)
    potentials = find_meeting_place(cos1, cos2)
    return potentials

def get_route(start, end):
    par, cos = dijkstra(start)
    route = parse_results(par, cos, start, end)
    time = cos[end] // 60
    return {'time':time, 'route':route, 'start':get_name(start), 'end':get_name(end)}

@app.route('/api/route/<string:do_fuzz>/<string:start>/<string:end>/', methods=['GET'])
def return_route(start, end, do_fuzz):
    do_fuzz = bool(do_fuzz)
    start = find_station(start, do_fuzz)
    end = find_station(end, do_fuzz)
    result = get_route(start, end)
    return jsonify(result)

@app.route('/api/meeting/<string:do_fuzz>/<string:start1>/<string:start2>/', methods=['Get'])
def return_meeting_place(start1, start2, do_fuzz):
    do_fuzz = bool(do_fuzz)
    start1 = find_station(start1, do_fuzz)
    start2 = find_station(start2, do_fuzz)
    potentials = find_meeting_place(start1, start2)
    return jsonify({'potentials':potentials})
    #to do: should also return routes for both users to each potential
    # maybe just return potentials and parents, then calculate route on front end?

def test_case():
    return_route('Franklin Av 2-3-4-5', "Flushing - Main St 7", False)

if __name__ == '__main__':
    app.run(debug=True)
