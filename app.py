from flask import Flask, render_template, url_for, request, redirect, flash,g
import csv
import sqlite3
import random
import string
import hashlib
import binascii

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tajnehalo'

app_info = {
    'db_file':'hotel.db'
}


import sqlite3
from flask import g

def get_db():
    if not hasattr(g, 'sqlite_db'):
        conn = sqlite3.connect(app_info['db_file'])
        conn.row_factory = sqlite3.Row
        g.sqlite_db = conn
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
class PriorityType:
    def __init__(self, code, description, selected):
        self.code = code
        self.description = description
        self.selected = selected

    def __repr__(self):
        return f'<Priorytet {self.code}>'


class NotificationPriorities:
    def __init__(self):
        self.list_of_priorities = []

    def load_priorities(self):
        self.list_of_priorities.append(PriorityType('low','niski',''))
        self.list_of_priorities.append(PriorityType('medium','sredni','selected'))
        self.list_of_priorities.append(PriorityType('high','wysoki' ,''))

    def get_priority_by_code(self,code):
        for i in self.list_of_priorities:
            if i.code == code:
                return (i)
        return(PriorityType('unk','unk', 'unk'))

class UserPass:
    def __init__(self, user ='', password=''):
        self.user = user
        self.password = password

@app.route('/')
def index ():
        return render_template("index.html")


@app.route('/przyjecie_usterki', methods = ['POST', 'GET'])
def zgloszenie ():

    priorytet = NotificationPriorities()
    priorytet.load_priorities()

    if request.method == 'GET':
        return render_template('opis_usterki.html', lista=priorytet.list_of_priorities)
    else:
        nazwisko = request.form['nazwisko']
        numer_pokoju = request.form['numer_pokoju']
        opis_usterki = request.form['opis_usterki']
        priorytet = request.form['priorytet']
        return redirect(url_for('opis', active_menu='zgloszenie',nazwisko=nazwisko, numer_pokoju=numer_pokoju,
                                opis_usterki=opis_usterki, priorytet = priorytet ))

@app.route('/opis_usterki', methods = ['POST', 'GET'])
def opis():
    czas = 'dzien'
    nazwisko = request.args.get('nazwisko')
    numer_pokoju = request.args.get('numer_pokoju')
    opis_usterki = request.args.get('opis_usterki')
    priorytet = request.args.get('priorytet')
    flash('notyfikacja zostala wyslana')
    if czas != 'dzien':
        priorytet = 'high'
        flash('zmieniono priorytet na wysoki')
    db = get_db()
    sql_command = 'insert into usterki (nr_pokoju, nazwisko , opis_usterki , priorytet ) values (?,?,?,?)'
    db.execute(sql_command, [numer_pokoju,nazwisko,opis_usterki, priorytet])
    db.commit()


    with open('data/dane.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([numer_pokoju, nazwisko,opis_usterki,priorytet])




    return render_template('wynik_opisu.html', active_menu = 'opis', nazwisko=nazwisko,
                           numer_pokoju=numer_pokoju, opis_usterki=opis_usterki, priorytet= priorytet)


@app.route('/opis_strony')
def opis_strony():
    return render_template("opis_strony.html", active_menu = 'opis_strony')


@app.route('/lista_usterek')
def lista():
    db = get_db()
    sql_command = 'select nr_pokoju, nazwisko, opis_usterki, priorytet from usterki;'
    cur = db.execute(sql_command)
    transaction = cur.fetchall()

    return render_template("lista_usterek.html",transaction = transaction, active_menu = 'lista')

# def lista():
#     with open('data/dane.csv', mode='r') as file:
#         reader = csv.reader(file)
#         data = list(reader)
#     return render_template("lista_usterek.html", active_menu = 'lista', data=data)
#
# a=''

if __name__ == '__main__':
    app.run(debug=True)