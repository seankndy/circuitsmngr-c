#!/usr/bin/env python

import argparse
import json
import os
from sys import exit
import requests

def parse_arguments():
    """Parse command-line arguments, return dict."""

    parser = argparse.ArgumentParser(description='circuitsmngr device connect utility')

    update_cache_group = parser.add_argument_group(title='Local cache update')
    update_cache_group.add_argument('--update-cache', action='store_true', help='Update local device cache and exit')
    update_cache_group.add_argument('-u', '--user', help='Specify your circuitsmngr username.')
    update_cache_group.add_argument('-p', '--password', help='Specify your circuitsmngr password.')

    parser.add_argument('--config', default=os.environ['HOME']+'/.config/c.json', help='Specify configuration file, defaults to $HOME/.config/c.json')
    parser.add_argument('-c', '--client', help='Specify client/customer')
    parser.add_argument('--bash-completion', choices=['client','service','network'], help='For use with bash completion to specify what to search.')

    parser.add_argument('query', nargs='?', default='', help='Device query')

    args = parser.parse_args()

    if args.update_cache and args.query:
        raise parser.error("--update-cache cannot be called with a query")

    if args.update_cache and not (args.user and args.password):
        raise parser.error("--update-cache requires --user and --password")

    if not args.update_cache and not args.query:
        raise parser.error("query required")

    return vars(args)

def load_config(filename):
    try:
        with open(filename) as fh:
            try:
                return json.load(fh)
            except:
                raise Exception('Failed to parse configuration, check syntax.')
    except FileNotFoundError:
        return {}

def load_cache(filename):
    with open(filename) as fh:
        try:
            cache = json.load(fh)
            devices = cache['devices'] if 'devices' in cache else []
            clients = cache['clients'] if 'clients' in cache else []
            return devices, clients
        except:
            return []

def fetch_cm_data(base_url, user, password):
    response = requests.post(
        base_url,
        json={'username':user, 'password':password},
        headers={'Content-type': 'application/json', 'Accept': 'application/json'}
    )

    if response.status_code == requests.codes.unauthorized:
        raise Exception('Invalid login.')

    if response.ok:
        return response.json()

def save_object_to_file_as_json(filename, obj):
    with open(filename, 'w+') as fh:
        json.dump(obj, fh, indent=2)

def err(msg):
    print('Error: ' + msg)
    exit(1)


def main():
    args = parse_arguments()
    default_config = {
        'commands.ssh1': '/usr/bin/ssh -1 -l %username% %hostname%',
        'commands.ssh2': '/usr/bin/ssh -l %username% %hostname%',
        'commands.telnet': '/usr/local/bin/telnet -K %hostname%',
        'commands.web': '/usr/bin/open http://%hostname%',
        'circuitsmngr.url': 'https://circuits.vcn.com/c.php',
        'cache.file': os.environ['HOME'] + '/.c-cache.json',
        'fallback.user': '',
        'fallback.proto': 'telnet',
    };
    try:
        config = {
            **default_config,
            **(load_config(args['config']) if 'config' in args and args['config'] else {})
        }
        config['cache.file'] = os.path.expanduser(config['cache.file'])
    except Exception as e:
        err(str(e))

    if not args['update_cache'] and not os.path.exists(config['cache.file']):
        err('one or more cache files do not exist.  You probably need to run --update-cache -u <user> -p <pass>.')

    if args['update_cache']:
        try:
            data = fetch_cm_data(config['circuitsmngr.url'], args['user'], args['password'])

            if 'devices' not in data or 'clients' not in data:
                raise Exception('Invalid data returned from circuitsmngr.')

            save_object_to_file_as_json(
                config['cache.file'],
                data
            )

            print('cache updated ({} devices, {} clients)'.format(len(data['devices']), len(data['clients'])))
            exit()
        except Exception as e:
            err(str(e))

    try:
        devices, clients = load_cache(config['cache.file'])
    except FileNotFoundError:
        err('Cache file '+config['cache.file']+' does not exist, run --update-cache first.')

    client_id = None
    if args['client']:
        for c in clients:
            if c['name'] == args['client']:
                client_id = c['id']
                break
        else:
            err('Client not found in cache, maybe it needs updated?')

    if args['bash_completion']:
        if args['bash_completion'] == 'client':
            print(*[c['name'] for c
                in clients
                if c['name'][:len(args['query'])] == args['query']
            ], sep='\n')
        elif args['bash_completion'] in ['service','network']:
            print(*[d['full_name'] for d in devices
                if d['location_type'] == args['bash_completion']
                    and (not client_id or client_id in d['clients'])
                    and d['full_name'][:len(args['query'])] == args['query']
            ], sep='\n')

        exit()

    try:
        device = [d for d
            in devices
            if d['full_name'] == args['query']
              and (not client_id or d['location_type'] == 'service')
        ][0]
    except IndexError:
        err('device not found')

    user = device['user'] if device['user'] else config['fallback.user']
    proto = device['proto'] if device['proto'] else config['fallback.proto']

    if proto == 'ssh':
        proto = 'ssh1'

    cmd = ''
    if 'commands.'+device['proto'] in config:
        cmd = config['commands.'+device['proto']]

    cmd = cmd.replace('%username%', user)
    cmd = cmd.replace('%hostname%', device['ip'])

    os.system(cmd)


if __name__ == "__main__":
    main()
