import csv, json, math, os
from datetime import datetime

WAIT_TIME = 600 #constant to represent wait time when transferring

######################################
# This file processes an NYC MTA GTFS dataset and creates a graph representing 
# each station stop as a node, with edges representing averaged travel time.
# Lots of complexities of the system are ironed out and special schedules are
# ignored. All trains are portrayed as weekday non-rush-hour service.
# Data is built up using station and trip information to parse stop times.
######################################


# bad_ids represents some odd Q train behavior I could not figure out other than
# hardcoding the 'bad' trip labels in.
bad_ids = [ 'BFA18GEN-N091-Weekday-00_049850_N..N65R', 'BFA18GEN-N091-Weekday-00_100200_N..N65R',
            'BFA18GEN-N091-Weekday-00_045550_N..N65R', 'BFA18GEN-N091-Weekday-00_089800_N..N65R',
            'BFA18GEN-N091-Weekday-00_093300_N..N69R', 'BFA18GEN-N091-Weekday-00_094500_N..N65R']


# get trips from trips.txt-- includes unique id, route, service, and "sign"
# each "trip" is one end-to-end subway journey scheduled for a particular time
# think "the 8AM Manhattan-Bound 4 Train"

all_trips = {}

print('Reading trips...')
with open("./data/trips.txt", 'r') as trips_txt:
    next(trips_txt)
    for line in trips_txt:
        line = line.split(",")
        route = line[0]
        service = line[1]
        trip = line[2]
        sign = line[3]
        if trip not in all_trips:
            all_trips[trip] = {"route": route, "service": service, 'sign': sign}


# helper functions: 
def is_daytime(a_time):
    """ensures a time is between 10AM and 3PM-- 'normal' schedule"""
    NIGHTTIME = datetime.strptime("15:00:00", "%H:%M:%S")
    MORNING = datetime.strptime("10:00:00", "%H:%M:%S")

    if a_time < MORNING or a_time > NIGHTTIME:
        return False
    else:
        return True

def get_name(station_number):
    """returns the name of a station, given the MTA station identifier"""
    return stations[station_number[:3]]['name']

def get_line(name):
    """return the Line ('A', '2', etc) of a train given station identifier"""
    return name.split('#')[1]

def get_line_name(station):
    """clean up line names, turn abbreviations into proper name"""
    station = get_line(station)
    if station =='GS':
        return 'GS_Shuttle'
    elif station == 'FS':
        return 'FA_Shuttle'
    elif station == 'AR' or station == 'AL':
        # "A" train forks to Lefferts (AL) and Far Rockaway (AR)
        return 'A'
    elif station == 'H':
        return 'R_Shuttle'
    else:
        return station

def fix_time(raw):
    # GTFS allows times greater than 24-- because a train that starts on a given day must be included in that day's schedule
    if int(raw[:2]) >= 24:
        return str('0' + str(int(raw[:2]) - 24) + raw[2:])
    else:
        return raw


#import stops from stops.txt

stations = {}
reverse_stations = {}

print('Importing stops...')
with open("./data/stops.txt", "r") as stops_file:
    next(stops_file)
    for line in stops_file:
        line = line.split(",")
        stations[line[0]] = {"name": line[2], "parent": line[9].strip(), 'lat': float(line[4]), 'lon': float(line[5])}
        reverse_stations[line[2]] = line[0][:3]


# read stop_times.txt and do some filtering

stops = []

#columns:
#0 trip_id, #1 arrival_time, # 2 departure_time, #3 stop_id, #4 stop_sequence,
#5 stop_headsign, #6 pickup_type, #7 drop_off_type, #8 shape_dist_traveled 

print('Importing Stop Times...')
with open("./data/stop_times.txt", 'r') as stop_times:
    next(stop_times)
    for line in stop_times:
        line = line.split(",")
        trip_id = line[0] #trip ID
        arrival = line[1] #time it arrived at station
        departure = line[2] #time it leaves station
        destined = all_trips[trip_id]['sign']
        #its displayed final destination, 'sign' column is blank in stop_times
        stop = line[3] # current stop
        sequence = line[4] #what number stop this is in the route
        route = all_trips[trip_id]['route'] #what route (A, C, 1, 2, 3, etc)

        arrival = datetime.strptime(fix_time(arrival),"%H:%M:%S")
        departure = datetime.strptime(fix_time(departure), "%H:%M:%S")

        if sequence == "1": #if it's the first stop on a path it won't have a travel time
            started = stop
            previous = ''
            prev_departure_time = ''
            edge_time = None
        else:
            wait_time = (departure - arrival).seconds
            edge_time = (arrival - prev_departure_time).seconds + wait_time
            #edge_time is time between arrival at this station and arrival at next station

        if route == 'A':
        #separate Lefferts and Rockway bound A trains, the only train that branches all day
            if destined == 'Ozone Park - Lefferts Blvd' or started == 'Ozone Park - Lefferts Blvd':
                route = 'AL' #A-Lefferts
            else:
                route = 'AR' #A-Rockaway

        if trip_id not in bad_ids:
            #bad_ids is a list of Q trains that run on the N line in the very early AM
            stops.append({'route': route, "id": trip_id, 'travel_time': edge_time,
                          'sequence': sequence, 'previous': previous,
                          "arrival": arrival, "departure": departure,
                          "stop": stop, 'started':started, 'destined':destined})
        previous = stop
        prev_departure_time = departure


#collect all weekday service patterns

weekday_services = set()

for trip in all_trips:
    service = all_trips[trip]['service']
    name = all_trips[trip]['route']
    if 'Weekday' in service and 'SIR' not in service:
        #sorry Staten Island...
        weekday_services.add(service)


# endpoints (and also, startpoints) for trains running a full route 
#(not stopping short or taking a rush-hour branch)

full_route_ends = {'1': ['South Ferry', 'Van Cortlandt Park - 242 St'],
                   '2': ['Wakefield - 241 St', 'Flatbush Av - Brooklyn College'],
                   '3': ['New Lots Av', 'Harlem - 148 St'],
                   '4': ['Crown Hts - Utica Av', 'Woodlawn'],
                   '5': ['Eastchester - Dyre Av', 'Flatbush Av - Brooklyn College'],
                   '6': ['Pelham Bay Park', 'Brooklyn Bridge - City Hall'],
                   '7': ['34 St - 11 Av', 'Flushing - Main St'],
                   'GS': ['Grand Central - 42 St', 'Times Sq - 42 St'],
                   'A': ['Inwood - 207 St', 'Ozone Park - Lefferts Blvd',
                         'Far Rockaway - Mott Av', 'Rockaway Park - Beach 116 St'],
                   'AL': ['Inwood - 207 St', 'Ozone Park - Lefferts Blvd'],
                   'AR': ['Far Rockaway - Mott Av', 'Inwood - 207 St'],
                   'B': ['Brighton Beach', '145 St'],
                   'C': ['Euclid Av', '168 St'],
                   'D': ['Coney Island - Stillwell Av', 'Norwood - 205 St'],
                   'E': ['World Trade Center', 'Jamaica Center - Parsons/Archer'],
                   'F': ['Coney Island - Stillwell Av', 'Jamaica - 179 St'],
                   'FS': ['Prospect Park', 'Franklin Av'],
                   'G': ['Church Av', 'Court Sq'],
                   'H': ['Broad Channel', 'Rockaway Park - Beach 116 St'],
                   'J': ['Broad St', 'Jamaica Center - Parsons/Archer'],
                   'Z': [], #ignore the Z... only runs at rush hour
                   'L': ['8 Av', 'Canarsie - Rockaway Pkwy'],
                   'M': ['Middle Village - Metropolitan Av', 'Forest Hills - 71 Av'],
                   'N': ['Coney Island - Stillwell Av', 'Astoria - Ditmars Blvd'],
                   'W': ['Whitehall St', 'Astoria - Ditmars Blvd'],
                   'Q': ['96 St', 'Coney Island - Stillwell Av'],
                   'R': ['Bay Ridge - 95 St', 'Forest Hills - 71 Av']}


# Functions to find "good" trains 
#(started and ended at right stations, daytime, weekday, doesn't change routes, not "x" type express)

def normal_route(route):
    '''remove "X" rush hour express routes and Staten Island trains'''
    if route[-1] != 'X' and 'SI' not in route:
        return True
    else:
        return False

def daytime_weekday_service(service, arrival):
    '''stop is made on a weekday during the day'''
    if is_daytime(arrival) and service in weekday_services:
        return True
    else:
        return False

def not_first(prev_stop):
    '''not first stop'''
    return prev_stop != ''

def normal_path(started, destination):
    ''' not first stop, destination and start point are correct for this route'''
    return destination in full_route_ends[route] and get_name(started) in full_route_ends[route]


edges_pre_avg = {}
previous_route = ''

print("Parsing Stop Times...")
for stop in stops:
    '''parse the stops read in from stop_times earlier and create the edges'''
    trip_id = stop["id"]
    parent = stop['stop']
    sequence = stop['sequence']
    destined = stop['destined']
    started = stop['started']
    now = stop['stop'] + '#' + route
    service = all_trips[stop['id']]['service']
    route = stop['route']
    name = stations[stop['stop']]['name']
    previous_stop = stop['previous'] + "#" + route
    arrival = stop['arrival']
    time = stop['travel_time']

    if not_first(previous_stop) and normal_route(route) and normal_path(started, destined) and daytime_weekday_service(service, arrival):
        # I separated all these functions to avoid 1 function with 6 positional args...
        # still ugly

        if len(previous_stop) > 3:
            # somehow some '' previous stops were sneaking past the check above
            # TODO fix this
            if previous_stop not in edges_pre_avg:
                edges_pre_avg[previous_stop] = {}
            if now not in edges_pre_avg[previous_stop]:
                edges_pre_avg[previous_stop][now] = []
            edges_pre_avg[previous_stop][now].append(time)
            if now not in edges_pre_avg:
                edges_pre_avg[now] = {}
    previous_route = route
print('\tDone.')


# This was an issue because of the way I parsed stops-- endpoints were missing
# for instance, the last Outward-Bound stop on the 4 is Utica,
# which got put into the data as an edge-endpoint but not a potential start.
# Even though it could be a startpoint for a transfer edge.

empty_ends = [] #endpoints with zero connections as of yet-- add back in when adding transfers
filtered_pre_avg = {}

print('Filtering edges...')
for start in edges_pre_avg:
    if len(edges_pre_avg[start]) == 0:
        empty_ends.append(start)
    else:
        filtered_pre_avg[start] = edges_pre_avg[start]


# In[12]:


#filter for most common path (to delete uncommon branches or trains that unexpectedly go local)
#then average the times.
#note that removing branches is OK because the two A train destinations are treated as separate lines
#all other branching routes are only during rush hour-- they're ignored for this version of the graph

averaged_edges = {}

print('Averaging edges...')
for start, ends in filtered_pre_avg.items():
    if start not in averaged_edges:
        averaged_edges[start] = {}
    maximum = 0
    maximum_key = ''
    for end, times in ends.items():
        if len(times) > maximum:
            maximum = len(times)
            maximum_key = end
    values = edges_pre_avg[start][maximum_key]
    tup = ('r' , math.ceil(sum(values) / len(values)))
    averaged_edges[start][maximum_key] = tup

# get sub-stops for every parent stop-- a sub stop represents one train that stops there 
# EG Nostrand Avenue 3 train stop has 2 sub_stops: 3 train Outbound and Inbound

sub_stops = {}

print('Finding sub-stops for each stop...')
for start, ends in averaged_edges.items():
    parent = start[:3]

    if parent not in sub_stops:
        sub_stops[parent] = []
    if start not in sub_stops[parent]:
        sub_stops[parent].append(start)

    for end in ends:
        end_parent = end[:3]

        if end_parent not in sub_stops:
            sub_stops[end_parent] = []
        if end not in sub_stops[end_parent]:
            sub_stops[end_parent].append(end)

# MTA treats some stops as multiple parent stops-- like the 2-3-4-5 vs D-N-R
# platforms at Atlantic. sub_stops only includes sub_stops of one parent


# check every combination of start and end, and make sure the reverse
# trip is also in averaged_edges. If you can get there from here, you can also
# get here from there.

averaged_edges_fixed = {}

def reverse_stop(stop):
    #returns the opposite direction train
    return stop[:3] + 'S' + stop[4:] if stop[3] == 'N' else stop[:3] + 'N' + stop[4:]

print('Ensuring all edges are mirrored-- you can get here from there.')
for start, ends in averaged_edges.items():
    reverse_start = reverse_stop(start)
    averaged_edges_fixed[start] = {}
    if start not in ['H01N#AR', 'H01S#AR']: #ignore these Rockaway stops the that have direction-dependent paths
        for end, time_tup in ends.items():
            averaged_edges_fixed[start][end] = time_tup
            reverse_end = reverse_stop(end)
            if get_line(reverse_start) == get_line(reverse_end):
                if reverse_end not in averaged_edges_fixed and reverse_end not in ['H01N#AR', 'H01S#AR']:#ditto above
                    #print(get_line(reverse_end), "From: ",reverse_end, get_name(reverse_end))
                    averaged_edges_fixed[reverse_end] = {}
                if reverse_end not in ['H01N#AR', 'H01S#AR', 'H02N#AR', 'H02S#AR'] and reverse_start not in averaged_edges_fixed[reverse_end]:
                    #print('\t to:', reverse_start, get_name(reverse_start))
                    averaged_edges_fixed[reverse_end][reverse_start] = time_tup

#for some reason this station is not getting added-- add it here TODO fix
averaged_edges_fixed['A65S#AL'] = {'A65N#AL': ('t', 820)}
#create graph_without_transfers: a dictionary of ONLY the next stop from a given stop. no transfers.

averaged_edges_fixed['M11S#J'].pop('M16S#J') #somehow an express train was sneaking through the filter above... TODO fix

# create next_stop_by_stop: for every stop, the next stop only.
next_stop_by_stop = {}

for start, ends in averaged_edges_fixed.items():
    for end in ends:
        if start not in next_stop_by_stop:
            next_stop_by_stop[start] = []
        if end not in next_stop_by_stop[start]:
            next_stop_by_stop[start].append(end)

# for line in transfers get the data and create transfer_edges

transfers_from_file = {}

print('Reading in transfers...')
with open('./data/transfers.txt', 'r') as transfer_file:
    next(transfer_file)#skip header
    for line in transfer_file:
        from_station, to, _, time = line.split(",")
        if from_station != '140':
            if from_station not in transfers_from_file:
                transfers_from_file[from_station] = {}
            if to not in transfers_from_file[from_station] and '140' not in to:
                transfers_from_file[from_station][to] = int(time) + WAIT_TIME


# some transfer edges don't exist for self-transfer... find those and add with a wait
transfers_with_self_transfers = dict(transfers_from_file)


print('Adding self-transfers from transfer file...')
for stop in sub_stops:
    if stop not in transfers_with_self_transfers:
        transfers_with_self_transfers[stop] = {stop: WAIT_TIME}
    else:
        if stop not in transfers_with_self_transfers[stop]:
            transfers_with_self_transfers[stop][stop] = WAIT_TIME

print('Ensuring all end-of-line stops exist for transfers...')
for stop in empty_ends:
    parent = stop[:3]
    if stop not in transfers_with_self_transfers:
        transfers_with_self_transfers[parent] = {parent: WAIT_TIME}
    else:
        if stop not in transfers_with_self_transfers[stop]:
            transfers_with_self_transfers[parent][parent] = WAIT_TIME #**


# add self-transfers to all edges

edges_with_self_transfers= dict(averaged_edges_fixed)

print('Adding self-transfers that were missing from file...')
for start, ends in averaged_edges.items():
    parent = start[:3]
    for sub_stop in sub_stops[parent]:
        neighbor = sub_stop[:3]
        time_tup = ('t', transfers_with_self_transfers[parent][neighbor])
        if sub_stop != start:
            edges_with_self_transfers[start][sub_stop] = time_tup


# make sure transfer edges that are transfer -only- (IE, they exist in Edges as ends but not starts) are added

edges_with_self_transfers_complete = dict(edges_with_self_transfers)

print('Cleanup second-check on missing self-transfers...')
for start, ends in edges_with_self_transfers.items():
    for end in ends:
        parent = end[:3]
        if end not in edges_with_self_transfers:
            edges_with_self_transfers_complete[end] = {}
            for sub in sub_stops[parent]:
                if sub != end: #* line below
                    edges_with_self_transfers_complete[end][sub] = ('t', transfers_with_self_transfers[parent][parent])

edges_with_self_transfers['A65S#AL'] = {'A65N#AL': ('t', 820)}


# note: transfers_with_self_transfers can have multiple transfers for 1 origin

edges_with_all_transfers = dict(edges_with_self_transfers_complete)

print('Combining trip edges with transfer edges...')
for start, ends in edges_with_self_transfers.items():
    parent = start[:3]
    if parent in transfers_with_self_transfers:
        for end, time in transfers_with_self_transfers[parent].items():
            for sub in sub_stops[end]:
                 if sub not in edges_with_all_transfers[start]:
                    if time < WAIT_TIME:
                        time_tup = ('t', time + WAIT_TIME)
                    else:
                        time_tup = ('t', time)
                    edges_with_all_transfers[start][sub] = time_tup


# filter out self-transfers like 'get off this 4 train, wait 5 minutes, get on the next one' that shouldn't be considered

weekday_edges_pre_walking = {}

print('Removing erroneous transfers...')
for start, ends in edges_with_all_transfers.items():
    for end, time_tup in ends.items():
        if end != start:
            if start not in weekday_edges_pre_walking:
                weekday_edges_pre_walking[start] = {}
            weekday_edges_pre_walking[start][end] = time_tup


# create a dict of all neighbors of a given station-- including after a transfer.
# This will be used to filter walk stations

within_one_stop = {}

def get_transfers(stop):
    '''look at all the potential endpoints and return only the transfers'''
    transfers = []
    for edge, time_tup in stop.items():
        if time_tup[0] == 't':
            transfers.append(edge)
    return transfers

# within_one_stop should include:
# next stop and its transfers
# transfers and their next stops and their transfers


for stop, next_stop in next_stop_by_stop.items():
    if next_stop[0] not in weekday_edges_pre_walking:
        print('missing: ', next_stop[0], get_name(next_stop[0]))
    else:
        next_transfers = get_transfers(weekday_edges_pre_walking[next_stop[0]]) #transfers of next stop
        transfers = get_transfers(weekday_edges_pre_walking[stop]) #transfers of current stop
        if transfers:
            transfer_next_neighbors = []
            transfer_nexts = [] # next stop of each transfer
            for t in transfers:
                try:
                    n = next_stop_by_stop[t]
                    transfer_nexts += n
                    transfer_next_neighbors += get_transfers(weekday_edges_pre_walking[n[0]])
                except KeyError:
                    pass # ignore keyerror that arises when looking for next stop of final stops
        full = next_stop + next_transfers + transfers + transfer_nexts + transfer_next_neighbors
        within_one_stop[stop] = list(set(full))


# within_one_stop is missing final stops and 1 random AR stop... code it in for now, find better solution TODO

within_one_stop['H02N#AR'] = ['H01N#AR', 'H03N#AR', 'H03S#AR', 'A61N#AR', 'A61S#AR', 'A61S#AL', 'A61N#AL']

missing = ['101N#1', '142S#1', '247S#2', '247S#5', '201N#2', '257S#3', '250S#4', '301N#3', '640S#6', '401N#4', '501N#5', '601N#6', '726S#7', '701N#7', '901S#GS', '902N#GS', 'A02N#AR', 'A02N#AL', 'A09N#C', 'A55S#C', 'H04N#H', 'H11S#AR', 'D13N#B', 'D26S#FS', 'D40S#B', 'D43S#D', 'D43S#F', 'D43S#N', 'D43S#Q', 'D01N#D', 'E01S#E', 'G08N#M', 'G08N#R', 'G05N#E', 'G05N#J', 'F27S#G', 'F01N#F', 'S01N#FS', 'G22N#G', 'H15S#H', 'M23S#J', 'L01N#L', 'L29S#L', 'M01S#M', 'R01N#N', 'R01N#W', 'R27S#W', 'Q05N#Q', 'R45S#R']

for stop in missing:
    within_one_stop[stop] = []


# add walking transfers

# 1. find distance nevins to hoyt-- 1/3 of a mile-- this is the max walk distance. Say it's 6 minutes

nevins = [40.688246, -73.980492]
hoyt = [40.690545, -73.985065]

a_sq = (nevins[0] - hoyt[0]) ** 2
b_sq = (nevins[1] - hoyt[1]) ** 2

max_walk = math.sqrt(a_sq + b_sq)
max_walk_time = 360
walk_per_second = max_walk_time / max_walk

# 2. measure distance of every station to every other station!?

weekday_edges_with_walking = dict(weekday_edges_pre_walking)

count = 0

missing_from_within = []

for start, ends in weekday_edges_pre_walking.items():
    for end in weekday_edges_pre_walking:
        if end != start and end not in within_one_stop[start]:
            start_lat, start_long = stations[start[:4]]['lat'], stations[start[:4]]['lon']
            end_lat, end_long = stations[end[:4]]['lat'], stations[end[:4]]['lon']
            a_sq = (start_lat - end_lat) ** 2
            b_sq = (start_long - end_long) ** 2
            distance = math.sqrt(a_sq + b_sq)
            # 3. Do the math to translate into time, add to edges as ('w', time)
            if distance <= max_walk:
                #print(get_name(start),' ', start, '\t to: ', get_name(end), ' ', end)
                count += 1
                time = math.ceil(walk_per_second * distance) + WAIT_TIME
                weekday_edges_with_walking[start][end] = ('w', time)


print(count, ' walking edges added.')


# add in two missing stations (?) #TODO debug why this is happening?

weekday_edges = dict(weekday_edges_with_walking)

weekday_edges['A65S#AL'] = {'A65N#AL': ('t', WAIT_TIME)}
weekday_edges['H01N#AR'] = {'A61N#AR': ('r', 180)}



# build node_children: for each node, all neighboring nodes (note that edges are directional)

node_children = {}

print('Finding children for all nodes...')
for start, ends in weekday_edges.items():
    parent = start[:3]
    node_children[start] = []
    node_children[start] += sub_stops[parent]
    if start in node_children[start]:
        node_children[start].remove(start)
    for end, value in ends.items():
        if end not in node_children[start] and end != start:
            node_children[start].append(end)

# remove self if in node_children
for node, children in node_children.items():
    if node in children:
        node_children[node].remove(node)


name_to_stations = {}
stations_with_full_name = dict(stations)
just_names = []


print('Creating name to MTA ID station dictionary... in both directions...')
for node, children in node_children.items():
    comp = [get_line_name(child) for child in children if get_name(child) == get_name(node) and weekday_edges[node][child][0]=='t']
    children_lines = sorted(list(set(comp)))
    name = get_name(node) + ' ' + '-'.join(children_lines)
    if ' ' != name[-1]:
        just_names.append(name)
    if name not in name_to_stations:
        children = [child for child in children if get_name(child) == get_name(node) and weekday_edges[node][child][0]=='t'] + [node]
        name_to_stations[name] = children
    stations_with_full_name[node[:3]]['full_name'] = name

just_names = sorted(list(set(just_names)))


print('Writing all data to disk.')
with open('./graph/station_names.json', 'w') as name_file:
    json.dump(name_to_stations, name_file, indent=2)

with open('./graph/all_names.json', 'w') as all_name_file:
    json.dump(just_names, all_name_file, indent=2)

with open('./graph/graph_network.json', 'w') as graph_file:
    json.dump(node_children, graph_file, indent=2)

with open('./graph/costs.json', 'w') as cost_file:
    json.dump(weekday_edges, cost_file, indent=2)

with open('./graph/stations.json', 'w') as stations_file:
    json.dump(stations_with_full_name, stations_file, indent=2)

# exported all of these which are then imported by the server to run the algo

