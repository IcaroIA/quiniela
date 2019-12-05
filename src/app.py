from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, session, url_for
from werkzeug.utils import redirect
from src.common.database import Database
from datetime import datetime
from src.models.user import User
from src.common.utils import season, get_week, find_users, update_live_score, update_results, update_totals
from src.models.quiniela import Quiniela, Resultados, Anual
from src.models.calendar import Calendar
import os


app = Flask(__name__)
app.secret_key = '1234'


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/', methods=['GET'])
def landing():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        name = request.form['registerName']
        email = request.form['registerEmail']
        password = request.form['registerPassword']
        date = datetime.utcnow()
        if User.register(email, name, password, date):
            return redirect(url_for('login_user', name=name, year=date.year))
        else:
            return redirect(url_for('landing'))


@app.route('/login/<string:name>', methods=['GET','POST'])
def login_user(name):
    if request.method == 'GET':
        if session['email'] is not None:
            user = User.get_by_email(session['email'])
            year = User.get_by_email(session['email']).date
            temporada, week = season()
            games = Calendar.get_week(temporada=str(temporada), week=str(week))
            juegos = Quiniela.get_week(user=user._id, temporada=str(temporada), week=str(week))
            resultado = Resultados.get_result(user._id, str(temporada), str(week))
            week_scores = Resultados.get_all_results(str(temporada), str(week))
            totals = Anual.get_all_results(str(temporada))
            try:
                maxi = max([total['total'] for total in totals])
            except ValueError:
                maxi = 0
            try:
                max20 = [total['total'] for total in totals][19]
            except IndexError:
               max20 = 0
            return render_template("profile.html", name=user.name, year=year.year, temporada=temporada, week=week,
                                   games=games, juegos=juegos, resultado=resultado, week_scores = week_scores,
                                   totals=totals, maxi=maxi, max20=max20)
        else:
            return redirect(url_for('landing'))
    else:
        name = request.form['inputName']
        password = request.form['inputPassword']
        if User.is_login_valid(name, password):
            User.login(name)
            user = User.get_by_name(name)
            year = User.get_by_name(name).date
            temporada, week = season()
            games = Calendar.get_week(temporada=str(temporada), week=str(week))
            juegos = Quiniela.get_week(user=user._id, temporada=str(temporada), week=str(week))
            resultado = Resultados.get_result(user._id, str(temporada), str(week))
            week_scores = Resultados.get_all_results(str(temporada), str(week))
            totals = Anual.get_all_results(str(temporada))
            try:
                maxi = max([total['total'] for total in totals])
            except ValueError:
                maxi = 0
            try:
                max20 = [total['total'] for total in totals][19]
            except IndexError:
                max20 = 0
            return render_template("profile.html", name=user.name, year=year.year, temporada=temporada, week=week,
                                   games=games, juegos=juegos, resultado=resultado, week_scores = week_scores,
                                   totals=totals, maxi=maxi, max20=max20)
        else:
            session['email'] = None
            return redirect(url_for('landing'))


@app.route('/logout')
def log_out():
    session['email'] = None
    return redirect(url_for('landing'))


@app.route('/<string:name>/<string:season>')
def week(name, season):
    return render_template('weeks.html', name = name, season = season)


@app.route('/<string:name>/<string:temporada>/<string:sem>')
def calendar(name, temporada, sem):

    temporada, week = temporada, sem
    player = User.get_by_name(name)
    name = player.name
    games = Calendar.get_week(temporada=str(temporada), week=str(week))
    juegos = Quiniela.get_week(user=player._id, temporada=str(temporada), week=str(week))
    return render_template('calendar.html', player = player, temporada = temporada, sem = sem, games = games,
                           juegos=juegos, name=name)


@app.route('/<string:name>/<string:temporada>/<string:sem>/played', methods=['POST'])
def resultado(name, temporada, sem):
    user = User.get_by_email(session['email'])
    temporada = temporada
    sem = sem
    f = request.form
    for i in range(len(f.getlist('gameid'))):
        gameid = f.getlist('gameid')[i]
        winner = f.getlist('winner')[i]
        gamescore = f.getlist('diff')[i]
        Quiniela(gameid, sem, temporada, user._id, 'Hoy', winner, gamescore, 0).save_to_mongo()


    return redirect(url_for('quiniela', name=user.name, sem=sem, temporada=temporada))


@app.route('/<string:name>/<string:temporada>/<string:sem>/play', methods=['GET'])
def quiniela(name, temporada, sem):
    user = User.get_by_email(session['email'])
    temporada = temporada
    sem = sem
    games = get_week(temporada, sem)
    if request.method == "GET":
        juegos = [game for game in Database.find('quiniela', {'temporada': temporada, 'week': sem, 'player': user._id})]
        if juegos:
            return render_template('resultado.html',name = user.name, temporada = temporada, sem = sem, games = juegos)
        return render_template('quiniela.html', name = name, temporada = temporada, sem = sem, games = games)


@app.route('/<string:name>/<string:temporada>/<string:sem>/result')
def resultados(temporada, sem, name):
    user = User.get_by_email(session['email'])
    juegos = Quiniela.get_week(user=user._id, temporada=temporada, week=sem)
    weekly = Resultados.get_all_results(str(temporada), str(sem))
    print(weekly)
    try:
        resultado = Resultados.get_result(user._id, temporada, sem).total
    except TypeError:
        resultado = 0
    except AttributeError:
        resultado = 0
    return render_template('resultados.html',name = user.name, temporada = temporada, sem = sem, games = juegos,
                           weekly= weekly, resultado=resultado)


@app.route('/<string:name>/pagos')
def bank(name):
    return "Holder for bank"


@app.context_processor
def utility_processor():
    def game_day(gameid):
        return Database.find_one('calendar', {'gameid': gameid})['Day']
    return dict(game_day=game_day)


@app.context_processor
def utility_processor():
    def game_h(gameid):
        return Database.find_one('calendar', {'gameid': gameid})['Home']
    return dict(game_h=game_h)


@app.context_processor
def utility_processor():
    def game_home(gameid):
        return Database.find_one('calendar', {'gameid': gameid})['Homenn']
    return dict(game_home=game_home)


@app.context_processor
def utility_processor():
    def game_visit(gameid):
        return Database.find_one('calendar', {'gameid': gameid})['Visitornn']
    return dict(game_visit=game_visit)


@app.context_processor
def utility_processor():
    def game_v(gameid):
        return Database.find_one('calendar', {'gameid': gameid})['Visitor']
    return dict(game_v=game_v)


@app.context_processor
def utility_processor():
    def game_v_score(gameid):
        return Database.find_one('calendar', {'gameid': gameid})['Vscore']
    return dict(game_v_score=game_v_score)


@app.context_processor
def utility_processor():
    def game_h_score(gameid):
        return Database.find_one('calendar', {'gameid': gameid})['Hscore']
    return dict(game_h_score=game_h_score)


@app.context_processor
def utility_processor():
    def game_winner(gameid):
        return Database.find_one('calendar', {'gameid': gameid})['Winner']
    return dict(game_winner=game_winner)


@app.context_processor
def utility_processor():
    def game_differ(gameid):
        return Database.find_one('calendar', {'gameid': gameid})['Differ']
    return dict(game_differ=game_differ)


@app.context_processor
def utility_processor():
    def player_name(id):
        return Database.find_one('users', {'_id': id})['name']
    return dict(player_name=player_name)


def sensor():
    """ Function for test purposes. """
    temporada, semana = season()
    Database.initialize()
    users = find_users()
    update_live_score()
    update_results(str(temporada), str(semana))
    for user in users:
        Quiniela.update_game_score(user, str(temporada), str(semana))
        resultado = Anual.get_result(user, str(temporada))
        Anual.update_totals(user,str(temporada), resultado)
    update_totals(str(temporada), str(semana))
    print(users, temporada, semana)


sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor,'interval',minutes=1)
sched.start()


if __name__ == '__main__':
    app.run(port=4995, debug=True)