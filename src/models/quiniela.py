from src.common.database import Database
from src.models.calendar import Calendar
import uuid


class Quiniela(object):

    def __init__(self, gameid, week, temporada, player, date, result, score, points, _id=None):
        self.gameid = gameid
        self.week = week
        self.temporada = temporada
        self.player = player
        self.date = date
        self.result = result
        self.score = score
        self.points = points
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return { "_id": self._id,
                 "gameid": self.gameid,
                 "week": self.week,
                 "temporada": self.temporada,
                 "player": self.player,
                 "date": self.date,
                 "result": self.result,
                 "score": self.score,
                 "points": self.points}

    def save_to_mongo( self ):
        Database.insert("quiniela", self.json())

    @classmethod
    def get_week(cls, user, temporada, week):
        return [cls(**game)for game in Database.find("quiniela", {"player": user, 'week': week, 'temporada': temporada})]

    @staticmethod
    def update_game_score(user, temporada, week):
        data = Quiniela.get_week(user, temporada, week)
        for game in data:
            if game.result == Calendar.get_winner(game.gameid):
                result = 100 - abs(int(game.score) - Calendar.get_differ(game.gameid))
                # print('Result of quniela 1st if update score {}'.format(result))
                # print(game.result, game.gameid, game.score)
                Database.update("quiniela", {"player": user, 'gameid': game.gameid},
                                {'$set': {'points': result}})
            else:
                result = 0
                # print('Result of quniela 1st else update score {}'.format(result))
                # print(game.result, game.gameid, game.score)
                Database.update("quiniela", {"player": user, 'gameid': game.gameid},
                                {'$set': {'points': result}})
        for game in data[::-1]:
            if game.result == Calendar.get_winner(game.gameid):
                result = 100 - abs(int(game.score) - Calendar.get_differ(game.gameid))
                # print('Result of quniela 2nd if update score {}'.format(result))
                # print(game.result, game.gameid, game.score)
                Database.update("quiniela", {"player": user, 'gameid': game.gameid},
                                {'$set': {'points': result}})
            else:
                result = 0
                # print('Result of quniela 2nd else update score {}'.format(result))
                # print(game.result, game.gameid, game.score)
                Database.update("quiniela", {"player": user, 'gameid': game.gameid},
                                {'$set': {'points': result}})


class Resultados(object):

    def __init__(self, season, week, player, total,  _id=None):
        self.season = season
        self.week = week
        self.player = player
        self.total = total
        self._id= uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "Total de la semana {} de {}".format(self.week, self.player)

    def json(self):
        return { '_id': self._id,
                 'season': self.season,
                 'week': self.week,
                 'player': self.player,
                 'total': self.total}

    def save_to_mongo(self):
        Database.insert("resultados", self.json())

    @classmethod
    def get_result(cls, player, season, week):
        data = Database.find_one('resultados', {'player': player, 'week': week, 'season':season})
        if data is None:
            return None
        else:
            return cls(**data)

    @classmethod
    def update_result(cls, user, temporada, semana, resultado):
        if cls.get_result(user, temporada, semana) is None:
            cls(temporada, semana, user, resultado).save_to_mongo()
            # print("Created new record for player " + user)
        else:
            query = {'player': user, 'season': temporada, 'week': semana}
            data = {'$set': {'total': resultado}}
            Database.update('resultados', query, data)
            # print("updated weekly score for player "+ user)

    @staticmethod
    def get_all_results(season, week):
        return [res for res in Database.find_ord('resultados', {'season': season, 'week': week},'total')]


class Anual(object):

    def __init__(self, season, player, total, _id=None):
        self.season = season
        self.player = player
        self.total = total
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "Total de la temporada de {} en la temporada {}".format(self.player, self.season)

    def json(self):
        return { '_id': self._id,
                 'season': self.season,
                 'player': self.player,
                 'total': self.total}

    def save_to_mongo(self):
        Database.insert("anual", self.json())

    @staticmethod
    def get_result(player, season):
        data = Database.find('resultados', {'player': player, 'season': season})
        if data is None:
            return None
        else:
            resultados = [res for res in data]
        total = 0
        for res in resultados:
            total = total + res['total']
        return total

    @classmethod
    def get_result_user(cls, player, season):
        data = Database.find_one('anual', {'player': player, 'season': season})
        if data is None:
            return None
        else:
            return cls(**data)

    @staticmethod
    def get_all_results(season):
        return [res for res in Database.find_ord('anual', {'season': season}, 'total')]

    @classmethod
    def update_totals(cls, user, temporada, resultado):
        if cls.get_result_user(user, temporada) is None:
            cls(str(temporada), user, resultado).save_to_mongo()
            # print("Created new anual total for player " + user)
        else:
            query = {'player': user, 'season': temporada}
            data = {'$set': {'total': resultado}}
            Database.update('anual', query, data)
            # print("updated total {} score for player ".format(resultado) + user)