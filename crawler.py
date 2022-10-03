import requests
import json
from os import path
from pythonping import ping as pyping
from ping3 import ping
from IPy import IP, IPSet
from datetime import datetime
from time import time, sleep
from pickle import load, dump


iter_minute = 0
full_ip_list = []
ip_map = {}
config = {}
ms_set = {
    'mess_header': 'Некоторые майнеры недоступны',
    'mess_body': 'Перечисленные ниже устройства не отвечают:',
}


def monitoring():
    global iter_minute
    while True:
        full_initialization('config.json')
        iter_minute += config.get('sleep_time')
        print(f'START CHECKING AT {datetime.now().time()}')
        checking_ip_set()
        print(f'END CHECKING AT {datetime.now().time()}. PROGRAM WORKING {iter_minute} MIN')
        sleep(config.get('sleep_time')*60)


def put_ip_map(devices_map, file):
    with open(file, 'wb') as f:
        dump(devices_map, f)


def full_initialization(conf):
    try:
        init_config(conf)
        init_ip_addresses(config.get('miner_list'), config.get('miner_map'))
    except FileNotFoundError:
        error_exit('One of the files not found in program directory: config.json, miner_list.txt, ip_map.pickle')
    except TypeError:
        error_exit('The configuration file is incorrect')


def init_ip_addresses(list_ip, map_ip):
    global ip_map
    global full_ip_list
    with open(list_ip) as fl:
        full_ip_list = [row.strip() for row in fl if validation_ip(row)]
    if path.getsize(map_ip) > 0:
        with open(map_ip, 'rb') as fm:
            ip_map = load(fm)
    print(f'{len(full_ip_list)} DEVICES INITIALIZED')


def init_config(file):
    global config
    with open(file) as f:
        data = json.load(f)
    for d in data:
        config[d] = data.get(d)
    print('CONFIGURATION INITIALIZED')


def update_ip_status(failed_list, file):
    global ip_map
    for ip in full_ip_list:
        if not ip_map.get(ip) or ip not in failed_list:
            ip_map[ip] = config.get('sleep_time')
        elif ip_map.get(ip) < config.get('sleep_limit'):
            ip_map[ip] = ip_map.get(ip) * config.get('skip_multiplier')
    put_ip_map(ip_map, file)


def checking_ip_set():
    fail_list = ping_ip_set(full_ip_list)
    if fail_list and not ping_ip_set(config.get('trusted_list')):
        update_ip_status(fail_list, config.get('miner_map'))
        send_message(config.get('send_tg'), config.get('send_mail'), message(fail_list))


def ping_ip_set(ip_list):
    failed_list = [i for i in ip_list if (ip_map.get(i) is None or iter_minute % ip_map.get(i) == 0) and not ping_ip(i)]
    return failed_list


def validation_ip(address):
    try:
        IP(address)
        return True
    except ValueError:
        return False


def ping_ip(ip):
    try:
        is_ping = True if ping(ip) else pyping(ip).success()
        print(f'{ip} - OK') if is_ping else print(f'{ip} - FAILED')
        return is_ping
    except (RuntimeError, OSError):
        print(f'{ip} - NETWORK ERROR')
        return False


def error_exit(text):
    print(f'Program has been stopped. {text}')
    input()
    exit()


def main():
    monitoring()


if __name__ == '__main__':
    main()