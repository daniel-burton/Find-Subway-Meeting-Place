from urllib import parse
import requests, json
from fuzzywuzzy import process, fuzz



with open('./graph/all_names.json', 'r') as names_file:
    all_names = json.load(names_file)


def try_name(prompt):
    '''Confirm the fuzzy match of user input'''
    user_typed = input(prompt)
    options = process.extract(user_typed, all_names)
    for i in options:
        attempt, score = i
        answer = input('Did you mean {}? '.format(attempt))
        if answer.lower() == 'y':
            return attempt


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


def print_response(re):
    '''parse the JSON response from the server and print the route directions'''
    print(re)
    announce = []
    announce.append('\nRoute from: {}\n to {}:\n'.format(re['start'], re['end']))
    announce.append('Elapsed time: {} minutes.'.format(re['time']))
    previous = ''
    for stop in re['route']:
        name = stop['name']
        line = get_route_name(stop['line'])
        # precis = name + line # to make sure train is at actual final stop-- not another stop with same simple name
        trip_type = stop['trip_type']
        if trip_type == 's':
            announce.append('Start journey on the {} Train at {}'.format(line, name))
        elif trip_type == 'r':
            announce.append('\t\t...arrive at {}...'.format(name))
        elif trip_type == 't':
            if announce[-1][-3:] == '...':
                announce.append('\tGet off at {}, then transfer to the {} Train at {}'.format(previous, line, name))
            else:
                announce.append('\tTransfer to the {} Train at {}'.format(line, name))
        elif trip_type == 'w':
            if announce[-1][-3:] == '...':
                announce.append('\tGet off at {}, then walk to the {} Train at {}'.format(previous, line, name))
            else:
                announce.append('\tWalk to the {} Train at {}'.format(line, name))
        elif trip_type == 'e':
            announce.append("Arrive at {}.\n\n".format(re['end']))
        previous = name
    for i in announce:
        print(i)

if __name__ =='__main__':
    start = try_name('Enter your starting point: ')
    end = try_name('Enter your destination: ')
    # turn the station strings into URL-formatted strings
    start = parse.quote_plus(start)
    end = parse.quote_plus(end)
    url = 'http://127.0.0.1:5000/api/route/False/{}/{}/'.format(start, end)
    response = requests.get(url)
    print_response(response.json())
