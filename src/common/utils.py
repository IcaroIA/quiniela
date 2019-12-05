import requests
import xml.etree.ElementTree as ET
from src.common.database import Database
from src.models.user import User
from src.models.calendar import Calendar
from src.models.quiniela import Quiniela, Resultados
from openpyxl import load_workbook
import time
import json


def hash_password(password):
    return password


def season():
    r = requests.get("http://www.nfl.com/liveupdate/scorestrip/ss.xml")
    t = r.text
    root = ET.fromstring(t)
    attr = root[0].attrib
    year = int(attr['y'])
    week = int(attr['w'])
    return year, week


def schedule(year, stype, week):
    r = requests.get("http://www.nfl.com/ajax/scorestrip?season={}&seasonType={}&week={}".format(year, stype, week))
    text = r.text
    root = ET.fromstring(text)

    game = {}
    for child in root:
        for j in child:
            winner = 'No' if j.attrib['q'] == 'P' else j.attrib['h'] if int(j.attrib['hs']) > int(j.attrib['vs']) else j.attrib['v']
            differ = 0 if j.attrib['hs'] == '' else abs(int(j.attrib['hs']) - int(j.attrib['vs']))
            Calendar(str(year),str(week), j.attrib['eid'], j.attrib['gsis'], j.attrib['h'], j.attrib['hnn'], j.attrib['hs'],
                     j.attrib['v'], j.attrib['vnn'], j.attrib['vs'], j.attrib['d'], j.attrib['t'], winner, differ,
                     j.attrib['q'], j.attrib['k'], j.attrib['p'], '', '', '').save_to_mongo()
    return "Added week {} of season {}".format(week, year)


def get_week(temporada, sem):
    games = [game for game in Database.find('calendar', {'season': temporada, 'week': sem})]
    return games


def update_score(year, stype, week):
    r = requests.get("http://www.nfl.com/ajax/scorestrip?season={}&seasonType={}&week={}".format(year, stype, week))
    text = r.text
    root = ET.fromstring(text)
    for child in root:
        for j in child:
            query = {'gsis': j.attrib['gsis']}
            data = {'$set': {'Hscore': j.attrib['hs'], 'Vscore': j.attrib['vs']}}
            Database.update('calendar', query, data)

    return "Updated week {} of season {}".format(week, year)


def update_live_score():
    r = requests.get("http://www.nfl.com/liveupdate/scorestrip/ss.xml")
    text = r.text
    root = ET.fromstring(text)
    child = root[0]
    r_json = requests.get("http://www.nfl.com/liveupdate/scores/scores.json")
    text_json = r_json.text
    info = json.loads(text_json)

    for j in child:
        if 'k' in j.attrib and 'p' in j.attrib:
            query = {'gsis': j.attrib['gsis']}
            differ = abs(int(j.attrib['hs']) - int(j.attrib['vs']))
            if int(j.attrib['hs']) > int(j.attrib['vs']):
                data = {'$set':
                            {'Winner': j.attrib['h'], 'Hscore': j.attrib['hs'], 'Vscore': j.attrib['vs'], 'Differ': differ,
                             'quarter': j.attrib['q'], 'k': j.attrib['k'], 'p': j.attrib['p'],
                             'down': info[j.attrib['eid']]['down'], 'togo': info[j.attrib['eid']]['togo'], 'yl': info[j.attrib['eid']]['yl']}}
            elif int(j.attrib['hs']) < int(j.attrib['vs']):
                data = {'$set':
                            {'Winner': j.attrib['v'], 'Hscore': j.attrib['hs'], 'Vscore': j.attrib['vs'], 'Differ': differ,
                             'quarter': j.attrib['q'], 'k': j.attrib['k'], 'p': j.attrib['p'],
                             'down': info[j.attrib['eid']]['down'], 'togo': info[j.attrib['eid']]['togo'], 'yl': info[j.attrib['eid']]['yl']}}
            else:
                data = {'$set':
                            {'Winner': 'Tie', 'Hscore': j.attrib['hs'], 'Vscore': j.attrib['vs'], 'quarter': j.attrib['q'], 'Differ': differ,
                             'k': j.attrib['k'], 'p': j.attrib['p'], 'down': info[j.attrib['eid']]['down'],
                             'togo': info[j.attrib['eid']]['togo'], 'yl': info[j.attrib['eid']]['yl']}}
            try:
                game = Calendar.get_by_gsis(j.attrib['gsis'])
            except TypeError:
                game = None
            if game is None:
                pass
            else:
                Database.update('calendar', query, data)
        else:
            query = {'gsis': j.attrib['gsis']}
            differ = abs(int(j.attrib['hs']) - int(j.attrib['vs']))
            if int(j.attrib['hs']) > int(j.attrib['vs']):
                data = {'$set':
                            {'Winner': j.attrib['h'], 'Hscore': j.attrib['hs'], 'Vscore': j.attrib['vs'], 'Differ': differ,
                             'quarter': j.attrib['q'], 'k': '', 'p': '','down': info[j.attrib['eid']]['down'],
                             'togo': info[j.attrib['eid']]['togo'], 'yl': info[j.attrib['eid']]['yl']}}
            elif int(j.attrib['hs']) < int(j.attrib['vs']):
                data = {'$set':
                            {'Winner': j.attrib['v'], 'Hscore': j.attrib['hs'], 'Vscore': j.attrib['vs'], 'Differ': differ,
                             'quarter': j.attrib['q'], 'k': '', 'p': '', 'down': info[j.attrib['eid']]['down'],
                             'togo': info[j.attrib['eid']]['togo'], 'yl': info[j.attrib['eid']]['yl']}}
            else:
                data = {'$set':
                            {'Winner': 'Tie', 'Hscore': j.attrib['hs'], 'Vscore': j.attrib['vs'], 'Differ': differ,
                             'quarter': j.attrib['q'],'k': '', 'p': '', 'down': info[j.attrib['eid']]['down'],
                             'togo': info[j.attrib['eid']]['togo'], 'yl': info[j.attrib['eid']]['yl']}}
            try:
                game = Calendar.get_by_gsis(j.attrib['gsis'])
            except TypeError:
                game = None
            if game is None:
                pass
            else:
                Database.update('calendar', query, data)

    return "Updated week"


def find_users():
    all_users = User.get_users()
    return [user._id for user in all_users]


def update_results(temporada, semana):
    all_users = find_users()
    for user in all_users:
        Quiniela.update_game_score(user, temporada, semana)
    return "All users game scores updated"


def update_totals(temporada, semana):
    all_users = find_users()

    for user in all_users:
        data = Quiniela.get_week(user, temporada, semana)
        resultado = 0
        for game in data:
            resultado = resultado + game.points
        Resultados.update_result(user, temporada, semana, resultado)


def upadate_anual(user, temporada):
    all_users = find_users()
    for user in all_users:
        pass


def upload_week(user, season, week):
    path = 'D:/WebDev/qnfl/src/static/NFL 2019.xlsx'
    wb = load_workbook(path)
    sheet = wb.get_sheet_by_name(user)
    player = User.get_by_name(user)
    rangos = {'1': range(8,24), '2': range(30, 46), '3': range(52, 68), '4': range(74,89), '5': range(95, 110),
              '6': range(116, 130), '7': range(136, 150), '8': range(156, 171), '9': range(177, 191),
              '10': range(197, 210), '11': range(216, 230), '12': range(236,250), '13': range(256,272)}
    for i in rangos[week]:
        game = Calendar.get_by_gsis(str(sheet._get_cell(i, 9).value))
        if sheet._get_cell(i, 4).value == 'L':
            pick = game.Home
            d_val =  sheet._get_cell(i, 5).value
        elif sheet._get_cell(i, 4).value == '':
            pick = 'DNA'
            d_val = 0
        elif sheet._get_cell(i, 4).value == 'V':
            pick = game.Visitor
            d_val = sheet._get_cell(i, 5).value
        else:
            pick = 'TIE'
            d_val = 0
        Quiniela(game.gameid,week, season, player._id, 'Hoy', pick, d_val , 0).save_to_mongo()
        time.sleep(20)