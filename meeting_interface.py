from urllib import parse
import requests, json
from fuzzywuzzy import process, fuzz



with open('./graph/all_names.json', 'r') as names_file:
    all_names = json.load(names_file)


def try_name(prompt):
    user_typed = input(prompt)
    options = process.extract(user_typed, all_names)
    for i in options:
        attempt, score = i
        answer = input('Did you mean {}? '.format(attempt))
        if answer.lower() == 'y':
            return attempt


def get_route_name(name):
    if name == 'AR' or name== 'AL':
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
    print('\nRoute from: {}\n to {}:\n'.format(re['start'], re['end']))
    print('Elapsed time: {} minutes.'.format(re['time']))
    previous = ''
    final =  re['route'][-1]['name'] + get_route_name(re['route'][-1]['line'])
    for stop in re['route']:
        name = stop['name']
        line = get_route_name(stop['line'])
        precis = name + line # to make sure train is at actual final stop-- not another stop with same simple name
        transfer = stop['transfer']

        if precis == final:
            print('Arrive at {}\n\n'.format(name))
            break
        elif transfer == 2:
            print('Start journey on the {} Train at {}'.format(line, name))
        elif transfer == 0 and name == previous:
            pass
        elif transfer == 0:
            print('\t\t...passing {}.'.format(name))
        elif transfer == 1:
            print('\tTransfer to the {} Train at {}'.format(line, name))

point1 = try_name('Enter point one: ')
point2 = try_name('Enter point two: ')

point1 = parse.quote_plus(point1)
point2 = parse.quote_plus(point2)

url = 'http://127.0.0.1:5000/api/meeting/False/{}/{}/'.format(point1, point2)
response = requests.get(url)

print(response.json())
