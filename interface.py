from urllib import parse
import requests, json
from fuzzywuzzy import process, fuzz



with open('./all_names.json', 'r') as names_file:
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
    final =  re['route'][-1]['name']
    for stop in re['route']:
        name = stop['name']
        line = get_route_name(stop['line'])
        transfer = stop['transfer']

        if name == final:
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

start = try_name('Enter your starting point: ')
end = try_name('Enter your destination: ')

start = parse.quote_plus(start)
end = parse.quote_plus(end)

url = 'http://127.0.0.1:5000/api/route/{}/{}/'.format(start, end)
response = requests.get(url)
print_response(response.json())
