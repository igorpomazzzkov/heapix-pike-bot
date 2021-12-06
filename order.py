import json

import requests

class Pike:
    type = "snack"
    id = 32
    size = "big"
    dough = ""

    def __init__(self, type="snack", size="big", dought="", id=32):
        self.type = type
        self.size = size
        self.dough = dought
        self.id = id


def update_address(street: str, house: str):
    response = requests.post('https://pzz.by/api/v1/basket/update-address', data={'street': street, 'house': house})
    return response.json()


def order(data: dict):
    user_data = read_data_from_file()
    response_update_address = update_address(user_data['street'], user_data['house'])
    filling_card(data, user_data['pikes'])


def filling_card(data: dict, pikes: dict):
    pikes = list()
    for key, value in data.items():
        for key, value in value['answers'].items():
            pikes.append(pike_builder(value))
    for pike in pikes:
        print(json.decoder)
        response = requests.post('https://pzz.by/api/v1/basket/add-item', data=json.JSONDecoder(pike))


def read_data_from_file() -> dict:
    f = open('store.json', encoding="utf-8")
    data = json.load(f)
    f.close()
    return data


def pike_builder(pike: str) -> Pike:
    if pike == 'Тейсти':
        return Pike("snack", "big", "", 32)
    if pike == 'Острый':
        return Pike("snack", "big", "", 33)
    else:
        return Pike("snack", "big", "", 34)
