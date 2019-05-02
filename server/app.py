from flask import Flask, jsonify, make_response, send_from_directory
import json, os
from fuzzywuzzy import process, fuzz
from urllib import parse

app = Flask(__name__, static_folder="react/build")

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
    '''modified from "Grokking Algorithms" by Aditya Bhargava '''
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
    name = parse.unquote(name)
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

    get_off_flag = 0 #to see if next stop is walking or transfer
    trip = []
    now = (ended, 'e')
    while now[0] != started:
        if get_off_flag == 1:
            now = (now[0], now[1]+'g')
            get_off_flag = 0
        trip.append(now)
        if now[1] in ['w', 't']:
            get_off_flag = 1
        now = parents[now[0]]
    trip.append(now)

    trip_dets = []
    trip_type = 's'
    for stop in trip[::-1]:
        full = {'line':get_line(stop[0]), 'name':get_name(stop[0]), 'trip_type':trip_type}
        trip_dets.append(full)
        trip_type = stop[1]
    #trip_dets[-1]['trip_type'] = 'e'

    if trip_dets[1]['trip_type'] in ['t', 'w']:
        trip_dets.pop(0)
        if trip_dets[0]['trip_type'] == 't':
            trip_dets[0]['trip_type'] = 's'
    return trip_dets

def create_route_text(route):
    '''create text explanation of each step in the route'''
    def get_route_name(name):
        '''fix odd route names'''
        if name == 'AR' or name== 'AL': #AL and AR are the branches of the A train
            return 'A'
        elif 'GC' in name:
            return 'Grand Central Shuttle'
        elif 'FA' in name:
            return 'Franklin Ave. Shuttle'
        elif 'R_' in name:
            return 'Rockaway Shuttle'
        else:
            return name
    complete_route = []
    previous = ''
    for stop in route:
        text = ''
        name = stop['name']
        line = get_route_name(stop['line'])
        trip_type = stop['trip_type']
        if trip_type == 's':
            text = 'Start journey on the {} Train at {}'.format(line, name)
        elif trip_type == 'r':
            text = '...pass {}...'.format(name)
        elif trip_type == 't':
            text = 'Within the station, transfer to the {} Train at {}.'.format(line, name)
        elif trip_type == 'w':
            if text != '' and text[-1] == ',':
                text = 'Leave the station, then walk to the {} Train at {}.'.format(previous, line, name)
            else:
                text = 'Walk to the {} Train at {} and board.'.format(line, name)
        elif trip_type == 'e':
            text = 'Arrive at {}, your destination.'.format(name)
        elif trip_type == 'rg':
            text = 'Get off the train at {},'.format(name)
        else:
            text = 'error: {}'.format(trip_type)
        previous = name
        complete_route.append({'name':name, 'line':line, 'trip_type':trip_type, 'text':text})
    if trip_type == 'r':
        complete_route[-1]['text'] = 'Arrive at {}, your destination.'.format(name)
    if complete_route[-1]['text'][0] != 'A':
        complete_route.append({'name':name, 'line':line, 'trip_type':'e', 'text':'Arrive at {}, your destination.'.format(name)})
    return complete_route

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

def find_meeting_place(start_1, start_2, count):
    '''find meeting place by calculating dijkstra from both start points'''

    def recur_try(blur, costs_1, costs_2):
        '''look for potential meeting places, with travel time within "blur" distance'''
        potentials = []
        for stop, time in costs_1.items():
            time_to_other = costs_2[stop]
            if time + blur > time_to_other > time - blur:
                potentials.append({'name': stop, 'time':time, 'time_2':time_to_other})
        return potentials

    parents_1, costs_1 = dijkstra(start_1)
    parents_2, costs_2 = dijkstra(start_2)
    costs_1 = simplify_costs(costs_1)
    costs_2 = simplify_costs(costs_2)
    blur_factor = 1
    potential = []
    while len(potential) < count:
        """look for endpoint with same travel time,
        retrying with looser parameters until sufficent count"""
        potential = recur_try(blur_factor, costs_1, costs_2)
        blur_factor += 1
    results = sorted(potential, key=lambda x: x['name'])[:count]
    for end in results:
        # append directions from both start points
        route = parse_results(parents_1, costs_1, start_1, find_station(end['name']))
        end['route_1'] = create_route_text(route)
        route = parse_results(parents_2, costs_2, start_2, find_station(end['name']))
        end['route_2'] = create_route_text(route)
    return results


def get_route(start, end):
    par, cos = dijkstra(start)
    route = parse_results(par, cos, start, end)
    time = cos[end] // 60
    return {'time':time, 'route':route, 'start':get_name(start), 'end':get_name(end)}


def package_response(content):
    response = make_response(content)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/')
def return_react_app():
    return send_from_directory('react/build', 'index.html')

@app.route('/static/<path:path>')
def return_static(path):
    print('returning static file at {}'.format(path))
    if path !='' and os.path.exists('react/build/static/' + path):
        return send_from_directory('react/build/static/' , path)
    else:
        return send_from_directory('react/build/', 'index.html')

@app.route('/api/route/<string:do_fuzz>/<string:start>/<string:end>/', methods=['GET'])
def return_route(start, end, do_fuzz):
    do_fuzz = bool(do_fuzz)
    start = find_station(start, do_fuzz)
    end = find_station(end, do_fuzz)
    result = get_route(start, end)
    return package_response(jsonify(result))

@app.route('/api/meeting/<string:do_fuzz>/<string:start_1>/<string:start_2>/<int:count>', methods=['Get'])
def return_meeting_place(start_1, start_2, do_fuzz, count):
    do_fuzz = bool(do_fuzz)
    start_1 = find_station(start_1, do_fuzz)
    start_2 = find_station(start_2, do_fuzz)
    potentials = find_meeting_place(start_1, start_2, count)
    return package_response(jsonify({'potentials':potentials}))

def test_case():
    return_route('Franklin Av 2-3-4-5', "Flushing - Main St 7", False)


if __name__ == '__main__':
    app.run()
