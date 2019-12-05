from src.common.database import Database
import uuid


class Calendar(object):

    def __init__(self, season, week, gameid, gsis, Home, Homenn, Hscore, Visitor, Visitornn, Vscore, Day, Time, Winner,
                 Differ, quarter, k, p, down, togo, yl, _id=None):
        self.season = season
        self.week = week
        self.gameid = gameid
        self.gsis = gsis
        self.Home = Home
        self.Homenn = Homenn
        self.Hscore = Hscore
        self.Visitor = Visitor
        self.Visitornn = Visitornn
        self.Vscore = Vscore
        self.Day = Day
        self.Time = Time
        self.Winner = Winner
        self.Differ = Differ
        self.quarter = quarter
        self.k = k
        self.p = p
        self.down = down
        self.togo = togo
        self.yl = yl
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "Game " + self.gsis + " of week " + self.week + " of season " + self.season

    def json(self):
        return {'_id': self._id,
                'season': self.season,
                'week':self.week,
                'gameid': self.gameid,
                'gsis': self.gsis,
                'Home': self.Home,
                'Homenn': self.Homenn,
                'Hscore': self.Hscore,
                'Visitor': self.Visitor,
                'Visitornn': self.Visitornn,
                'Vscore': self.Vscore,
                'Day': self.Day,
                'Time': self.Time,
                'Winner': self.Winner,
                'Differ': self.Differ,
                'quarter': self.quarter,
                'k': self.k,
                'p': self.p,
                'down': self.down,
                'togo': self.togo,
                'yl': self.yl
                }

    def save_to_mongo(self):
        Database.insert('calendar', self.json())

    @classmethod
    def get_week(cls, temporada, week):
        return [cls(**game) for game in
                Database.find("calendar", {'week': week, 'season': temporada})]

    @classmethod
    def get_winner(cls, gameid):
        game = Database.find_one('calendar', {'gameid': gameid})
        return cls(**game).Winner

    @classmethod
    def get_differ(cls, gameid):
        game = Database.find_one('calendar', {'gameid': gameid})
        return abs(int(cls(**game).Hscore) - int(cls(**game).Vscore))

    @classmethod
    def get_by_gsis(cls, gsis):
        game = Database.find_one('calendar', {'gsis': gsis})
        return cls(**game)